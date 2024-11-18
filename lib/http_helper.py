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
