from flask import Flask, request, jsonify
from database import NoteRepository
from llm import LLMHandler  # LLM 관련 처리 모듈 (추후 구현)
import logging

# Flask 애플리케이션 초기화
app = Flask(__name__)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s"
)

# 노트 저장소 초기화
note_repository: NoteRepository = NoteRepository()

# LLM 핸들러 초기화
llm_handler = LLMHandler()


@app.route("/")
def home():
    """서버 상태 확인용 엔드포인트"""
    return jsonify({"message": "PAUL MOED server is running!"})


@app.route("/notes", methods=["POST"])
def create_note():
    """
    클라이언트에서 노트를 생성하여 저장소에 추가
    ---
    요청 데이터 예제:
    {
        "type": "memo",
        "name": "회의록",
        "content": "프로젝트 상태 업데이트",
        "metadata": { ... }  # 선택사항
    }
    """
    data = request.json

    if not data.get("type") or not data.get("name") or not data.get("content"):
        return (
            jsonify({"error": "Missing required fields: type, name, or content"}),
            400,
        )

    note_id = note_repository.create(data)
    return jsonify({"message": "Note created successfully", "id": note_id}), 201


@app.route("/notes/<string:note_type>/<int:note_id>", methods=["GET"])
def get_note(note_type, note_id):
    """
    특정 ID의 노트를 가져옴
    """
    note = note_repository.read(note_id, note_type)
    if not note:
        return jsonify({"error": "Note not found"}), 404

    return jsonify(note)


@app.route("/notes", methods=["GET"])
def get_all_notes():
    """
    저장소에 저장된 모든 노트를 반환
    """
    notes = []
    for note_type in note_repository.note_types:
        notes.extend(note_repository.read_all(note_type))

    return jsonify(notes)


@app.route("/notes/filter", methods=["GET"])
def get_filtered_notes():
    """
    다양한 조건(id, created, updated, tags)으로 노트를 필터링
    ---
    쿼리 매개변수:
    - `type`: 필수, 노트 타입 ("memo", "event", "task")
    - `created_start`: 선택, 생성 시작일 (ISO 형식)
    - `created_end`: 선택, 생성 종료일 (ISO 형식)
    - `updated_start`: 선택, 업데이트 시작일 (ISO 형식)
    - `updated_end`: 선택, 업데이트 종료일 (ISO 형식)
    - `tags`: 선택, 쉼표로 구분된 태그 리스트 (예: "work,project")
    """
    note_type = request.args.get("type")
    if not note_type:
        return jsonify({"error": "Note type is required"}), 400

    # 쿼리 매개변수 읽기
    filters = {}
    if "created_start" in request.args and "created_end" in request.args:
        filters["created_start"] = request.args["created_start"]
        filters["created_end"] = request.args["created_end"]
    if "updated_start" in request.args and "updated_end" in request.args:
        filters["updated_start"] = request.args["updated_start"]
        filters["updated_end"] = request.args["updated_end"]
    if "tags" in request.args:
        filters["tags"] = request.args["tags"].split(",")

    try:
        notes = note_repository.get_filtered_notes(note_type, filters)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    return jsonify(notes)


@app.route("/notes/<int:note_id>", methods=["PUT"])
def update_note(note_id):
    """
    특정 ID의 노트를 업데이트
    ---
    요청 데이터 예제:
    {
        "name": "업데이트된 이름",
        "content": "업데이트된 내용",
        "metadata": { ... }  # 선택사항
    }
    """
    data = request.json
    updated = note_repository.update(note_id, data)
    if not updated:
        return jsonify({"error": "Note not found or update failed"}), 404

    return jsonify({"message": "Note updated successfully"})


@app.route("/notes/<string:note_type>/<int:note_id>", methods=["DELETE"])
def delete_note(note_type, note_id):
    """
    특정 ID의 노트를 삭제
    """
    deleted = note_repository.delete(note_id, note_type)
    if not deleted:
        return jsonify({"error": "Note not found"}), 404

    return jsonify({"message": "Note deleted successfully"})


@app.route("/notes", methods=["DELETE"])
def delete_all_notes():
    """
    모든 노트를 삭제
    """
    deleted = note_repository.delete_all()
    if not deleted:
        return jsonify({"error": "Note not found"}), 404

    return jsonify({"message": "Note deleted successfully"})


@app.route("/interact", methods=["POST"])
def interact_with_llm():
    """
    노트 데이터를 기반으로 LLM과 상호작용
    ---
    요청 데이터 예제:
    {
        "note_id": 1,
        "action": "summarize"
    }
    """
    data = request.json
    note_id = data.get("note_id")
    action = data.get("action")

    if not note_id or not action:
        return jsonify({"error": "Missing required fields: note_id or action"}), 400

    note = note_repository.read(note_id)
    if not note:
        return jsonify({"error": "Note not found"}), 404

    response = llm_handler.process(note, action)
    return jsonify(response)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
