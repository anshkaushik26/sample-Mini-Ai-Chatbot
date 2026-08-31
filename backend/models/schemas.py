from pydantic import BaseModel


class Message(BaseModel):
    id: str
    role: str  # "user" | "assistant"
    content: str
    created_at: str


class Conversation(BaseModel):
    id: str
    title: str
    created_at: str
    messages: list[Message] = []


class CreateConversationRequest(BaseModel):
    title: str | None = None


class ChatRequest(BaseModel):
    conversation_id: str
    message: str
