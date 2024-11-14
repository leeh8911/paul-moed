import pytest
import requests

BASE_URL = "http://127.0.0.1:5000/notes"


@pytest.fixture
def cleanup():
    """
    Clean up the database before and after each test.
    """
    print("call cleanup")
    yield
    requests.delete(f"{BASE_URL}")


def test_memo_operations(cleanup):
    # 1. Memo 생성
    memo_data = {
        "type": "memo",
        "name": "Test Memo",
        "content": "This is a test memo.",
        "tags": ["test"],
    }
    response = requests.post(BASE_URL, json=memo_data)
    assert response.status_code == 201
    memo_id = response.json().get("id")
    assert memo_id is not None

    # 2. Memo 읽기
    response = requests.get(f"{BASE_URL}/memo/{memo_id}")
    assert response.status_code == 200
    memo = response.json()
    assert memo["name"] == "Test Memo"
    assert memo["content"] == "This is a test memo."

    # 3. Memo 수정
    memo["name"] = "Updated Memo"
    memo["content"] = "Updated content."
    memo["tags"].append("test updated")
    response = requests.put(f"{BASE_URL}/{memo_id}", json=memo)
    assert response.status_code == 200

    # 4. Memo 수정 확인
    response = requests.get(f"{BASE_URL}/memo/{memo_id}")
    assert response.status_code == 200
    updated_memo = response.json()
    assert updated_memo["name"] == "Updated Memo"
    assert updated_memo["content"] == "Updated content."

    # 5. Memo 삭제
    response = requests.delete(f"{BASE_URL}/memo/{memo_id}")
    assert response.status_code == 200

    # 6. Memo 삭제 확인
    response = requests.get(f"{BASE_URL}/memo/{memo_id}")
    assert response.status_code == 404


def test_event_operations(cleanup):
    # 1. Event 생성
    event_data = {
        "type": "event",
        "name": "Test Event",
        "content": "Event details",
        "date": "2024-12-31T23:59:59",
    }
    response = requests.post(BASE_URL, json=event_data)
    assert response.status_code == 201
    event_id = response.json().get("id")
    assert event_id is not None

    # 2. Event 읽기
    response = requests.get(f"{BASE_URL}/event/{event_id}")
    assert response.status_code == 200
    event = response.json()
    assert event["name"] == "Test Event"
    assert event["content"] == "Event details"

    # 3. Event 삭제
    response = requests.delete(f"{BASE_URL}/event/{event_id}")
    assert response.status_code == 200

    # 4. Event 삭제 확인
    response = requests.get(f"{BASE_URL}/event/{event_id}")
    assert response.status_code == 404


def test_task_operations(cleanup):
    # 1. Task 생성
    task_data = {
        "type": "task",
        "name": "Test Task",
        "content": "Task details",
        "due_date": "2024-12-31T23:59:59",
        "done": False,
    }
    response = requests.post(BASE_URL, json=task_data)
    assert response.status_code == 201
    task_id = response.json().get("id")
    assert task_id is not None

    # 2. Task 읽기
    response = requests.get(f"{BASE_URL}/task/{task_id}")
    assert response.status_code == 200
    task = response.json()
    assert task["name"] == "Test Task"
    assert task["content"] == "Task details"

    # 3. Task 상태 변경
    task["done"] = True
    response = requests.put(f"{BASE_URL}/{task_id}", json=task)
    assert response.status_code == 200

    # 4. Task 상태 변경 확인
    response = requests.get(f"{BASE_URL}/task/{task_id}")
    assert response.status_code == 200
    updated_task = response.json()
    assert updated_task["done"] is True

    # 5. Task 삭제
    response = requests.delete(f"{BASE_URL}/task/{task_id}")
    assert response.status_code == 200

    # 6. Task 삭제 확인
    response = requests.get(f"{BASE_URL}/task/{task_id}")
    assert response.status_code == 404


def test_count_notes(cleanup):
    """
    Note 개수를 확인하고 필터링 조건에 따른 결과를 검증하는 테스트
    """

    # 초기 Note 개수 확인
    initial_response = requests.get(BASE_URL)
    assert initial_response.status_code == 200
    initial_notes = initial_response.json()
    initial_count = len(initial_notes)

    # Memo 생성
    memo_data = {
        "type": "memo",
        "name": "Count Memo",
        "content": "This is a count test.",
        "tags": ["group1"],
    }
    requests.post(BASE_URL, json=memo_data)

    # Event 생성
    event_data_1 = {
        "type": "event",
        "name": "Count Event",
        "content": "Event details for count.",
        "date": "2024-12-31T23:59:59",
        "tags": ["group1", "group2"],
    }
    requests.post(BASE_URL, json=event_data_1)

    event_data_2 = {
        "type": "event",
        "name": "Count Event 2",
        "content": "Event details for count.",
        "date": "2024-12-31T23:59:59",
        "tags": ["group1", "group3"],
    }
    requests.post(BASE_URL, json=event_data_2)

    event_data_3 = {
        "type": "event",
        "name": "Count Event 3",
        "content": "Event details for count.",
        "date": "2024-12-31T23:59:59",
        "tags": ["group1", "group2"],
    }
    requests.post(BASE_URL, json=event_data_3)

    # Task 생성
    task_data = {
        "type": "task",
        "name": "Count Task",
        "content": "Task details for count.",
        "due_date": "2024-12-31T23:59:59",
        "done": False,
        "tags": ["group1", "group3"],
    }
    requests.post(BASE_URL, json=task_data)

    # 전체 Note 개수 확인
    response = requests.get(BASE_URL)
    assert response.status_code == 200
    all_notes = response.json()
    assert len(all_notes) == initial_count + 5

    # Event 중 tags에 "group1"과 "group2"가 포함된 노트 필터링
    filter_url = f"{BASE_URL}/filter?type=event&tags=group1,group2"
    response = requests.get(filter_url)
    assert response.status_code == 200
    filtered_notes = response.json()
    assert len(filtered_notes) == 2  # `event_data_1`와 `event_data_3`이 필터에 맞음
