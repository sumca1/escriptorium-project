"""
Python wrapper for Passim text alignment service.

עוטף Python לשירות יישור הטקסט Passim.
מספק ממשק פשוט לתקשורת עם שירות הפלאסק ב-Docker.
"""

import requests
import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class AlignmentPairResult:
    """תוצאת זוג יישור בודד - Single alignment pair result"""
    text1: str
    text2: str
    index1: int
    index2: int
    similarity: float
    method: str
    metadata: Dict = None


@dataclass
class AlignmentResult:
    """תוצאות יישור מלאות - Complete alignment results"""
    doc1_id: str
    doc2_id: str
    pairs: List[AlignmentPairResult]
    statistics: Dict
    parameters: Dict
    timestamp: datetime = None


class PassimWrapper:
    """
    Wrapper class for communicating with Passim alignment service.
    
    מחלקה לתקשורת עם שירות יישור הטקסט Passim.
    """
    
    def __init__(
        self,
        service_url: str = "http://passim:9090",
        timeout: int = 300,  # 5 minutes default
        max_retries: int = 3
    ):
        """
        Initialize Passim wrapper.
        
        Args:
            service_url: URL of Passim service (default: http://passim:9090)
            timeout: Request timeout in seconds (default: 300)
            max_retries: Maximum number of retry attempts (default: 3)
        """
        self.service_url = service_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()
        
    def check_health(self) -> Tuple[bool, Dict]:
        """
        Check if Passim service is healthy and available.
        
        Returns:
            Tuple of (is_healthy: bool, health_data: dict)
            
        Example:
            >>> wrapper = PassimWrapper()
            >>> is_healthy, data = wrapper.check_health()
            >>> if is_healthy:
            ...     print(f"Service version: {data['version']}")
        """
        try:
            response = self.session.get(
                f"{self.service_url}/health",
                timeout=5  # Quick health check
            )
            response.raise_for_status()
            data = response.json()
            
            is_healthy = data.get('status') == 'healthy'
            logger.info(f"Passim health check: {data}")
            return is_healthy, data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Health check failed: {e}")
            return False, {"error": str(e)}
    
    def align_documents(
        self,
        doc1_lines: List[str],
        doc2_lines: List[str],
        method: str = "auto",
        threshold: float = 0.7,
        min_length: int = 10,
        doc1_id: Optional[str] = None,
        doc2_id: Optional[str] = None
    ) -> Optional[AlignmentResult]:
        """
        Align two documents line by line.
        
        יישר שני מסמכים שורה אחר שורה.
        
        Args:
            doc1_lines: List of lines from first document
            doc2_lines: List of lines from second document
            method: Alignment method ('auto', 'sequence', 'levenshtein', 'jaccard')
            threshold: Similarity threshold (0.0-1.0)
            min_length: Minimum line length to consider
            doc1_id: Optional ID for first document
            doc2_id: Optional ID for second document
            
        Returns:
            AlignmentResult object or None if failed
            
        Example:
            >>> wrapper = PassimWrapper()
            >>> doc1 = ["Hello world", "This is a test"]
            >>> doc2 = ["Hello world", "This is a test line"]
            >>> result = wrapper.align_documents(doc1, doc2)
            >>> print(f"Found {len(result.pairs)} aligned pairs")
            >>> print(f"Average similarity: {result.statistics['average_similarity']:.2%}")
        """
        payload = {
            "doc1_lines": doc1_lines,
            "doc2_lines": doc2_lines,
            "method": method,
            "threshold": threshold,
            "min_length": min_length
        }
        
        if doc1_id:
            payload["doc1_id"] = doc1_id
        if doc2_id:
            payload["doc2_id"] = doc2_id
        
        for attempt in range(self.max_retries):
            try:
                logger.info(
                    f"Aligning documents (attempt {attempt + 1}/{self.max_retries}): "
                    f"{len(doc1_lines)} vs {len(doc2_lines)} lines"
                )
                
                response = self.session.post(
                    f"{self.service_url}/align",
                    json=payload,
                    timeout=self.timeout
                )
                response.raise_for_status()
                data = response.json()
                
                # Convert response to AlignmentResult
                pairs = [
                    AlignmentPairResult(
                        text1=pair['text1'],
                        text2=pair['text2'],
                        index1=pair['index1'],
                        index2=pair['index2'],
                        similarity=pair['similarity'],
                        method=pair['method'],
                        metadata=pair.get('metadata', {})
                    )
                    for pair in data['pairs']
                ]
                
                result = AlignmentResult(
                    doc1_id=data.get('doc1_id', doc1_id or 'doc1'),
                    doc2_id=data.get('doc2_id', doc2_id or 'doc2'),
                    pairs=pairs,
                    statistics=data['statistics'],
                    parameters=data['parameters'],
                    timestamp=datetime.now()
                )
                
                logger.info(
                    f"Alignment successful: {len(pairs)} pairs, "
                    f"avg similarity: {data['statistics']['average_similarity']:.2%}"
                )
                return result
                
            except requests.exceptions.Timeout:
                logger.warning(f"Alignment timeout on attempt {attempt + 1}")
                if attempt == self.max_retries - 1:
                    logger.error("Max retries reached for alignment")
                    return None
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"Alignment request failed: {e}")
                if attempt == self.max_retries - 1:
                    return None
                    
            except (KeyError, ValueError) as e:
                logger.error(f"Invalid response format: {e}")
                return None
        
        return None
    
    def compare_texts(
        self,
        text1: str,
        text2: str,
        method: str = "auto"
    ) -> Optional[float]:
        """
        Compare two texts and return similarity score.
        
        השווה שני טקסטים והחזר ציון דמיון.
        
        Args:
            text1: First text to compare
            text2: Second text to compare
            method: Comparison method ('auto', 'sequence', 'levenshtein', 'jaccard')
            
        Returns:
            Similarity score (0.0-1.0) or None if failed
            
        Example:
            >>> wrapper = PassimWrapper()
            >>> score = wrapper.compare_texts("Hello world", "Hello there")
            >>> print(f"Similarity: {score:.2%}")
        """
        payload = {
            "text1": text1,
            "text2": text2,
            "method": method
        }
        
        try:
            response = self.session.post(
                f"{self.service_url}/compare",
                json=payload,
                timeout=10  # Quick comparison
            )
            response.raise_for_status()
            data = response.json()
            
            similarity = data.get('similarity')
            logger.debug(f"Text comparison: {similarity:.2%} similarity")
            return similarity
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Text comparison failed: {e}")
            return None
        except (KeyError, ValueError) as e:
            logger.error(f"Invalid comparison response: {e}")
            return None
    
    def batch_compare_texts(
        self,
        text_pairs: List[Tuple[str, str]],
        method: str = "auto"
    ) -> List[Optional[float]]:
        """
        Compare multiple text pairs in batch.
        
        השווה מספר זוגות טקסט במקבץ.
        
        Args:
            text_pairs: List of (text1, text2) tuples
            method: Comparison method
            
        Returns:
            List of similarity scores (None for failed comparisons)
        """
        results = []
        for text1, text2 in text_pairs:
            score = self.compare_texts(text1, text2, method)
            results.append(score)
        return results
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close session"""
        self.session.close()
        return False


# Convenience functions for quick usage
# פונקציות נוחות לשימוש מהיר

def quick_align(
    doc1_lines: List[str],
    doc2_lines: List[str],
    **kwargs
) -> Optional[AlignmentResult]:
    """Quick alignment without creating wrapper instance"""
    with PassimWrapper() as wrapper:
        return wrapper.align_documents(doc1_lines, doc2_lines, **kwargs)


def quick_compare(text1: str, text2: str, method: str = "auto") -> Optional[float]:
    """Quick text comparison without creating wrapper instance"""
    with PassimWrapper() as wrapper:
        return wrapper.compare_texts(text1, text2, method)


def is_service_available() -> bool:
    """Check if Passim service is available"""
    with PassimWrapper() as wrapper:
        is_healthy, _ = wrapper.check_health()
        return is_healthy
