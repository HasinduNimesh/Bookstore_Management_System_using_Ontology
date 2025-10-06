"""Ultra-light message bus for agents.

Topics used:
- 'purchase_request'  : Customer -> Employee
- 'purchase_result'   : Employee -> Customer
- 'restock_request'   : Employee (self-init) -> Employee
- 'restock_done'      : Employee -> All
"""
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List
import uuid

@dataclass
class Message:
    topic: str
    sender: str
    payload: dict
    conversation_id: str = field(default_factory=lambda: str(uuid.uuid4()))

class MessageBus:
    def __init__(self):
        self._subs: Dict[str, List[Callable[[Message], None]]] = {}
        self._queues: Dict[str, List[Message]] = {}

    def publish(self, topic: str, message: Message):
        self._queues.setdefault(topic, []).append(message)

    def drain(self, topic: str) -> List[Message]:
        q = self._queues.get(topic, [])
        self._queues[topic] = []
        return q

    def subscribe(self, topic: str, handler: Callable[[Message], None]):
        self._subs.setdefault(topic, []).append(handler)

    def deliver(self):
        """Synchronous fan-out delivery to subscribers. Invoke once per step."""
        for topic, subs in self._subs.items():
            if not subs: continue
            messages = self.drain(topic)
            for m in messages:
                for h in subs:
                    h(m)
