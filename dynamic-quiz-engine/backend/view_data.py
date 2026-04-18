import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "db" / "quiz.db"


def main():
    if not DB_PATH.exists():
        print("資料庫尚未建立，請先啟動後端或初始化資料庫。")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("==== TelemetryLogs ====")
    rows = cursor.execute(
        "SELECT session_id, question_id, event_type, event_value, elapsed_ms, timestamp FROM TelemetryLogs"
    ).fetchall()
    if not rows:
        print("目前沒有遙測資料。")
    else:
        for row in rows:
            print(
                f"session_id={row[0]}, question_id={row[1]}, event_type={row[2]}, "
                f"event_value={row[3]}, elapsed_ms={row[4]}, timestamp={row[5]}"
            )

    conn.close()


if __name__ == "__main__":
    main()
