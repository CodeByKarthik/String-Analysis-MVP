from backend.database import SessionLocal
from backend.models.audit_log import AuditLog
from fastapi.testclient import TestClient
from sqlalchemy import select

ANALYSE_URL = "/analyse"


def test_word_count_basic(client: TestClient) -> None:
    response = client.post(
        f"{ANALYSE_URL}?analyses=word_count", json={"text": "Hello world from Barclays"}
    )
    assert response.status_code == 200
    assert response.json()["results"]["word_count"] == 4


def test_character_count_with_spaces(client: TestClient) -> None:
    response = client.post(
        f"{ANALYSE_URL}?analyses=character_count&include_spaces=true",
        json={"text": "Hello world"},
    )
    assert response.status_code == 200
    assert response.json()["results"]["character_count"] == 11


def test_character_count_without_spaces(client: TestClient) -> None:
    response = client.post(
        f"{ANALYSE_URL}?analyses=character_count&include_spaces=false",
        json={"text": "Hello world"},
    )
    assert response.status_code == 200
    assert response.json()["results"]["character_count"] == 10


def test_sentence_count_handles_abbreviations(client: TestClient) -> None:
    response = client.post(
        f"{ANALYSE_URL}?analyses=sentence_count",
        json={"text": "Dr. Smith went to the U.S.A. yesterday."},
    )
    assert response.status_code == 200
    assert response.json()["results"]["sentence_count"] == 1


def test_multiple_analyses_in_one_request(client: TestClient) -> None:
    text = "Hello world. This is a test."
    response = client.post(
        f"{ANALYSE_URL}?analyses=word_count&analyses=character_count&analyses=sentence_count",
        json={"text": text},
    )
    assert response.status_code == 200
    payload = response.json()
    assert {"word_count", "character_count", "sentence_count"} <= payload[
        "results"
    ].keys()
    assert payload["metadata"]["request_id"]
    assert payload["metadata"]["input_length"] == len(text)
    assert isinstance(payload["metadata"]["processing_time_ms"], (int, float))


def test_input_exceeding_max_length_rejected(client: TestClient) -> None:
    response = client.post(
        f"{ANALYSE_URL}?analyses=word_count",
        json={"text": "a" * 101},
    )
    assert response.status_code == 422
    details = response.json()["detail"]
    assert any(error.get("type") == "string_too_long" for error in details)
    assert any("text" in error.get("loc", []) for error in details)


def test_empty_string_rejected(client: TestClient) -> None:
    response = client.post(
        f"{ANALYSE_URL}?analyses=word_count",
        json={"text": ""},
    )
    assert response.status_code == 422


def test_missing_text_field_rejected(client: TestClient) -> None:
    response = client.post(
        f"{ANALYSE_URL}?analyses=word_count",
        json={},
    )
    assert response.status_code == 422
    details = response.json()["detail"]
    assert any("text" in error.get("loc", []) for error in details)


def test_unknown_analysis_type_rejected(client: TestClient) -> None:
    response = client.post(
        f"{ANALYSE_URL}?analyses=bogus_analyser",
        json={"text": "Hello"},
    )
    assert response.status_code == 422


def test_no_analyses_specified_rejected(client: TestClient) -> None:
    response = client.post(
        ANALYSE_URL,
        json={"text": "Hello"},
    )
    assert response.status_code == 422


def test_analysis_requests_metric_exported(client: TestClient) -> None:
    response = client.post(
        f"{ANALYSE_URL}?analyses=word_count",
        json={"text": "Hello world"},
    )
    assert response.status_code == 200

    metrics_response = client.get("/metrics")
    assert metrics_response.status_code == 200
    metrics = metrics_response.text
    assert "analysis_requests_total" in metrics
    assert 'status="success"' in metrics


def test_analysis_request_and_response_are_audited(client: TestClient) -> None:
    response = client.post(
        f"{ANALYSE_URL}?analyses=character_count&include_spaces=false",
        json={"text": "Hello world"},
    )
    assert response.status_code == 200

    request_id = response.json()["metadata"]["request_id"]
    with SessionLocal() as session:
        audit_log = session.scalar(
            select(AuditLog).where(AuditLog.request_id == request_id)
        )

    assert audit_log is not None
    assert audit_log.query_parameters == {
        "analyses": ["character_count"],
        "include_spaces": ["false"],
    }
    assert audit_log.request_body == {"text": "Hello world"}
    assert isinstance(audit_log.response_body, dict)
    assert audit_log.response_body["results"] == {"character_count": 10}
    assert audit_log.status_code == 200
