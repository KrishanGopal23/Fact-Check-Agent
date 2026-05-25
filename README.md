# Fact-Check Agent

Fact-Check Agent is a full-stack web application that audits factual claims in uploaded PDF
documents. It extracts checkable statements with Gemini, retrieves current web evidence with
Tavily, and presents evidence-linked verdicts and corrections in a polished React dashboard.

The application is designed for marketing reports, research summaries, generated content, and
business documents where stale statistics or unsupported assertions carry risk.

## Features

- Drag-and-drop PDF upload with validation and a 10 MB server-enforced limit.
- Page-aware text extraction using PyMuPDF.
- Structured claim detection for statistics, dates, money, science, and technical assertions.
- Concurrent Tavily retrieval for each extracted claim.
- Batched Gemini verification grounded only in retrieved evidence, with citations and corrections.
- Verdicts: `VERIFIED`, `INACCURATE`, `FALSE`, `MISLEADING`, `OUTDATED`, and
  `INSUFFICIENT_EVIDENCE`.
- Filterable, responsive report dashboard with JSON and CSV exports.
- Render Blueprint deployment for a React static site and FastAPI web service.

## Reliability Policy

Absence of a search result is not proof that a claim is false. The API returns
`INSUFFICIENT_EVIDENCE` when live sources cannot establish a defensible verdict. A claim is marked
`FALSE` when evidence contradicts it, and corrected facts are returned only when supported by the
retrieved sources.

PDF text is sent to Gemini for claim extraction. Retrieved snippets and claims are sent to Gemini
for one batched verification judgment. A normal analysis therefore uses two Gemini generations,
rather than one request per claim. Uploaded PDFs and API responses are served with `Cache-Control: no-store`; add
authentication and a formal retention policy before processing confidential documents.

## Architecture

```text
React + Vite + Tailwind UI
        |
        | multipart PDF upload
        v
FastAPI /fact-check
        |
        +--> PyMuPDF text extraction
        +--> Gemini structured claim extraction
        +--> Tavily live web retrieval (concurrent per claim)
        +--> Gemini evidence-bound verification
        +--> Deterministic summary report
```

## Project Layout

```text
.
|-- backend/
|   |-- app/
|   |   |-- core/config.py
|   |   |-- models/schemas.py
|   |   |-- routes/factcheck.py
|   |   `-- services/
|   |       |-- pdf_extractor.py
|   |       |-- claim_extractor.py
|   |       |-- tavily_search.py
|   |       |-- verifier.py
|   |       `-- report_generator.py
|   |-- tests/test_api.py
|   |-- requirements.txt
|   |-- requirements-dev.txt
|   `-- .env.example
|-- frontend/
|   |-- src/components/
|   |-- src/pages/Home.jsx
|   |-- src/services/api.js
|   |-- package.json
|   `-- .env.example
`-- render.yaml
```

## Required Accounts

1. Create a Gemini API key in [Google AI Studio](https://aistudio.google.com/app/apikey).
2. Create a Tavily API key in the [Tavily dashboard](https://app.tavily.com/).
3. Create a Render account and connect the Git repository for deployment.

## Run Locally

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
```

Set real keys in `backend/.env`, then start the API:

```bash
uvicorn app.main:app --reload --port 8000
```

API documentation is available at `http://localhost:8000/docs`.

### Frontend

In a second terminal:

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Open `http://localhost:5173`.

## Environment Variables

Backend variables:

| Variable | Required | Purpose |
| --- | --- | --- |
| `GEMINI_API_KEY` | Yes | Gemini model authentication. |
| `TAVILY_API_KEY` | Yes | Live evidence retrieval authentication. |
| `GEMINI_MODEL` | No | Defaults to `gemini-2.5-flash`. |
| `FRONTEND_ORIGINS` | No | Comma-separated CORS origins. |
| `MAX_UPLOAD_MB` | No | Upload limit, default `10`. |
| `MAX_CLAIMS` | No | Maximum claims audited per run, default `18`. |
| `VERIFICATION_CONCURRENCY` | No | Concurrent Tavily retrieval tasks, default `4`. |

Frontend variable:

| Variable | Required | Purpose |
| --- | --- | --- |
| `VITE_API_BASE_URL` | Yes in production | Public FastAPI service URL. |

## API Routes

| Method | Route | Description |
| --- | --- | --- |
| `GET` | `/health` | Health and API-key configuration readiness. |
| `POST` | `/upload` | Validate a PDF and preview extracted text. |
| `POST` | `/extract` | Extract structured claims from a PDF. |
| `POST` | `/verify` | Verify supplied structured claims against live evidence. |
| `POST` | `/fact-check` | Upload-to-report end-to-end pipeline used by the frontend. |

For PDF routes, submit multipart form data with a `file` field. `/verify` accepts JSON matching
the schema exposed in Swagger documentation.

## Deploy To Render

The repository includes [`render.yaml`](./render.yaml), which creates:

- `fact-check-agent-api`: a Python FastAPI web service.
- `fact-check-agent-web`: a React static site built by Vite.

Deployment steps:

1. Push this repository to GitHub or GitLab.
2. In Render, choose **New > Blueprint** and select the repository.
3. During Blueprint creation, enter secret values for `GEMINI_API_KEY` and `TAVILY_API_KEY`.
4. Confirm the generated service URLs. The blueprint assumes
   `https://fact-check-agent-api.onrender.com` and
   `https://fact-check-agent-web.onrender.com`.
5. If Render assigns different URLs, update `VITE_API_BASE_URL` on the static site and
   `FRONTEND_ORIGINS` on the API service, then redeploy the frontend.
6. Visit the web service URL, upload a PDF, and verify that each claim displays live evidence.

The frontend is a static app; the backend keys remain only on the FastAPI service and are never
exposed in browser JavaScript.

## Validation

```bash
cd backend
pytest

cd ../frontend
npm run lint
npm run build
```

Live end-to-end verification additionally requires valid Gemini and Tavily credentials.

## Screenshots

Add deployment screenshots here after the Render URL is provisioned:

- Landing and upload dashboard
- Processing state
- Evidence-linked fact-check report

## Further Improvements

- OCR for scanned/image-only PDFs.
- Highlight annotations embedded into an exported marked-up PDF.
- Authentication, usage quotas, and encrypted report persistence.
- Domain-specific authoritative source allowlists and evaluation fixtures.
- Server-sent progress events for claim-by-claim streaming updates.

## Integration References

- [Gemini structured outputs](https://ai.google.dev/gemini-api/docs/structured-output)
- [Tavily Python SDK](https://docs.tavily.com/sdk/python/reference)
- [Tailwind CSS with Vite](https://tailwindcss.com/docs/installation/using-vite)
- [Render Blueprint YAML reference](https://render.com/docs/blueprint-spec)
