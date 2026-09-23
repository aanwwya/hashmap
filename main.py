import hashlib
import json

from deduplicator import Deduplicator


deduplicator = Deduplicator(ttl=60)


while True:
    user_id = input("user id: ")
    action = input("action: ")

    event = {
        "user_id": user_id,
        "action": action,
    }

    event_data = json.dumps(event, sort_keys=True)
    fingerprint = hashlib.sha256(event_data.encode()).hexdigest()

    result = deduplicator.check(fingerprint)

    print(result["status"])