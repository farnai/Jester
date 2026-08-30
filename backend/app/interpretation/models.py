from pydantic import BaseModel


class JesterMessageRequest(BaseModel):
    context: str
    target_user_id: str | None = None
    user_prompt: str | None = None


class JesterMessageResponse(BaseModel):
    message: str
    tone: str = "smart_warm_ironic"
