
export const telemetryBuffer = [];

export function logEvent(sessionId, questionId, eventType, value, startTime) {
  telemetryBuffer.push({
    sessionId,
    questionId,
    eventType,
    eventValue: value,
    elapsedMs: Date.now() - startTime,
    timestamp: new Date().toISOString(),
  });
}
