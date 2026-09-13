from io import BytesIO

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from src.api import MAX_RESUMES, app, validate_filename
from src.config import UploadConfig


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


@pytest.mark.parametrize(
    ("uploaded_name", "expected_name"),
    [
        (r"C:\fake\folder\resume.pdf", "resume.pdf"),
        ("/fake/folder/candidate.docx", "candidate.docx"),
    ],
)
def test_validate_filename_removes_uploaded_paths(
    uploaded_name: str,
    expected_name: str,
) -> None:
    assert validate_filename(uploaded_name) == expected_name


def test_validate_filename_rejects_excessive_length() -> None:
    oversized_name = f"{'a' * 181}.pdf"

    with pytest.raises(HTTPException) as error:
        validate_filename(oversized_name)

    assert error.value.status_code == 400
    assert "filename is too long" in str(error.value.detail)


@pytest.mark.parametrize(
    "invalid_config",
    [
        {"max_resumes": 0},
        {"max_file_size_bytes": 0},
        {"read_chunk_size_bytes": 0},
        {"max_filename_length": 0},
        {"allowed_extensions": frozenset()},
        {"allowed_extensions": frozenset({"PDF"})},
    ],
)
def test_upload_config_rejects_invalid_values(
    invalid_config: dict[str, object],
) -> None:
    with pytest.raises(ValueError):
        UploadConfig(**invalid_config)
