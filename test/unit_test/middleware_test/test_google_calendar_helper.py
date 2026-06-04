from datetime import datetime, timezone

from utils.value_object import GoogleCalendarHelper


def test_to_rfc3339_converts_naive_datetime_to_utc_string():
    value = datetime(2026, 3, 27, 10, 30, 0)

    assert GoogleCalendarHelper.to_rfc3339(value) == "2026-03-27T10:30:00Z"


def test_build_event_payload_includes_summary_and_time_window():
    start = datetime(2026, 3, 27, 10, 30, 0, tzinfo=timezone.utc)
    end = datetime(2026, 3, 27, 11, 0, 0, tzinfo=timezone.utc)

    payload = GoogleCalendarHelper.build_event_payload(
        summary="Corte de Cabelo - João (11999999999)",
        start=start,
        end=end,
        description="Estabelecimento: Barbearia Central",
    )

    assert payload["summary"] == "Corte de Cabelo - João (11999999999)"
    assert payload["start"]["dateTime"] == "2026-03-27T10:30:00Z"
    assert payload["end"]["dateTime"] == "2026-03-27T11:00:00Z"
    assert payload["description"] == "Estabelecimento: Barbearia Central"