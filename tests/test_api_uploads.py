from io import BytesIO

from fastapi.testclient import TestClient

from src.api import MAX_RESUMES, app


client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_rank_rejects_unsupported_job_description() -> None:
    response = client.post(
        "/rank",
        files=[
            (
                "job_description",
                ("job.exe", BytesIO(b"not a document"), "application/octet-stream"),
            ),
            (
                "resumes",
                ("resume.txt", BytesIO(b"Python developer"), "text/plain"),
            ),
        ],
    )

    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]


def test_rank_rejects_unsupported_resume() -> None:
    response = client.post(
        "/rank",
        files=[
            (
                "job_description",
                ("job.txt", BytesIO(b"Looking for a Python developer"), "text/plain"),
            ),
            (
                "resumes",
                ("resume.exe", BytesIO(b"not a resume"), "application/octet-stream"),
            ),
        ],
    )

    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]


def test_rank_rejects_more_than_maximum_resumes() -> None:
    files = [
        (
            "job_description",
            ("job.txt", BytesIO(b"Looking for Python"), "text/plain"),
        )
    ]

    files.extend(
        (
            "resumes",
            (
                f"resume_{index}.txt",
                BytesIO(b"Python developer"),
                "text/plain",
            ),
        )
        for index in range(MAX_RESUMES + 1)
    )

    response = client.post("/rank", files=files)

    assert response.status_code == 400
    assert f"maximum of {MAX_RESUMES}" in response.json()["detail"]
def test_rank_rejects_empty_job_description() -> None:
    response = client.post(
        "/rank",
        files=[
            (
                "job_description",
                ("job.txt", BytesIO(b""), "text/plain"),
            ),
            (
                "resumes",
                ("resume.txt", BytesIO(b"Python developer"), "text/plain"),
            ),
        ],
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "job.txt is empty."