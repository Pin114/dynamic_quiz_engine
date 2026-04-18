
import React, { useEffect, useState, useRef } from "react";
import QuizCard from "./components/QuizCard";
import AiCoachModal from "./components/AiCoachModal";
import { telemetryBuffer, logEvent } from "./services/telemetry";

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

  useEffect(() => {
    fetch("/api/quiz/module/1")
      .then(async (r) => {
        if (!r.ok) throw new Error(`Fetch failed: ${r.status}`);
        return r.json();
      })
      .then((data) => {
        setQuestions(data);
      })
      .catch((err) => {
        setError(err.message);
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  async function answer(key) {
    const q = questions[index];
    logEvent(sessionId.current, q.id, "select", key, startTime.current);

    if (key !== q.correctKey) {
      setWrongAnswers(prev => [...prev, {
        question: q.content,
        wrong: q.options[key],
        correct: q.options[q.correctKey]
      }]);
      const res = await fetch("/api/ai/coach", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question: q.content,
          correct: q.options[q.correctKey],
          wrong: q.options[key],
        }),
      });
      setCoach((await res.json()).feedback);
    }

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
  }

  if (loading) {
    return (
      <div className="d-flex justify-content-center align-items-center vh-100">
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
      </div>
    );
  }

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
              <h1 className="h4 mb-0">KGI 動態測驗系統</h1>
            </div>
            <div className="card-body">
              <div className="mb-3">
                <small className="text-muted">
                  題目 {index + 1} / {questions.length}
                </small>
              </div>
              <QuizCard
                question={questions[index]}
                sessionId={sessionId.current}
                startTime={startTime.current}
                onAnswer={answer}
              />
            </div>
          </div>
        </div>
      </div>
      {coach && <AiCoachModal text={coach} onClose={() => setCoach(null)} />}
    </div>
  );
}
