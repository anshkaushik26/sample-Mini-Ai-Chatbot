from fastapi import APIRouter, HTTPException

from models.schemas import CreateConversationRequest
from services import conversation_service

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.post("")
def create_conversation(body: CreateConversationRequest):
    return conversation_service.create_conversation(body.title)


@router.get("")
def list_conversations():
    return conversation_service.list_conversations()


@router.get("/{conversation_id}/messages")
def get_messages(conversation_id: str):
    conversation = conversation_service.get_conversation(conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation["messages"]


@router.delete("/{conversation_id}")
def delete_conversation(conversation_id: str):
    deleted = conversation_service.delete_conversation(conversation_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"deleted": True}
