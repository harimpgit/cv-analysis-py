import os
import pytest
from fastapi.testclient import TestClient
from cv_analysis import app

client = TestClient(app)

def test_upload_cv():
    file_path = "data/sample_cvs/File.pdf"
    with open(file_path, "rb") as file:
        response = client.post("/upload_cv/", files={"file": file})
    assert response.status_code == 200
    assert "message" in response.json()

def test_list_cvs():
    response = client.get("/list_cvs/")
    assert response.status_code == 200
    assert "cvs" in response.json()

def test_chatbot_query():
    response = client.post("/chatbot/", json={"filename": "sample", "message": "What skills does this person have?"})
    assert response.status_code == 200
    assert isinstance(response.json(), str)
