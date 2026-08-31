from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from models.schemas import ChatRequest
from services import conversation_service, gemini_service

router = APIRouter(tags=["chat"])


@router.post("/chat")
def chat(body: ChatRequest):
    conversation = conversation_service.get_conversation(body.conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")

    history = conversation["messages"]
    conversation_service.add_message(body.conversation_id, "user", body.message)

    reply = gemini_service.generate_reply(history, body.message)

    conversation_service.add_message(body.conversation_id, "assistant", reply)
    return {"reply": reply}


@router.post("/chat/stream")
def chat_stream(body: ChatRequest):
    conversation = conversation_service.get_conversation(body.conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")

    history = list(conversation["messages"])
    conversation_service.add_message(body.conversation_id, "user", body.message)

    def event_generator():
        full_reply = []
        try:
            for chunk in gemini_service.stream_reply(history, body.message):
                full_reply.append(chunk)
                yield chunk
        finally:
            if full_reply:
                conversation_service.add_message(
                    body.conversation_id, "assistant", "".join(full_reply)
                )

    return StreamingResponse(event_generator(), media_type="text/plain")
