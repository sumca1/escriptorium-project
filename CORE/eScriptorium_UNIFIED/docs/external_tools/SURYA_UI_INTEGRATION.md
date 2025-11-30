Surya OCR UI Integration - Quick Reference

Summary

This document lists the files created for Surya OCR integration, the REST API endpoints, the Vue component, Celery task, and quick usage notes.

Files created

- app/apps/api/views_surya_ocr.py   : REST API endpoints for Surya OCR
- app/apps/api/urls_surya_ocr.py    : URL router for the above endpoints
- app/apps/core/tasks_surya.py      : Celery tasks for background processing
- front/src/components/SuryaOCRPanel.vue : Vue component for the eScriptorium UI

Key REST endpoints

1) GET /api/ocr/engines/surya/
   - Returns engine metadata and status

2) POST /api/documents/{id}/ocr/surya/
   - Starts Surya OCR processing for document {id}
   - Payload: JSON with keys: language (e.g., "he"), force (boolean)
   - Response: 202 with task_id if processed asynchronously

3) GET /api/documents/{id}/ocr/surya/status/
   - Returns processing progress and basic stats

4) GET /api/documents/{id}/ocr/surya/results/
   - Returns created transcriptions for the document

Celery task

- process_document_with_surya_task
  - Located in app/apps/core/tasks_surya.py
  - Arguments: document_id, image_paths (list), force_reprocess (bool)
  - Returns: dict with pages_processed and lines_created

Vue component

- SuryaOCRPanel.vue
  - Props: documentId (number)
  - On mount: checks engine status and page info
  - On start: calls POST /api/documents/{id}/ocr/surya/ and polls status
  - Emits: 'results-ready' with results payload when done

Integration steps (quick)

1) Add the API urls to the project URL configuration so the endpoints are reachable under /api/.
2) Register the Vue component in your frontend and place it in the document editor template.
3) Configure Celery if you want background processing. If Celery is not available, the endpoints fall back to synchronous processing.
4) Ensure the Surya OCR engine can download its models. Note: models are hosted on models.datalab.to and require network access. If your environment blocks that domain, request approval with your firewall administrator.

Testing tips

- Use the engine info endpoint to confirm Surya is ready before starting a job.
- Start the job and poll the status endpoint for progress updates.
- If Celery is used, ensure a worker is running and the broker and result backend are configured.

NetFree / Firewall note

If you are behind a restrictive firewall, the Surya model downloader may be blocked. The models are typically downloaded from the domain models.datalab.to. Obtain permission to allow downloads from that domain to enable Surya to load models.

Contact

If you want, I can:
- Add the component into a specific template file you point to
- Wire the router automatically into your project urls
- Run a quick local test (if you enable model downloads or provide models locally)

Status

- Integration code created and wired in the repository
- Remaining: place the component into the specific template and run tests once models are available
- Blocker: model download requires network access (firewall) if not already allowed

