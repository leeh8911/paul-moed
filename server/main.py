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
note_repository = NoteRepository()

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
    note_type = data.get("type")
    name = data.get("name")
    content = data.get("content")
    metadata = data.get("metadata", {})

    if not note_type or not name or not content:
        return (
            jsonify({"error": "Missing required fields: type, name, or content"}),
            400,
        )

    note_id = note_repository.create(note_type, name, content, metadata)
    return jsonify({"message": "Note created successfully", "id": note_id}), 201


@app.route("/notes/<int:note_id>", methods=["GET"])
def get_note(note_id):
    """
    특정 ID의 노트를 가져옴
    """
    note = note_repository.read(note_id)
    if not note:
        return jsonify({"error": "Note not found"}), 404

    return jsonify(note)


@app.route("/notes", methods=["GET"])
def get_all_notes():
    """
    저장소에 저장된 모든 노트를 반환
    """
    notes = note_repository.read_all()
    return jsonify({"notes": notes})


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


@app.route("/notes/<int:note_id>", methods=["DELETE"])
def delete_note(note_id):
    """
    특정 ID의 노트를 삭제
    """
    deleted = note_repository.delete(note_id)
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
