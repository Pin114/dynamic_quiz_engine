
from pathlib import Path
from fastapi import FastAPI
from models import TelemetryEvent, CoachRequest
import sqlite3
import uuid
import json

#使用 FastAPI 框架撰寫。它扮演著資料管理員的角色，負責與 SQLite 資料庫溝通，並提供 API 給前端呼叫

app = FastAPI()
BASE_DIR = Path(__file__).resolve().parent #利用 pathlib 找出資料庫檔案 (quiz.db) 與資料表結構檔案 (schema.sql) 的絕對路徑
DB_PATH = BASE_DIR / "db" / "quiz.db"
SCHEMA_PATH = BASE_DIR / "db" / "schema.sql" 


def generate_ai_feedback(question, correct_ans, wrong_ans):
    # 靜態 AI 教練回饋
    return (
        f"你選擇了『{wrong_ans}』，但正確答案是『{correct_ans}』。"
        " 這題重點在於法規定義的精確用詞。請再接再厲！"
    )

# 初始化資料庫：如果 quiz.db 不存在，就建立它並執行 schema.sql 裡的 SQL 指令來建立資料表結構。
# 接著呼叫 seed_default_questions() 來插入預設的測驗題目。
def init_db():
    is_new_db = False
    if not DB_PATH.exists():
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(DB_PATH) as conn:
            conn.executescript(SCHEMA_PATH.read_text())
        is_new_db = True
    if is_new_db:
        seed_default_questions()

# 如果資料表 QuizQuestions 裡已經有 module_id = 1 的題目，就不插入；如果沒有，就插入四題關於個人資料保護法的測驗題目。
def seed_default_questions():
    with sqlite3.connect(DB_PATH) as conn:
        count = conn.execute(
            "SELECT COUNT(*) FROM QuizQuestions WHERE module_id = ?",
            (1,),
        ).fetchone()[0]
        if count != 0:
            return
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

#提供一個 API 讓前端可以根據 module_id 來取得對應的測驗題目資料。它會從 QuizQuestions 資料表裡撈出符合條件的題目，並把 options_json 欄位的 JSON 字串轉回 Python dict 後回傳給前端。
@app.get("/api/quiz/module/{module_id}")
def get_quiz(module_id: int):
    c = db().cursor() # 連接資料庫並建立 cursor 物件來執行 SQL 查詢
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
# 提供一個 API 讓前端提交遙測事件資料。它會接收一個 TelemetryEvent 物件的列表，然後把每個事件的資料插入到 TelemetryLogs 資料表裡。
# 最後回傳一個包含狀態和 sessionId 的 JSON 物件給前端。
@app.post("/api/telemetry/submit")
def submit_telemetry(events: list[TelemetryEvent]): # 接收一個 TelemetryEvent 清單（這是由 models.py 定義的格式）
    if not events:
        return {"status": "error", "message": "No events provided"}

    session_id = events[0].sessionId
    conn = db()
    c = conn.cursor()

    for e in events: # 利用迴圈將清單中的每一項動作（如滑鼠懸停、點擊、思考毫秒數）逐一寫入 TelemetryLogs 資料表
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

    # 計算總分並存入 QuizSessions
    # 在後端根據 select 事件與資料庫的 correct_key 比對來算分，而不是讓前端直接傳分數過來。這樣可以防止使用者透過修改前端代碼來竄改分數
    select_events = [e for e in events if e.eventType == "select"]
    
    score = 0
    module_id = 1 # 預設模組 ID，實務上可從前端傳入
    
    for sev in select_events:
        # 從資料庫比對正確答案
        correct_key = c.execute(
            "SELECT correct_key FROM QuizQuestions WHERE id = ?", 
            (sev.questionId,)
        ).fetchone()[0]
        
        if sev.eventValue == correct_key:
            score += 1

    # 寫入 QuizSessions 資料表
    # 假設 schema.sql 定義為: session_id, module_id, score, completed_at
    from datetime import datetime
    c.execute(
        "INSERT INTO QuizSessions (session_id, module_id, score, completed_at) VALUES (?, ?, ?, ?)",
        (
            session_id,
            module_id,
            score,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
    )

    conn.commit()# 提交交易，確保資料寫入資料庫
    return {"status": "ok", "sessionId": session_id, "finalScore": score}

# 提供一個 API 讓前端提交 AI 教練請求。它會接收一個 CoachRequest 物件，然後呼叫 generate_ai_feedback() 函式來產生回饋文字。
# 當使用者答錯時，前端會請求這項服務，並把題目內容、正確答案和使用者選錯的答案傳給它。它會根據這些資訊產生一段 AI 教練回饋文字，然後把這段文字插入到 AiFeedbackArchive 資料表裡，最後回傳給前端。
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
