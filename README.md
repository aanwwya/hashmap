# hashmap

a small event deduplication system built around a hashmap.

the idea is simple: when an event comes in, the system generates a fingerprint for it and uses that fingerprint as a hashmap key. if the same event shows up again within the ttl window, it gets marked as a duplicate.

## how it works

```text
event
  ↓
validate
  ↓
canonical json
  ↓
sha-256 fingerprint
  ↓
hashmap lookup
  ↓
ttl check
  ↓
accepted / duplicate
```

the hashmap stores:

```text
fingerprint → timestamp
```

so the system doesn't need to keep the entire event around just to check whether it has already been seen.

## example

send:

```json
{
  "user_id": 42,
  "action": "purchase"
}
```

first time:

```text
accepted
```

send the same event again within the ttl:

```text
duplicate
```

different event:

```json
{
  "user_id": 42,
  "action": "refund"
}
```

is treated separately.

## fingerprinting

events are converted into deterministic json before being hashed:

```python
json.dumps(event.model_dump(), sort_keys=True)
```

the sorted keys make the representation consistent even when the fields arrive in a different order.

the resulting data is hashed using sha-256 to produce the fingerprint used as the hashmap key.

## ttl

each fingerprint has a limited lifetime.

once the ttl expires, the fingerprint is removed and the same event can be accepted again.

this prevents old events from staying in memory forever.

## concurrency

the hashmap is shared mutable state, so access is protected with a `threading.lock`.

the check-and-store operation happens under the same lock so concurrent requests cannot both see the same event as new.

## api

the project includes a small fastapi interface.

### `post /events`

accepts an event and returns whether it was accepted or considered a duplicate.

example:

```json
{
  "user_id": 42,
  "action": "purchase"
}
```

### `get /stats`

returns basic runtime statistics:

```json
{
  "active_events": 1,
  "accepted": 2,
  "duplicates": 1
}
```

the interactive api documentation is available through fastapi's `/docs` endpoint when the server is running.

## running it

start the api with:

```bash
uvicorn api:app --reload
```

then open:

```text
http://127.0.0.1:8000/docs
```

## testing

run:

```bash
pytest
```

the test suite covers:

* new events
* duplicate events
* different events
* ttl expiration
* concurrent duplicate checks
* api validation
* api responses
* statistics

## project structure

```text
hashmap/
├── api.py
├── deduplicator.py
├── main.py
├── test_api.py
├── test_deduplicator.py
├── README.md
└── .gitignore
```

## stack

* python
* fastapi
* pydantic
* pytest
* sha-256
* python dictionary

## tradeoffs

the current implementation keeps state in memory.

this keeps the implementation small and makes the hashmap behavior easy to see, but the state is lost when the process restarts and isn't shared between multiple application instances.

a distributed implementation could move the state into something like redis, but that would introduce another layer of networking, consistency, and concurrency concerns.

for this project, the in-memory approach is intentional. the point is to understand the data structure and the system built around it rather than hide the core logic behind an external datastore.
