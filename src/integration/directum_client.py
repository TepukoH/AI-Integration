from dataclasses import dataclass, field

@dataclass
class Ticket:
    id: str
    subject: str
    body: str
    status: str = "new"


class DirectumClient:
    def __init__(self, base_url: str | None = None, token: str | None = None):
        self.base_url = base_url or "https://directum.example.local/api"
        self.token = token
        self._tickets: list[Ticket] = []
        self._counter = 0

    def create_ticket(self, subject: str, body: str) -> Ticket:
        self._counter += 1
        t = Ticket(id=f"RX-{self._counter:05d}", subject=subject, body=body)
        self._tickets.append(t)
        return t

    def list_tickets(self) -> list[Ticket]:
        return list(self._tickets)