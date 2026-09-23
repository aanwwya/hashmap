import threading
import time


class Deduplicator:
    def __init__(self, ttl):
        self.ttl = ttl
        self.events = {}
        self.accepted = 0
        self.duplicates = 0
        self.lock = threading.Lock()

    def _cleanup(self, now):
        expired = []

        for fingerprint, timestamp in self.events.items():
            if now - timestamp >= self.ttl:
                expired.append(fingerprint)

        for fingerprint in expired:
            del self.events[fingerprint]

    def check(self, fingerprint):
        with self.lock:
            now = time.time()

            self._cleanup(now)

            if fingerprint in self.events:
                age = now - self.events[fingerprint]

                self.duplicates += 1

                return {
                    "duplicate": True,
                    "age": age,
                    "status": "duplicate"
                }

            self.events[fingerprint] = now
            self.accepted += 1

            return {
                "duplicate": False,
                "age": 0,
                "status": "accepted"
            }

    def stats(self):
        with self.lock:
            self._cleanup(time.time())

            return {
                "active_events": len(self.events),
                "accepted": self.accepted,
                "duplicates": self.duplicates
            }