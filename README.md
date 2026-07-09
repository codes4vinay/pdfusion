# PDFusion

AI-powered PDF analyzer built with FastAPI, OpenAI GPT-4.1, MongoDB, and Redis/Valkey.

## What It Does

PDFusion accepts PDF uploads, stores job status in MongoDB, sends each file to a background RQ worker, converts PDF pages into images with Poppler/pdf2image/Pillow, and uses OpenAI GPT-4.1 to generate document analysis.

## Tech Stack

- Python 3.12
- FastAPI and Uvicorn
- OpenAI GPT-4.1
- MongoDB
- Redis/Valkey
- RQ background jobs
- pdf2image, Poppler, and Pillow
- Docker Compose

## Run Locally

You do not need to activate a virtual environment, install Python packages locally, or start the worker manually. Docker Compose starts everything.

From the project folder:

```powershell
docker compose up --build -d
```

This starts:

- FastAPI app
- RQ worker
- MongoDB
- Valkey/Redis

## Environment

Create or update `.env`:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

If the key is missing or still a placeholder, uploads will still be accepted and processed through the queue, but the final job status will be `failed` with `OPENAI_API_KEY is not configured`.

After changing `.env`, restart:

```powershell
docker compose up --build -d
```

## API

Health check:

```powershell
Invoke-RestMethod http://localhost:8000/
```

Upload a PDF:

```powershell
curl.exe -X POST http://localhost:8000/upload -F "file=@C:\path\to\file.pdf"
```

Response:

```json
{
  "file_id": "..."
}
```

Check processing status and result:

```powershell
Invoke-RestMethod http://localhost:8000/{file_id}
```

## Useful Commands

Show running services:

```powershell
docker compose ps
```

View logs:

```powershell
docker compose logs -f app
docker compose logs -f worker
```

Stop the app:

```powershell
docker compose down
```

Rebuild after code changes:

```powershell
docker compose up --build -d
```
