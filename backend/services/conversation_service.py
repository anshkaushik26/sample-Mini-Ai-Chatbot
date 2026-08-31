import json
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path

STORAGE_PATH = Path(__file__).resolve().parent.parent / "storage" / "conversations.json"

_lock = threading.Lock()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_all() -> dict:
    if not STORAGE_PATH.exists():
        return {}
    with STORAGE_PATH.open("r") as f:
        content = f.read().strip()
        return json.loads(content) if content else {}


def _write_all(data: dict) -> None:
    STORAGE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with STORAGE_PATH.open("w") as f:
        json.dump(data, f, indent=2)


def create_conversation(title: str | None = None) -> dict:
    with _lock:
        data = _read_all()
        conv_id = str(uuid.uuid4())
        conversation = {
            "id": conv_id,
            "title": title or "New Conversation",
            "created_at": _now(),
            "messages": [],
        }
        data[conv_id] = conversation
        _write_all(data)
        return conversation


def list_conversations() -> list[dict]:
    with _lock:
        data = _read_all()
        conversations = list(data.values())
        conversations.sort(key=lambda c: c["created_at"], reverse=True)
        return conversations


def get_conversation(conversation_id: str) -> dict | None:
    with _lock:
        data = _read_all()
        return data.get(conversation_id)


def delete_conversation(conversation_id: str) -> bool:
    with _lock:
        data = _read_all()
        if conversation_id not in data:
            return False
        del data[conversation_id]
        _write_all(data)
        return True


def add_message(conversation_id: str, role: str, content: str) -> dict | None:
    with _lock:
        data = _read_all()
        conversation = data.get(conversation_id)
        if conversation is None:
            return None
        message = {
            "id": str(uuid.uuid4()),
            "role": role,
            "content": content,
            "created_at": _now(),
        }
        conversation["messages"].append(message)
        if role == "user" and conversation["title"] in (None, "New Conversation"):
            conversation["title"] = content[:60]
        _write_all(data)
        return message
