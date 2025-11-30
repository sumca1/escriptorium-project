# CERberus API Reference

**Base URL**: `http://localhost:8082/api/cerberus/`  
**Authentication**: Token-based (Django REST Framework)  
**Version**: 1.0  
**Date**: October 26, 2024

---

## Authentication

All endpoints require authentication using a token in the header:

```bash
Authorization: Token YOUR_TOKEN_HERE
```

To get a token:
```bash
docker-compose exec web python manage.py drf_create_token USERNAME
```

---

## Endpoints

### 1. Create CER Analysis

**Endpoint**: `POST /api/cerberus/analyses/`

**Description**: Create a new Character Error Rate analysis comparing two transcriptions.

**Request Body**:
```json
{
  "ground_truth_transcription_id": 33,
  "hypothesis_transcription_id": 1,
  "ignore_case": false,
  "ignore_punctuation": false,
  "ignore_whitespace": false,
  "ignore_numbers": false,
  "ignore_newlines": false,
  "ignore_chars": "",
  "analyze_unicode_blocks": true
}
```

**Parameters**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `ground_truth_transcription_id` | integer | ✅ Yes | ID of the ground truth transcription |
| `hypothesis_transcription_id` | integer | ✅ Yes | ID of the hypothesis transcription to compare |
| `ignore_case` | boolean | ❌ No (default: false) | Ignore letter case differences |
| `ignore_punctuation` | boolean | ❌ No (default: false) | Ignore punctuation marks |
| `ignore_whitespace` | boolean | ❌ No (default: false) | Ignore spaces and tabs |
| `ignore_numbers` | boolean | ❌ No (default: false) | Ignore numeric digits |
| `ignore_newlines` | boolean | ❌ No (default: false) | Ignore line breaks |
| `ignore_chars` | string | ❌ No (default: "") | Additional characters to ignore (comma-separated) |
| `analyze_unicode_blocks` | boolean | ❌ No (default: true) | Analyze by Unicode blocks (Hebrew, Arabic, etc.) |

**Response** (201 CREATED):
```json
{
  "id": 1,
  "ground_truth_transcription": 33,
  "hypothesis_transcription": 1,
  "cer_value": 18.75,
  "accuracy": 81.25,
  "num_correct": 13,
  "num_substitutions": 2,
  "num_insertions": 1,
  "num_deletions": 0,
  "total_characters": 16,
  "character_statistics": [
    {
      "character": "א",
      "count": 120,
      "correct": 110,
      "incorrect": 10,
      "correct_ratio": 0.9167,
      "incorrect_ratio": 0.0833
    }
  ],
  "block_statistics": [
    {
      "block": "Hebrew",
      "count": 14,
      "correct": 12,
      "incorrect": 2,
      "correct_ratio": 0.8571,
      "incorrect_ratio": 0.1429
    }
  ],
  "confusion_statistics": [
    {
      "correct_character": "ה",
      "generated_character": "ח",
      "count": 3,
      "ratio": 0.15
    }
  ],
  "error_breakdown": {
    "substitutions": 12.5,
    "insertions": 6.25,
    "deletions": 0.0
  },
  "created_at": "2024-10-26T14:30:00Z",
  "updated_at": "2024-10-26T14:30:00Z"
}
```

**cURL Example**:
```bash
curl -X POST http://localhost:8082/api/cerberus/analyses/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "ground_truth_transcription_id": 33,
    "hypothesis_transcription_id": 1,
    "ignore_case": false,
    "analyze_unicode_blocks": true
  }'
```

---

### 2. List All Analyses

**Endpoint**: `GET /api/cerberus/analyses/`

**Description**: Retrieve a paginated list of all CER analyses.

**Query Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `page` | integer | Page number (default: 1) |
| `page_size` | integer | Results per page (default: 20, max: 100) |

**Response** (200 OK):
```json
{
  "count": 42,
  "next": "http://localhost:8082/api/cerberus/analyses/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "cer_value": 18.75,
      "accuracy": 81.25,
      "total_characters": 16,
      "created_at": "2024-10-26T14:30:00Z"
    }
  ]
}
```

**cURL Example**:
```bash
curl -X GET "http://localhost:8082/api/cerberus/analyses/?page=1&page_size=10" \
  -H "Authorization: Token YOUR_TOKEN"
```

---

### 3. Get Analysis Details

**Endpoint**: `GET /api/cerberus/analyses/{id}/`

**Description**: Retrieve detailed information about a specific CER analysis.

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | integer | Analysis ID |

**Response** (200 OK):
```json
{
  "id": 1,
  "ground_truth_transcription": 33,
  "hypothesis_transcription": 1,
  "cer_value": 18.75,
  "accuracy": 81.25,
  "num_correct": 13,
  "num_substitutions": 2,
  "num_insertions": 1,
  "num_deletions": 0,
  "total_characters": 16,
  "ignore_case": false,
  "ignore_punctuation": false,
  "ignore_whitespace": false,
  "character_statistics": [...],
  "block_statistics": [...],
  "confusion_statistics": [...],
  "error_breakdown": {...},
  "created_at": "2024-10-26T14:30:00Z"
}
```

