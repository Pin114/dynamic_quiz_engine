
import { logEvent } from "../services/telemetry";

export default function QuizCard({ question, sessionId, startTime, onAnswer }) {
  return (
    <div>
      <h3 className="mb-4">{question.content}</h3>
      <div className="d-grid gap-3">
        {Object.entries(question.options).map(([k, v]) => (
          <button
            key={k}
            className="btn btn-outline-primary btn-lg text-start"
            onMouseEnter={() => logEvent(sessionId, question.id, "hover", k, startTime)}
            onClick={() => onAnswer(k)}
          >
            <strong>{k}.</strong> {v}
          </button>
        ))}
      </div>
    </div>
  );
}
