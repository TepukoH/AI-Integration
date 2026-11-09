"""Мок-клиент LMS. В реальной эксплуатации — REST API LMS Synergy."""

from dataclasses import dataclass


@dataclass
class StudentProgress:
    student_id: str
    course: str
    progress_pct: float
    last_active_days: int


class LMSClient:
    def __init__(self, base_url: str | None = None, token: str | None = None):
        self.base_url = base_url or "https://lms.example.local/api"
        self.token = token
        self._data: dict[str, StudentProgress] = {}

    def upsert(self, p: StudentProgress) -> None:
        self._data[p.student_id] = p

    def get_progress(self, student_id: str) -> StudentProgress | None:
        return self._data.get(student_id)

    def at_risk(self, progress_threshold: float = 30.0,
                days_threshold: int = 14) -> list[StudentProgress]:
        return [
            p for p in self._data.values()
            if p.progress_pct < progress_threshold or p.last_active_days >= days_threshold
        ]