**cURL Example**:
```bash
curl -X GET http://localhost:8082/api/cerberus/analyses/1/ \
  -H "Authorization: Token YOUR_TOKEN"
```

---

### 4. Get Confusion Matrix

**Endpoint**: `GET /api/cerberus/analyses/{id}/confusion_matrix/`

**Description**: Retrieve the top character confusions for an analysis.

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | integer | Analysis ID |

**Query Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | integer | 20 | Number of top confusions to return |

**Response** (200 OK):
```json
{
  "analysis_id": 1,
  "limit": 20,
  "confusions": [
    {
      "correct_character": "ה",
      "generated_character": "ח",
      "count": 15,
      "ratio": 0.25
    },
    {
      "correct_character": "כ",
      "generated_character": "ב",
      "count": 8,
      "ratio": 0.13
    }
  ]
}
```

**cURL Example**:
```bash
curl -X GET "http://localhost:8082/api/cerberus/analyses/1/confusion_matrix/?limit=10" \
  -H "Authorization: Token YOUR_TOKEN"
```

---

### 5. Get Problematic Characters

**Endpoint**: `GET /api/cerberus/analyses/{id}/problematic_characters/`

**Description**: Retrieve characters with accuracy below a threshold.

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | integer | Analysis ID |

**Query Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `threshold` | float | 0.5 | Accuracy threshold (0.0 - 1.0) |

**Response** (200 OK):
```json
{
  "analysis_id": 1,
  "threshold": 0.5,
  "problematic_characters": [
    {
      "character": "ץ",
      "count": 120,
      "correct": 45,
      "incorrect": 75,
      "correct_ratio": 0.375,
      "incorrect_ratio": 0.625
    },
    {
      "character": "ף",
      "count": 80,
      "correct": 30,
      "incorrect": 50,
      "correct_ratio": 0.375,
      "incorrect_ratio": 0.625
    }
  ]
}
```

**cURL Example**:
```bash
curl -X GET "http://localhost:8082/api/cerberus/analyses/1/problematic_characters/?threshold=0.8" \
  -H "Authorization: Token YOUR_TOKEN"
```

---

### 6. Export Analysis

**Endpoint**: `GET /api/cerberus/analyses/{id}/export/`

**Description**: Export analysis data in JSON or CSV format.

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | integer | Analysis ID |

**Query Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `format` | string | ✅ Yes | Export format: `json` or `csv` |
| `data_type` | string | ❌ No (CSV only) | Data type for CSV: `character`, `block`, or `confusion` |

**JSON Export**:
```bash
curl -X GET "http://localhost:8082/api/cerberus/analyses/1/export/?format=json" \
  -H "Authorization: Token YOUR_TOKEN" \
  -o analysis_1.json
```

**Response** (200 OK):
- Content-Type: `application/json`
- Content-Disposition: `attachment; filename="cer_analysis_1.json"`

**CSV Export**:
```bash
curl -X GET "http://localhost:8082/api/cerberus/analyses/1/export/?format=csv&data_type=confusion" \
  -H "Authorization: Token YOUR_TOKEN" \
  -o confusions_1.csv
```

**Response** (200 OK):
- Content-Type: `text/csv; charset=utf-8-sig`
- Content-Disposition: `attachment; filename="cer_analysis_1_confusion.csv"`
- UTF-8 BOM included for Excel compatibility ✅

**CSV Data Types**:
- `character` - Character-level statistics (character, count, correct, incorrect, ratios)
- `block` - Unicode block statistics (block name, count, correct, incorrect, ratios)
- `confusion` - Confusion matrix (correct char, generated char, count, ratio)

---

### 7. Update Analysis

**Endpoint**: `PUT /api/cerberus/analyses/{id}/` or `PATCH /api/cerberus/analyses/{id}/`

**Description**: Update analysis metadata (NOT recommended - create new analysis instead).

**Note**: ⚠️ Analysis results are computed on creation and should not be modified. This endpoint is provided for metadata updates only.

---

### 8. Delete Analysis

**Endpoint**: `DELETE /api/cerberus/analyses/{id}/`

**Description**: Delete a CER analysis.

**Response** (204 NO CONTENT)

**cURL Example**:
```bash
curl -X DELETE http://localhost:8082/api/cerberus/analyses/1/ \
  -H "Authorization: Token YOUR_TOKEN"
```

---

## Error Responses

### 400 Bad Request
**Description**: Invalid input parameters.

```json
{
  "ground_truth_transcription_id": [
    "This field is required."
  ]
}
```

### 401 Unauthorized
**Description**: Missing or invalid authentication token.

