
import React, { useEffect, useState, useRef } from "react";
import QuizCard from "./components/QuizCard";
import AiCoachModal from "./components/AiCoachModal";
import { telemetryBuffer, logEvent } from "./services/telemetry";

// 定義了多個 useState 來驅動畫面更新
// 使用 useRef 紀錄不需要觸發重新渲染的資訊
export default function App() {
  const [questions, setQuestions] = useState([]);
  const [index, setIndex] = useState(0);
  const [coach, setCoach] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [wrongAnswers, setWrongAnswers] = useState([]);
  const [showReport, setShowReport] = useState(false);
  const sessionId = useRef(crypto.randomUUID());
  const startTime = useRef(Date.now());

  useEffect(() => { // 在頁面第一次載入時，從後端 API 獲取題目數據
    fetch("/api/quiz/module/1")
      .then(async (r) => {
        if (!r.ok) throw new Error(`Fetch failed: ${r.status}`);
        return r.json(); 
      })
      .then((data) => {
        setQuestions(data); // 將獲取到的題目數據存儲在 state 中
      })
      .catch((err) => { // 如果獲取過程中出現錯誤，將錯誤信息存儲在 state 中
        setError(err.message);
      })
      .finally(() => {
        setLoading(false); // 不管成功或失敗，都關閉「載入中」動畫
      });
  }, []);

  async function answer(key) {
    const q = questions[index];
    logEvent(sessionId.current, q.id, "select", key, startTime.current); // 記錄使用者選擇的答案和花費的時間

    if (key !== q.correctKey) {
      setWrongAnswers((prev) => [
        ...prev,
        {
          question: q.content,
          wrong: q.options[key],
          correct: q.options[q.correctKey],
        },
      ]);
      const res = await fetch("/api/ai/coach", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ //  向 /api/ai/coach 發送 POST 請求，傳入題目與使用者的選項
          question: q.content,
          correct: q.options[q.correctKey],
          wrong: q.options[key],
        }),
      });
      setCoach((await res.json()).feedback);
      return;
    }

    // 如果是最後一題：將這段期間所有累積在 telemetryBuffer 的操作數據（滑鼠移過、點擊時間等）一次性 POST 給 /api/telemetry/submit 儲存，然後顯示結算報告。
    if (index === questions.length - 1) {
      await fetch("/api/telemetry/submit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(telemetryBuffer),
      });
      setShowReport(true);
    } else { // 如果不是最後一題：跳到下一題 (index + 1)，並重設下一題的計時起點。
      setIndex(index + 1);
      startTime.current = Date.now();
    }
  }

  // 顯示 Bootstrap 的 Spinner 旋轉動畫
  if (loading) {
    return (
      <div className="d-flex justify-content-center align-items-center vh-100">
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
      </div>
    );
  }

  //顯示錯誤訊息警告框
  if (error) {
    return (
      <div className="container mt-5">
        <div className="alert alert-danger" role="alert">
          <h4 className="alert-heading">載入失敗</h4>
          <p>{error}</p>
        </div>
      </div>
    );
  }

  if (!questions.length) {
    return (
      <div className="container mt-5">
        <div className="alert alert-warning" role="alert">
          <h4 className="alert-heading">目前沒有題目</h4>
          <p>請稍後再試。</p>
        </div>
      </div>
    );
  }

  // 測驗完成 (showReport)：顯示錯題列表與「重新測驗」按鈕
  if (showReport) {
    return (
      <div className="container-fluid bg-light min-vh-100">
        <div className="row justify-content-center">
          <div className="col-md-8 col-lg-6">
            <div className="card shadow mt-5">
              <div className="card-header bg-success text-white">
                <h1 className="h4 mb-0">測驗完成！</h1>
              </div>
              <div className="card-body">
                <h3>錯題報告</h3>
                {wrongAnswers.length === 0 ? (
                  <p className="text-success">恭喜！全部答對！</p>
                ) : (
                  <div>
                    <p>您答錯了 {wrongAnswers.length} 題：</p>
                    <ul className="list-group">
                      {wrongAnswers.map((item, idx) => (
                        <li key={idx} className="list-group-item">
                          <strong>題目：</strong> {item.question}<br />
                          <span className="text-danger">您的答案：{item.wrong}</span><br />
                          <span className="text-success">正確答案：{item.correct}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                <button className="btn btn-primary mt-3" onClick={() => window.location.reload()}>
                  重新測驗
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container-fluid bg-light min-vh-100">
      <div className="row justify-content-center">
        <div className="col-md-8 col-lg-6">
          <div className="card shadow mt-5">
            <div className="card-header bg-primary text-white">
              <h1 className="h4 mb-0">動態測驗系統</h1>
            </div>
            <div className="card-body">
              <div className="mb-3">
                <small className="text-muted">
                  題目 {index + 1} / {questions.length}
                </small>
              </div>
              <QuizCard //QuizCard：負責顯示題目。
              // App.jsx 把目前這題的資料、sessionId 傳給它，並監聽它的 onAnswer 事件。
                question={questions[index]}
                sessionId={sessionId.current}
                startTime={startTime.current}
                onAnswer={answer}
              />
            </div>
          </div>
        </div>
      </div>
      
      {coach && <AiCoachModal text={coach} onClose={async () => { 
        //當 coach 狀態有文字時才出現。它有一個 onClose 邏輯，當使用者點擊「我懂了」關閉彈窗時，程式會檢查是否要進入下一題或結算。
        setCoach(null);
        if (index === questions.length - 1) {
          await fetch("/api/telemetry/submit", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(telemetryBuffer),
          });
          setShowReport(true);
        } else {
          setIndex(index + 1);
          startTime.current = Date.now();
        }
      }} />}
    </div>
  );
}
