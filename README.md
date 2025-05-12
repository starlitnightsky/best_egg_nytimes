# NY Times Article Microservice

A lightweight, async FastAPI service that wraps two NY Times endpoints:

- **Top Stories** – returns the two newest articles from each configured section
- **Article Search** – full‑text search with optional date filters

## Quick‑Start

```bash
git clone https://github.com/<you>/nyt-microservice.git
cd nyt-microservice
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

- create local .env with your key

uvicorn app.main:app --reload  # http://127.0.0.1:8000/docs
```
