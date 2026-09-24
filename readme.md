
## Overview

A production-shaped REST API for text analysis which includes logs and system observability. Submit text via a `POST` request, select which analyses to run, and receive structured JSON results.

## Quickstart

**Prerequisites:** Docker Compose (desktop). 

```bash
docker compose up -d
```

Once the containers are up:
- **API:** http://localhost:8000
- **OpenAPI docs:** http://localhost:8000/docs
- **Prometheus:** http://localhost:9090
- **Grafana:** http://localhost:3000
- **PostgreSQL:** `localhost:5432`

### Available Analysis

- word_count: Count of whitespace-separated words.
- character_count: Count of characters, optionally excluding spaces (default is set to true).
- sentence_count: Count of sentences using nltk library.

### Example Queries

```bash
curl -X POST "http://localhost:8000/analyse?analyses=word_count&analyses=sentence_count" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world. Dr. Smith went to the USA yesterday."}'
```

Expected response:

```json
{
  "results": {
    "word_count": 9,
    "sentence_count": 2
  },
  "metadata": {
    "request_id": "b3a7f2e1-...",
    "input_length": 52,
    "processing_time_ms": 1.42
  }
}
```

## API reference

| Method | Path              | Purpose                              |
|--------|-------------------|--------------------------------------|
| `POST` | `/analyse`        | Run selected analyses on input text  |
| `GET`  | `/analysers`      | List registered analysers            |
| `GET`  | `/health`         | Liveness probe                       |
| `GET`  | `/metrics`        | Prometheus metrics                   |
| `GET`  | `/docs`           | Interactive OpenAPI UI               |


## Database audit logging

Every API request is stored in the PostgreSQL `audit_logs` table. Each row contains the request ID, HTTP method, path, query parameters, request body, response body, status code, client IP, and timestamp. Existing structured console logs remain enabled.

Inspect recent audit records:

```bash
docker compose exec postgres \
  psql -U string_analysis_user -d string_analysis_db \
  -c "SELECT * FROM audit_logs ORDER BY id DESC LIMIT 10;"
```

### Connect with DataGrip

```text
Host: localhost
Port: 5432
Database: string_analysis_db
User: [your-password]
Password: [your-password]
```

JDBC URL:

```text
jdbc:postgresql://yout-host:[port1234]/string_analysis_db
```


### `POST /analyse`

**Query parameters**

| Name             | Type              | Required | Description                                       |
|------------------|-------------------|----------|---------------------------------------------------|
| `analyses`       | repeated string   | yes      | One or more analyser names to run                 |
| `include_spaces` | boolean           | no       | Passed to `character_count` (default `true`)      |


### Adding a new analyser

1. Create a class in `backend/src/backend/core/analysers/` inheriting from `BaseAnalyser`, setting `name` and implementing `analyse()`.
2. Add the class to `_DEFAULT_ANALYSERS` in `backend/src/backend/core/registry.py`.
3. Add the name to the `AnalysisType` enum in `backend/src/backend/schema/analysis_schema.py`.

No changes to the API layer, the registry itself, or error handling are needed.


## Testing

Twelve integration tests cover analysis behavior, validation failures, metrics, and audit persistence.

```bash
uv run pytest
```

## Deployed Backend: 

GitHub Actions runs two workflows:

- **`test.yml`** — runs on every pull request. Installs dependencies via `uv`and runs the pytest suite.
- **`build-and-push.yml`** — Invokes `test.yml` and then builds the backend image and pushes to GitHub Container Registry 

https://github.com/CodeByKarthik?tab=packages

Pull the published image:

```bash
docker pull ghcr.io/codebykarthik/string-analysis-backend:latest
```

---

## Author

Karthikeyan Sivakumar 