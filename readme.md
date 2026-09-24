
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


### `POST /analyse`

**Query parameters**

| Name             | Type              | Required | Description                                       |
|------------------|-------------------|----------|---------------------------------------------------|
| `analyses`       | repeated string   | yes      | One or more analyser names to run                 |
| `include_spaces` | boolean           | no       | Passed to `character_count` (default `true`)      |


### Adding a new analyser

1. Create a class in `backend/analysers/` inheriting from `BaseAnalyser`, setting `name` and implementing `analyse()`.
2. Add the class to `_DEFAULT_ANALYSERS` in `registry.py`.
3. Add the name to the `AnalysisType` enum in `schemas.py`.

No changes to the API layer, the registry itself, or error handling are needed.


## Testing

Ten integration tests cover happy paths, boundary conditions, and validation failures.

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