```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 404 Not Found
**Description**: Analysis or transcription not found.

```json
{
  "detail": "Not found."
}
```

### 500 Internal Server Error
**Description**: Server error during CER calculation.

```json
{
  "detail": "An error occurred during CER analysis."
}
```

---

## Data Models

### CERAnalysis Object

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Unique analysis ID |
| `ground_truth_transcription` | integer | Ground truth transcription ID |
| `hypothesis_transcription` | integer | Hypothesis transcription ID |
| `cer_value` | float | Character Error Rate (0.0 - 100.0) |
| `accuracy` | float | Character accuracy (0.0 - 100.0) |
| `num_correct` | integer | Number of correct characters |
| `num_substitutions` | integer | Number of character substitutions |
| `num_insertions` | integer | Number of character insertions |
| `num_deletions` | integer | Number of character deletions |
| `total_characters` | integer | Total characters in ground truth |
| `ignore_case` | boolean | Case-insensitive analysis |
| `ignore_punctuation` | boolean | Punctuation ignored |
| `ignore_whitespace` | boolean | Whitespace ignored |
| `ignore_numbers` | boolean | Numbers ignored |
| `ignore_newlines` | boolean | Newlines ignored |
| `ignore_chars` | string | Custom ignored characters |
| `character_statistics` | array | Per-character statistics |
| `block_statistics` | array | Unicode block statistics |
| `confusion_statistics` | array | Character confusion matrix |
| `error_breakdown` | object | Error type percentages |
| `created_at` | datetime | Creation timestamp |
| `updated_at` | datetime | Last update timestamp |

### Character Statistics Object

```json
{
  "character": "א",
  "count": 120,
  "correct": 110,
  "incorrect": 10,
  "correct_ratio": 0.9167,
  "incorrect_ratio": 0.0833
}
```

### Block Statistics Object

```json
{
  "block": "Hebrew",
  "count": 500,
  "correct": 450,
  "incorrect": 50,
  "correct_ratio": 0.9,
  "incorrect_ratio": 0.1
}
```

### Confusion Statistics Object

```json
{
  "correct_character": "ה",
  "generated_character": "ח",
  "count": 15,
  "ratio": 0.25
}
```

---

## Python Client Example

```python
import requests

# Configuration
BASE_URL = "http://localhost:8082/api/cerberus"
TOKEN = "your_token_here"
HEADERS = {
    "Authorization": f"Token {TOKEN}",
    "Content-Type": "application/json"
}

# Create analysis
response = requests.post(
    f"{BASE_URL}/analyses/",
    headers=HEADERS,
    json={
        "ground_truth_transcription_id": 33,
        "hypothesis_transcription_id": 1,
        "ignore_case": False,
        "analyze_unicode_blocks": True
    }
)
analysis = response.json()
print(f"CER: {analysis['cer_value']}%")

# Get confusion matrix
response = requests.get(
    f"{BASE_URL}/analyses/{analysis['id']}/confusion_matrix/",
    headers=HEADERS,
    params={"limit": 10}
)
confusions = response.json()
for conf in confusions['confusions']:
    print(f"{conf['correct_character']} → {conf['generated_character']}: {conf['count']} times")

# Export to CSV
response = requests.get(
    f"{BASE_URL}/analyses/{analysis['id']}/export/",
    headers=HEADERS,
    params={"format": "csv", "data_type": "confusion"}
)
with open("confusions.csv", "wb") as f:
    f.write(response.content)
```

---

## JavaScript Client Example

```javascript
const BASE_URL = 'http://localhost:8082/api/cerberus';
const TOKEN = 'your_token_here';

// Create analysis
const createAnalysis = async (groundTruthId, hypothesisId) => {
  const response = await fetch(`${BASE_URL}/analyses/`, {
    method: 'POST',
    headers: {
      'Authorization': `Token ${TOKEN}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      ground_truth_transcription_id: groundTruthId,
      hypothesis_transcription_id: hypothesisId,
      ignore_case: false,
      analyze_unicode_blocks: true
    })
  });
  return await response.json();
};

// Get confusion matrix
const getConfusions = async (analysisId, limit = 20) => {
  const response = await fetch(
    `${BASE_URL}/analyses/${analysisId}/confusion_matrix/?limit=${limit}`,
    {
      headers: { 'Authorization': `Token ${TOKEN}` }
    }
  );
  return await response.json();
};

// Usage
(async () => {
  const analysis = await createAnalysis(33, 1);
  console.log(`CER: ${analysis.cer_value}%`);
  
  const confusions = await getConfusions(analysis.id, 10);
  confusions.confusions.forEach(conf => {
    console.log(`${conf.correct_character} → ${conf.generated_character}: ${conf.count} times`);
  });
})();
```

---

## Rate Limiting

Currently, there is no rate limiting on the API. For production deployments, consider implementing rate limiting using:
- Django REST Framework throttling
- Nginx rate limiting
- API Gateway

---

## Changelog

### Version 1.0 (October 26, 2024)
- Initial release
- 8 REST endpoints
- Support for Hebrew and Arabic Unicode blocks
- JSON and CSV export formats
- Comprehensive error handling

---

## Support

For issues or questions:
1. Check Django admin: http://localhost:8082/admin/cerberus_integration/ceranalysis/
2. Run tests: `docker-compose exec web python manage.py test_cerberus_api`
3. View logs: `docker-compose logs web --tail=100`

---

**Last Updated**: October 26, 2024  
**API Version**: 1.0  
**eScriptorium**: Custom BiblIA Integration
