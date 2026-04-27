
#定義了 API 傳輸資料時的格式，確保前端傳過來的資料符合正確的結構
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
