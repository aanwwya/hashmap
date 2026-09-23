import threading
import time

from deduplicator import Deduplicator


def test_new_event_is_accepted():
    deduplicator = Deduplicator(ttl=60)

    result = deduplicator.check("event-1")

    assert result["duplicate"] is False
    assert result["status"] == "accepted"


def test_same_event_is_duplicate():
    deduplicator = Deduplicator(ttl=60)

    deduplicator.check("event-1")
    result = deduplicator.check("event-1")

    assert result["duplicate"] is True
    assert result["status"] == "duplicate"


def test_different_events_are_not_duplicates():
    deduplicator = Deduplicator(ttl=60)

    deduplicator.check("event-1")
    result = deduplicator.check("event-2")

    assert result["duplicate"] is False
    assert result["status"] == "accepted"


def test_event_expires_after_ttl():
    deduplicator = Deduplicator(ttl=1)

    deduplicator.check("event-1")

    time.sleep(1.1)

    result = deduplicator.check("event-1")

    assert result["duplicate"] is False
    assert result["status"] == "accepted"


def test_concurrent_duplicate_checks():
    deduplicator = Deduplicator(ttl=60)

    results = []

    def check_event():
        result = deduplicator.check("same-event")
        results.append(result["duplicate"])

    threads = [
        threading.Thread(target=check_event)
        for _ in range(20)
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    assert results.count(False) == 1
    assert results.count(True) == 19