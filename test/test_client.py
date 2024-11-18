import pytest
import requests
from unittest.mock import patch
from client.repository import Repository
from client.memo_tab import MemoTab
from client.todo_tab import TodoTab

# Sample configurations
PROTOCOL = "http"
HOST = "localhost"
PORT = "8000"


@pytest.fixture
def repository():
    """Repository 객체를 반환하는 pytest fixture"""
    return Repository(PROTOCOL, HOST, PORT)


@pytest.fixture
def mock_response():
    """Mocked requests.Response 객체"""

    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    return MockResponse


@patch("requests.get")
def test_repository_get_all_notes(mock_get, repository, mock_response):
    """모든 노트를 가져오는 테스트"""
    mock_get.return_value = mock_response({"notes": []}, 200)

    notes = repository.get_all_notes()
    assert notes == {"notes": []}
    mock_get.assert_called_with(f"{repository.server}/notes")


@patch("requests.get")
def test_repository_filtered_notes(mock_get, repository, mock_response):
    """필터 조건으로 노트를 가져오는 테스트"""
    mock_get.return_value = mock_response(
        {"notes": [{"id": 1, "name": "Test Note"}]}, 200
    )

    notes = repository.filtered_notes(note_type="memo", tags=["test"])
    assert len(notes) == 1
    assert notes[0]["id"] == 1
    mock_get.assert_called_once()


@patch("requests.post")
def test_repository_new_note_success(mock_post, repository, mock_response):
    """새로운 노트 생성 성공 테스트"""
    mock_post.return_value = mock_response({"id": 1}, 201)

    new_note = {"type": "memo", "name": "Test Note", "content": "Content"}
    response = repository.new_note(**new_note)
    assert response == {"id": 1}
    mock_post.assert_called_with(f"{repository.server}/notes", json=new_note)


@patch("requests.post")
def test_repository_new_note_failure(mock_post, repository, mock_response):
    """새로운 노트 생성 실패 테스트"""
    mock_post.return_value = mock_response({"error": "Bad Request"}, 400)

    new_note = {"type": "memo", "name": "Test Note", "content": "Content"}
    response = repository.new_note(**new_note)
    assert response is None
    mock_post.assert_called_with(f"{repository.server}/notes", json=new_note)


@patch("requests.put")
def test_repository_update_note_success(mock_put, repository, mock_response):
    """노트 업데이트 성공 테스트"""
    mock_put.return_value = mock_response({"message": "Updated"}, 200)

    note_updates = {"name": "Updated Note"}
    response = repository.update_note(1, **note_updates)
    assert response == {"message": "Updated"}
    mock_put.assert_called_with(f"{repository.server}/notes/1", json=note_updates)


@patch("requests.delete")
def test_repository_delete_note_success(mock_delete, repository, mock_response):
    """노트 삭제 성공 테스트"""
    mock_delete.return_value = mock_response({"message": "Deleted"}, 200)

    response = repository.delete_note(1)
    assert response == {"message": "Deleted"}
    mock_delete.assert_called_with(f"{repository.server}/notes/1")
