
from pathlib import Path
from fastapi import FastAPI
from models import TelemetryEvent, CoachRequest
import sqlite3
import uuid
import json

app = FastAPI()
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "db" / "quiz.db"
SCHEMA_PATH = BASE_DIR / "db" / "schema.sql"


def generate_ai_feedback(question, correct_ans, wrong_ans):
    # 移除 Gemini API 串接，改用靜態 AI 教練回饋
    return (
        f"你選擇了『{wrong_ans}』，但正確答案是『{correct_ans}』。"
        " 這題重點在於法規定義的精確用詞。請再接再厲！"
    )


def init_db():
    if not DB_PATH.exists():
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(DB_PATH) as conn:
            conn.executescript(SCHEMA_PATH.read_text())
    seed_default_questions()


def seed_default_questions():
    with sqlite3.connect(DB_PATH) as conn:
        # 刪除現有題目並重新插入
        conn.execute("DELETE FROM QuizQuestions WHERE module_id = ?", (1,))
        sample_questions = [
            {
                "module_id": 1,
                "content": "以下哪一項不是個人資料保護法所定義的個人資料？",
                "options": {"A": "姓名", "B": "身分證號", "C": "公司名稱", "D": "電話號碼"},
                "correct_key": "C",
            },
            {
                "module_id": 1,
                "content": "依據個資法，蒐集個人資料時，最重要的是什麼？",
                "options": {
                    "A": "事前通知與目的告知",
                    "B": "資料保全設備",
                    "C": "取得資料同意書",
                    "D": "資料備份"},
                "correct_key": "A",
            },
            {
                "module_id": 1,
                "content": "個人資料保護法中，『個人資料』的定義不包括哪一項？",
                "options": {
                    "A": "自然人之姓名",
                    "B": "自然人之住址",
                    "C": "法人之名稱",
                    "D": "自然人之照片"},
                "correct_key": "C",
            },
            {
                "module_id": 1,
                "content": "當個人資料被非法蒐集、處理或利用時，當事人可以行使哪些權利？",
                "options": {
                    "A": "查詢權",
                    "B": "更正權",
                    "C": "停止蒐集權",
                    "D": "以上皆是"},
                "correct_key": "D",
            },
        ]
        for q in sample_questions:
            conn.execute(
                "INSERT INTO QuizQuestions (module_id, content, options_json, correct_key) VALUES (?,?,?,?)",
                (
                    q["module_id"],
                    q["content"],
                    json.dumps(q["options"], ensure_ascii=False),
                    q["correct_key"],
                ),
            )
        conn.commit()


def db():
    init_db()
    return sqlite3.connect(DB_PATH, check_same_thread=False)

@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "API is running. Use /api/quiz/module/1 to fetch quiz data.",
    }

@app.get("/api/quiz/module/{module_id}")
def get_quiz(module_id: int):
    c = db().cursor()
    rows = c.execute(
        "SELECT id, content, options_json, correct_key FROM QuizQuestions WHERE module_id=?",
        (module_id,),
    ).fetchall()
    return [
        {
            "id": r[0],
            "content": r[1],
            "options": json.loads(r[2]),
            "correctKey": r[3],
        }
        for r in rows
    ]

@app.post("/api/telemetry/submit")
def submit_telemetry(events: list[TelemetryEvent]):
    session_id = events[0].sessionId
    c = db().cursor()
    for e in events:
        c.execute(
            "INSERT INTO TelemetryLogs VALUES (?,?,?,?,?,?)",
            (
                session_id,
                e.questionId,
                e.eventType,
                e.eventValue,
                e.elapsedMs,
                e.timestamp,
            ),
        )
    c.connection.commit()
    return {"status": "ok", "sessionId": session_id}

@app.post("/api/ai/coach")
def ai_coach(req: CoachRequest):
    feedback = generate_ai_feedback(req.question, req.correct, req.wrong)
    c = db().cursor()
    c.execute(
        "INSERT INTO AiFeedbackArchive VALUES (?,?,?,?)",
        (str(uuid.uuid4()), req.question, req.wrong, feedback),
    )
    c.connection.commit()
    return {"feedback": feedback}
