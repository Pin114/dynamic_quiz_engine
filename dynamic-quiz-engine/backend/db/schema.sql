
CREATE TABLE QuizQuestions (
  id INTEGER PRIMARY KEY,
  module_id INTEGER,
  content TEXT,
  options_json TEXT,
  correct_key TEXT
);

CREATE TABLE QuizSessions (
  session_id TEXT PRIMARY KEY,
  '''agent_id TEXT,'''
  module_id INTEGER,
  score INTEGER,
  completed_at TEXT
);

CREATE TABLE TelemetryLogs (
  session_id TEXT,
  question_id INTEGER,
  event_type TEXT,
  event_value TEXT,
  elapsed_ms INTEGER,
  timestamp TEXT
);

CREATE TABLE AiFeedbackArchive (
  id TEXT PRIMARY KEY,
  question TEXT,
  wrong_answer TEXT,
  feedback TEXT
);
