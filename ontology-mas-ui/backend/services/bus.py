"""Simple event bus for broadcasting to WebSocket clients."""
from typing import List, Callable, Any
import asyncio
import logging

logger = logging.getLogger(__name__)

class EventBus:
    """In-memory event bus for simulation events."""
    
    def __init__(self):
        self.subscribers: List[Callable[[dict], None]] = []
    
    def subscribe(self, callback: Callable[[dict], None]):
        """Subscribe to events."""
        self.subscribers.append(callback)
    
    def unsubscribe(self, callback: Callable[[dict], None]):
        """Unsubscribe from events."""
        if callback in self.subscribers:
            self.subscribers.remove(callback)
    
    async def publish(self, event: dict):
        """Publish event to all subscribers."""
        for callback in self.subscribers:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(event)
                else:
                    callback(event)
            except Exception as e:
                logger.error(f"Error in event subscriber: {e}")
    
    def clear(self):
        """Clear all subscribers."""
        self.subscribers.clear()

# Global event bus instance
event_bus = EventBus()
