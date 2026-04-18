"""In-process pub/sub for SSE. Single gevent worker only.

Works because all greenlets live in the same OS process and share the
module-level _subscribers set. If we ever scale horizontally, this has to be
replaced with Redis pub/sub or Postgres LISTEN/NOTIFY.
"""
import threading
from gevent.queue import Queue

_lock = threading.Lock()
_subscribers: set = set()
_seq: int = 0


def _next_seq() -> int:
    global _seq
    with _lock:
        _seq += 1
        return _seq


def get_current_seq() -> int:
    with _lock:
        return _seq


def subscribe() -> Queue:
    q: Queue = Queue()
    with _lock:
        _subscribers.add(q)
    return q


def unsubscribe(q: Queue) -> None:
    with _lock:
        _subscribers.discard(q)


def publish(event: dict) -> None:
    seq = _next_seq()
    event = {**event, "seq": seq}
    with _lock:
        targets = list(_subscribers)
    for q in targets:
        q.put_nowait(event)
