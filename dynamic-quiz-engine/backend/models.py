
from pydantic import BaseModel
class TelemetryEvent(BaseModel):
    sessionId: str
    questionId: int
    eventType: str
    eventValue: str | None
    elapsedMs: int
    timestamp: str
class CoachRequest(BaseModel):
    question: str
    correct: str
    wrong: str
