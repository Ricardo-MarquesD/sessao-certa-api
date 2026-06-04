import httplib2

from googleapiclient.errors import HttpError

from infra.google_calendar.adapter import BackoffPolicy, GoogleCalendarAdapter


class FakeRequest:
    def __init__(self, response):
        self._response = response

    def execute(self):
        return self._response


class FakeEvents:
    def __init__(self):
        self.calls = []
        self._page = 0

    def list(self, **kwargs):
        self.calls.append(kwargs)
        self._page = 1
        return FakeRequest({"items": [{"id": "evt-1"}], "nextPageToken": "next"})

    def list_next(self, previous_request, previous_response):
        if previous_response.get("nextPageToken") and self._page == 1:
            self._page = 2
            return FakeRequest({"items": [{"id": "evt-2"}]})
        return None


class FakeService:
    def __init__(self, events):
        self._events = events

    def events(self):
        return self._events


def test_backoff_retries_on_quota_errors(monkeypatch):
    attempts = {"count": 0}

    def flaky_request():
        attempts["count"] += 1
        if attempts["count"] < 3:
            response = httplib2.Response({"status": "429", "reason": "Too Many Requests"})
            response.status = 429
            response.reason = "Too Many Requests"
            raise HttpError(response, b"quota")
        return {"ok": True}

    monkeypatch.setattr("infra.google_calendar.adapter.time.sleep", lambda *_: None)

    policy = BackoffPolicy(max_attempts=3, base_delay=0.0, max_delay=0.0)
    result = policy.execute(flaky_request)

    assert result == {"ok": True}
    assert attempts["count"] == 3


def test_list_events_uses_fields_and_paginates():
    events_api = FakeEvents()
    adapter = GoogleCalendarAdapter(FakeService(events_api))

    events = adapter.list_events(
        calendar_id="primary",
        fields="items(id),nextPageToken",
    )

    assert events == [{"id": "evt-1"}, {"id": "evt-2"}]
    assert events_api.calls[0]["fields"] == "items(id),nextPageToken"
