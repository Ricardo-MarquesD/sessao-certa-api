from __future__ import annotations

from datetime import datetime, timezone


class GoogleCalendarHelper:

    @staticmethod
    def to_rfc3339(value: datetime) -> str:
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)

        return value.isoformat().replace("+00:00", "Z")

    @staticmethod
    def build_event_summary(*, service_name: str, customer_name: str, phone_number: str) -> str:
        return f"{service_name} - {customer_name} ({phone_number})"

    @staticmethod
    def build_event_payload(*, summary: str, start: datetime, end: datetime, description: str | None = None, timezone_name: str = "UTC") -> dict:
        payload = {
            "summary": summary,
            "start": {
                "dateTime": GoogleCalendarHelper.to_rfc3339(start),
                "timeZone": timezone_name,
            },
            "end": {
                "dateTime": GoogleCalendarHelper.to_rfc3339(end),
                "timeZone": timezone_name,
            },
        }

        if description:
            payload["description"] = description

        return payload

    @staticmethod
    def build_description(
        *,
        establishment_name: str,
        employee_name: str | None = None,
        service_name: str | None = None,
        customer_name: str | None = None,
        phone_number: str | None = None,
    ) -> str:
        parts = [f"Estabelecimento: {establishment_name}"]

        if employee_name:
            parts.append(f"Funcionário: {employee_name}")

        if service_name:
            parts.append(f"Serviço: {service_name}")

        if customer_name:
            parts.append(f"Cliente: {customer_name}")

        if phone_number:
            parts.append(f"Telefone: {phone_number}")

        return "\n".join(parts)