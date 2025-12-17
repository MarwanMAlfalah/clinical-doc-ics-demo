from dataclasses import dataclass
from typing import List, Dict, Any
from datetime import datetime


@dataclass
class LogEvent:
    time: str
    from_state: str
    to_state: str
    action: str
    details: Dict[str, Any]


class StateMachine:
    """
    Minimal ICS state tracker with decision logs.
    """
    def __init__(self):
        self.state = "S0"
        self.log: List[LogEvent] = []

    def transition(self, to_state: str, action: str, details: Dict[str, Any] = None):
        if details is None:
            details = {}
        evt = LogEvent(
            time=datetime.now().isoformat(timespec="seconds"),
            from_state=self.state,
            to_state=to_state,
            action=action,
            details=details
        )
        self.log.append(evt)
        self.state = to_state
