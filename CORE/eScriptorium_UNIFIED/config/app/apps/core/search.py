import re
from urllib.parse import unquote_plus

from django.conf import settings
from django.contrib.postgres.search import SearchHeadline, SearchQuery
from django.db.models import CharField, F, Func, Value
from elasticsearch import Elasticsearch

EXTRACT_EXACT_TERMS_REGEXP = '"[^"]+"'
WORD_BY_WORD_SEARCH_MODE = "word-by-word"
REGEX_SEARCH_MODE = "regex"


def search_content_es(current_page, page_size, user_id, terms, projects=None, documents=None, transcriptions=None):
    es_client = Elasticsearch(hosts=[settings.ELASTICSEARCH_URL])

    cleaned_terms = re.escape(terms)
    exact_matches = re.findall(EXTRACT_EXACT_TERMS_REGEXP, cleaned_terms)
    # Removing the quotation marks around exact terms
    terms_exact = [m[1:-1] for m in exact_matches]
    if terms_exact:
        terms_fuzzy = re.split(EXTRACT_EXACT_TERMS_REGEXP, cleaned_terms)
    else:
        terms_fuzzy = [terms]

    body = {
        "from": (current_page - 1) * page_size,
        "size": page_size,
        "sort": ["_score"],
        "query": {
            "bool": {
                "must": [
                    {"term": {"have_access": user_id}},
                    # Prevent from loading results from archived documents
                    {"term": {"document_archived": False}},
                ] + [
                    {"multi_match": {
                        "query": unquote_plus(term),
                        "fuzziness": "AUTO",
                        "fields": ["raw_content^3", "context"]
                    }}
                    for term in terms_fuzzy if term.strip() != ""
                ] + [
                    {"multi_match": {
                        "query": unquote_plus(term),
                        "type": "phrase",
                        "fields": ["raw_content^3", "context"]
                    }}
                    for term in terms_exact if term.strip() != ""
                ]
            }
        },
        "highlight": {
            "require_field_match": False,
            "pre_tags": ['<strong class="text-success">'],
            "post_tags": ["</strong>"],
            "fields": {
                "raw_content": {},
                "context_before": {},
                "context_after": {}
            },
        }
    }

    if projects:
        body["query"]["bool"]["must"].append({"terms": {"project_id": projects}})

    if documents:
        body["query"]["bool"]["must"].append({"terms": {"document_id": documents}})

    if transcriptions:
        body["query"]["bool"]["must"].append({"terms": {"transcription_id": transcriptions}})

    return es_client.search(index=settings.ELASTICSEARCH_COMMON_INDEX, body=body)


def get_filtered_queryset(user, project_id, document_id, transcription_id, part_id):
    from core.models import Document, LineTranscription, Project

    right_filters = {
        "line__document_part__document__project_id__in": Project.objects.for_user_read(user),
        "line__document_part__document_id__in": Document.objects.for_user(user),
    }

    filters = {}
    if project_id:
        filters["line__document_part__document__project_id"] = project_id

    if document_id:
        filters["line__document_part__document_id"] = document_id

    if transcription_id:
        filters["transcription_id"] = transcription_id

    if part_id:
        filters["line__document_part_id"] = part_id

    return LineTranscription.objects.select_related(
        "transcription",
        "line",
        "line__document_part",
        "line__document_part__document",
    ).filter(**right_filters, **filters)


def search_content_psql_word(terms, user, highlight_class, project_id=None, document_id=None, transcription_id=None, part_id=None):
    search_query = SearchQuery(terms)
    return (
        get_filtered_queryset(user, project_id, document_id, transcription_id, part_id)
        .filter(content__search=search_query)
        .annotate(
            highlighted_content=SearchHeadline(
                "content",
                search_query,
                start_sel=f'<strong class="{highlight_class}">',
                stop_sel="</strong>",
            )
        )
    )


def search_content_psql_regex(terms, user, highlight_class, project_id=None, document_id=None, transcription_id=None, part_id=None):
    return (
        get_filtered_queryset(user, project_id, document_id, transcription_id, part_id)
        .filter(content__regex=terms)
        .annotate(
            highlighted_content=Func(
                F("content"),
                Value(r"(%s)" % terms),
                Value(r'<strong class="%s">\1</strong>' % highlight_class),
                Value("g"),
                function="REGEXP_REPLACE",
                output_field=CharField(),
            )
        )
    )


