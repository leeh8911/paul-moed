import requests
import logging
from typing import Optional, List, Dict, Union
from datetime import datetime


class HTTPStatus:
    """HTTP 상태 코드 상수"""

    OK = 200  # 요청 성공
    CREATED = 201  # 생성 성공
    NO_CONTENT = 204  # 내용 없음

    BAD_REQUEST = 400  # 잘못된 요청
    UNAUTHORIZED = 401  # 인증 필요
    FORBIDDEN = 403  # 접근 금지
    NOT_FOUND = 404  # 리소스를 찾을 수 없음
    METHOD_NOT_ALLOWED = 405  # 허용되지 않은 메서드
    CONFLICT = 409  # 리소스 충돌

    INTERNAL_SERVER_ERROR = 500  # 서버 오류
    NOT_IMPLEMENTED = 501  # 구현되지 않음
    BAD_GATEWAY = 502  # 게이트웨이 오류
    SERVICE_UNAVAILABLE = 503  # 서비스 이용 불가


class Repository:
    """서버와 통신을 담당하는 Repository 클래스"""

    def __init__(self, protocol: str, host: str, port: int):
        """
        초기화 메서드

        Args:
            protocol (str): 프로토콜 (예: "http")
            host (str): 서버 호스트명
            port (int): 서버 포트 번호
        """
        self.protocol = protocol
        self.host = host
        self.port = port
        self.server = f"{protocol}://{host}:{port}"

    def _build_url(self, endpoint: str) -> str:
        """
        엔드포인트를 포함한 URL 생성

        Args:
            endpoint (str): API 엔드포인트
        Returns:
            str: 완성된 URL
        """
        return f"{self.server}{endpoint}"

    def _handle_response(
        self, response: requests.Response, success_message: str
    ) -> Union[Dict, List, None]:
        """
        서버 응답 처리

        Args:
            response (requests.Response): 서버 응답 객체
            success_message (str): 성공 시 로깅 메시지

        Returns:
            dict or list or None: 서버 응답 데이터
        """
        try:
            if response.status_code in range(200, 300):
                logging.info(success_message)
                return response.json()
            else:
                logging.error(
                    f"Error: {response.status_code} - {response.reason} - {response.text}"
                )
                return {"error": response.reason}
        except ValueError as e:
            logging.error(f"Response parsing failed: {e}")
            return {"error": "Invalid JSON response"}
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            return {"error": "Unexpected error occurred"}

    def new_note(self, **kwargs) -> Optional[Dict]:
        """
        새로운 노트 생성

        Args:
            **kwargs: 노트 데이터
        Returns:
            dict: 생성된 노트 정보
        """
        try:
            response = requests.post(self._build_url("/notes"), json=kwargs)
            return self._handle_response(response, f"Success: New {kwargs.get('type')}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to create note: {e}")
            return {"error": "Connection error"}

    def get_note(self, note_id: int) -> Optional[Dict]:
        """
        특정 ID의 노트 가져오기

        Args:
            note_id (int): 노트 ID
        Returns:
            dict: 노트 정보
        """
        try:
            response = requests.get(self._build_url(f"/notes/{note_id}"))
            return self._handle_response(response, f"Retrieved note with ID {note_id}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to retrieve note: {e}")
            return {"error": "Connection error"}

    def get_all_notes(self) -> Optional[List[Dict]]:
        """
        모든 노트 가져오기

        Returns:
            list: 노트 리스트
        """
        try:
            response = requests.get(self._build_url("/notes"))
            return self._handle_response(response, "Retrieved all notes")
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to retrieve all notes: {e}")
            return {"error": "Connection error"}

    def filtered_notes(
        self,
        note_type: str,
        created_start: Optional[datetime] = None,
        created_end: Optional[datetime] = None,
        updated_start: Optional[datetime] = None,
        updated_end: Optional[datetime] = None,
        tags: Optional[List[str]] = None,
    ) -> List[Dict]:
        """
        필터 조건을 기반으로 노트를 가져옵니다.

        Args:
            note_type (str): 필수, 노트 타입 ("memo", "event", "task").
            created_start (datetime): 선택, 생성 시작일.
            created_end (datetime): 선택, 생성 종료일.
            updated_start (datetime): 선택, 업데이트 시작일.
            updated_end (datetime): 선택, 업데이트 종료일.
            tags (List[str]): 선택, 태그 리스트.

        Returns:
            list: 필터링된 노트 리스트
        """
        filter_params = {"type": note_type}
        if created_start and created_end:
            filter_params.update(
                {
                    "created_start": created_start.isoformat(),
                    "created_end": created_end.isoformat(),
                }
            )
        if updated_start and updated_end:
            filter_params.update(
                {
                    "updated_start": updated_start.isoformat(),
                    "updated_end": updated_end.isoformat(),
                }
            )
        if tags:
            filter_params["tags"] = ",".join(tags)

        try:
            response = requests.get(
                self._build_url("/notes/filter"), params=filter_params
            )
            return self._handle_response(
                response, "Filtered notes retrieved successfully"
            )
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to retrieve filtered notes: {e}")
            return {"error": "Connection error"}

    def update_note(self, note_id: int, **kwargs) -> Optional[Dict]:
        """
        노트 업데이트

        Args:
            note_id (int): 노트 ID
            **kwargs: 업데이트할 데이터
        Returns:
            dict: 업데이트된 노트 정보
        """
        try:
            if "id" in kwargs:
                kwargs.update({"id": note_id})
            response = requests.put(self._build_url(f"/notes/{note_id}"), json=kwargs)
            return self._handle_response(response, f"Updated note with ID {note_id}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to update note: {e}")
            return {"error": "Connection error"}

    def delete_note(self, note_id: int) -> Optional[Dict]:
        """
        노트 삭제

        Args:
            note_id (int): 노트 ID
        Returns:
            dict: 삭제 결과
        """
        try:
            response = requests.delete(self._build_url(f"/notes/{note_id}"))
            return self._handle_response(response, f"Deleted note with ID {note_id}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to delete note: {e}")
            return {"error": "Connection error"}

    def delete_all_notes(self) -> Optional[Dict]:
        """
        모든 노트 삭제

        Returns:
            dict: 삭제 결과
        """
        try:
            response = requests.delete(self._build_url("/notes"))
            return self._handle_response(response, "Deleted all notes")
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to delete all notes: {e}")
            return {"error": "Connection error"}

    def ping(self) -> Optional[Dict]:
        """
        서버 상태 확인

        Returns:
            dict: 서버 상태
        """
        try:
            response = requests.get(self._build_url("/ping"))
            return self._handle_response(response, "Server is reachable")
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to ping server: {e}")
            return {"error": "Connection error"}