def build_highlighted_replacement_psql(mode, find_terms, replace_term, highlighted_content):
    if not replace_term:
        return None

    extra = {}
    if mode == WORD_BY_WORD_SEARCH_MODE:
        replace_term = replace_term.replace('\\', r'\\')
        extra = {"flags": re.IGNORECASE}

    return re.sub(r'<strong class="text-danger">%s</strong>' % find_terms, r'<strong class="text-success">%s</strong>' % replace_term, highlighted_content, **extra)


# ============================================================================
# 🆕 Enhanced Elasticsearch Service for BiblIA
# Created: 20 אוקטובר 2025
# ============================================================================

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from elasticsearch import exceptions as es_exceptions

logger = logging.getLogger(__name__)


class ElasticsearchService:
    """
    שירות חיפוש Elasticsearch משופר
    מנהל אינדוקס וחיפוש של תמלולי OCR
    """
    
    def __init__(self):
        """אתחול חיבור ל-Elasticsearch"""
        self.enabled = not settings.DISABLE_ELASTICSEARCH
        self.es = None
        self.index_name = settings.ELASTICSEARCH_COMMON_INDEX
        
        if self.enabled:
            try:
                self.es = Elasticsearch(
                    [settings.ELASTICSEARCH_URL],
                    timeout=30,
                    max_retries=3,
                    retry_on_timeout=True
                )
                # בדוק חיבור
                if self.es.ping():
                    logger.info(f"✅ Elasticsearch connected: {settings.ELASTICSEARCH_URL}")
                    self._ensure_index_exists()
                else:
                    logger.error("❌ Elasticsearch ping failed")
                    self.enabled = False
            except Exception as e:
                logger.error(f"❌ Elasticsearch connection error: {e}")
                self.enabled = False
        else:
            logger.warning("⚠️ Elasticsearch is disabled in settings")
    
    def _ensure_index_exists(self):
        """וודא שה-index קיים, אם לא - צור אותו"""
        try:
            if not self.es.indices.exists(index=self.index_name):
                # הגדרות index עם mappings מותאמים לעברית וערבית
                index_settings = {
                    "settings": {
                        "number_of_shards": 1,
                        "number_of_replicas": 0,
                        "analysis": {
                            "analyzer": {
                                "hebrew_analyzer": {
                                    "type": "custom",
                                    "tokenizer": "standard",
                                    "filter": ["lowercase"]
                                },
                                "arabic_analyzer": {
                                    "type": "arabic"
                                }
                            }
                        }
                    },
                    "mappings": {
                        "properties": {
                            "content": {
                                "type": "text",
                                "analyzer": "hebrew_analyzer",
                                "fields": {
                                    "raw": {"type": "keyword"},
                                    "arabic": {
                                        "type": "text",
                                        "analyzer": "arabic_analyzer"
                                    }
                                }
                            },
                            "document_id": {"type": "integer"},
                            "document_name": {
                                "type": "text",
                                "fields": {"keyword": {"type": "keyword"}}
                            },
                            "document_part_id": {"type": "integer"},
                            "transcription_id": {"type": "integer"},
                            "transcription_name": {"type": "keyword"},
                            "line_id": {"type": "integer"},
                            "line_order": {"type": "integer"},
                            "confidence": {"type": "float"},
                            "project_id": {"type": "integer"},
                            "project_name": {
                                "type": "text",
                                "fields": {"keyword": {"type": "keyword"}}
                            },
                            "created": {"type": "date"},
                            "updated": {"type": "date"}
                        }
                    }
                }
                
                self.es.indices.create(index=self.index_name, body=index_settings)
                logger.info(f"✅ Created Elasticsearch index: {self.index_name}")
        except Exception as e:
            logger.error(f"❌ Error creating index: {e}")
    
    def index_transcription(self, line_transcription) -> bool:
        """
        אינדקס תמלול בודד
        
        Args:
            line_transcription: LineTranscription model instance
            
        Returns:
            bool: הצלחה/כישלון
        """
        if not self.enabled or not self.es:
            return False
        
        try:
            # שלוף נתונים רלוונטיים
            line = line_transcription.line
            document_part = line.document_part
            document = document_part.document
            transcription = line_transcription.transcription
            
            # בנה document ל-ES
            doc = {
                "content": line_transcription.content or "",
                "document_id": document.id,
                "document_name": document.name,
                "document_part_id": document_part.id,
                "transcription_id": transcription.id,
                "transcription_name": transcription.name,
                "line_id": line.id,
                "line_order": line.order,
                "confidence": getattr(line_transcription, 'avg_confidence', None),
                "created": line_transcription.created.isoformat() if hasattr(line_transcription, 'created') else datetime.now().isoformat(),
                "updated": line_transcription.updated.isoformat() if hasattr(line_transcription, 'updated') else datetime.now().isoformat(),
                "project_id": document.project.id if document.project else None,
                "project_name": document.project.name if document.project else None,
            }
            
            # שלח ל-ES
            self.es.index(
                index=self.index_name,
                id=f"line_{line_transcription.id}",
                body=doc
            )
            
            logger.debug(f"✅ Indexed transcription {line_transcription.id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error indexing transcription {line_transcription.id}: {e}")
            return False
    
    def delete_transcription(self, line_transcription_id: int) -> bool:
        """מחק תמלול מה-index"""
        if not self.enabled or not self.es:
            return False
        
        try:
            self.es.delete(
                index=self.index_name,
                id=f"line_{line_transcription_id}",
                ignore=[404]
            )
            logger.debug(f"✅ Deleted transcription {line_transcription_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Error deleting: {e}")
            return False
    
    def search_advanced(
        self,
        query: str,
        document_id: Optional[int] = None,
        project_id: Optional[int] = None,
        min_confidence: Optional[float] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """
        חיפוש מתקדם עם סינונים
        """
        if not self.enabled or not self.es:
            return {
                "total": 0,
                "results": [],
                "error": "Elasticsearch is not enabled"
            }
        
        try:
            must_clauses = []
            filter_clauses = []
            
            # חיפוש טקסט
            if query:
                must_clauses.append({
                    "multi_match": {
                        "query": query,
                        "fields": ["content^3", "document_name^2", "project_name"],
                        "fuzziness": "AUTO"
                    }
                })
            
            # סינונים
            if document_id:
                filter_clauses.append({"term": {"document_id": document_id}})
            if project_id:
                filter_clauses.append({"term": {"project_id": project_id}})
            if min_confidence:
                filter_clauses.append({"range": {"confidence": {"gte": min_confidence}}})
            
            search_body = {
                "query": {
                    "bool": {
                        "must": must_clauses if must_clauses else [{"match_all": {}}],
                        "filter": filter_clauses
                    }
                },
                "highlight": {
                    "fields": {
                        "content": {
                            "pre_tags": ["<mark>"],
                            "post_tags": ["</mark>"]
                        }
                    }
                },
                "from": (page - 1) * page_size,
                "size": page_size
            }
            
            response = self.es.search(index=self.index_name, body=search_body)
            
            results = []
            for hit in response['hits']['hits']:
                results.append({
                    "id": hit['_id'],
                    "score": hit['_score'],
                    "content": hit['_source']['content'],
                    "document_name": hit['_source']['document_name'],
                    "highlight": hit.get('highlight', {}).get('content', [])
                })
            
            return {
                "total": response['hits']['total']['value'],
                "results": results,
                "page": page,
                "page_size": page_size
            }
            
        except Exception as e:
            logger.error(f"❌ Search error: {e}")
            return {"total": 0, "results": [], "error": str(e)}
    
    def get_stats(self) -> Dict[str, Any]:
        """קבל סטטיסטיקות על ה-index"""
        if not self.enabled or not self.es:
            return {"enabled": False}
        
        try:
            count = self.es.count(index=self.index_name)
            stats = self.es.indices.stats(index=self.index_name)
            
            return {
                "enabled": True,
                "total_documents": count['count'],
                "size_mb": round(stats['indices'][self.index_name]['total']['store']['size_in_bytes'] / 1024 / 1024, 2)
            }
        except Exception as e:
            return {"enabled": True, "error": str(e)}


# Singleton instance
_es_service = None

def get_es_service() -> ElasticsearchService:
    """קבל instance יחיד של ElasticsearchService"""
    global _es_service
    if _es_service is None:
        _es_service = ElasticsearchService()
    return _es_service
