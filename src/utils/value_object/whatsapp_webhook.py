from __future__ import annotations

from datetime import datetime, timedelta

from config.db import Session
from domain.entities import Context, TaskQueue
from infra.repository import ContextRepository, EstablishmentRepository, TaskQueueRepository
from middleware.task_queue import TaskQueueFactory


class WhatsappWebhookHelper:

    @staticmethod
    def extract_message(payload: dict) -> dict | None:
        entries = payload.get("entry") or []
        for entry in entries:
            changes = entry.get("changes") or []
            for change in changes:
                value = change.get("value") or {}
                metadata = value.get("metadata") or {}
                messages = value.get("messages") or []
                if not messages:
                    continue

                message = messages[0]
                text = (message.get("text") or {}).get("body")
                sender = message.get("from")
                phone_number_id = metadata.get("phone_number_id")
                message_id = message.get("id")

                if text and sender and phone_number_id:
                    return {
                        "phone_number_id": phone_number_id,
                        "sender": sender,
                        "message": text,
                        "message_id": message_id,
                    }

        return None

    @staticmethod
    def _build_context(*, establishments_id: int, phone_number: str, message_id: str | None) -> Context:
        now = datetime.now()
        return Context(
            id=None,
            establishments_id=establishments_id,
            customers_id=None,
            phone_number=phone_number,
            last_message_id=message_id,
            context_arrow=None,
            is_open=True,
            context_data={},
            created_at=now,
            updated_at=now,
            expires_at=now + timedelta(days=1),
        )

    @staticmethod
    def _upsert_context(session, *, establishments_id: int, sender: str, message_id: str | None) -> Context:
        context_repository = ContextRepository(session)
        context = context_repository.get_open_by_phone_number(sender, establishments_id)

        if context is None:
            context = WhatsappWebhookHelper._build_context(
                establishments_id=establishments_id,
                phone_number=sender,
                message_id=message_id,
            )
            return context_repository.create(context)

        context.last_message_id = message_id
        context.is_open = True
        return context_repository.update(context)

    @staticmethod
    def enqueue_process_message(payload: dict, session=None) -> TaskQueue | None:
        message_data = WhatsappWebhookHelper.extract_message(payload)
        if message_data is None:
            return None

        own_session = session is None
        db_session = session or Session()

        try:
            establishment_repository = EstablishmentRepository(db_session)
            establishment_internal_id = establishment_repository.get_internal_id_by_chatbot_phone_number(
                message_data["phone_number_id"]
            )

            if establishment_internal_id is None:
                return None

            context = WhatsappWebhookHelper._upsert_context(
                db_session,
                establishments_id=establishment_internal_id,
                sender=message_data["sender"],
                message_id=message_data.get("message_id"),
            )

            task = TaskQueueFactory.process_message(context, message_data["message"])
            return TaskQueueRepository(db_session).create(task)
        finally:
            if own_session:
                db_session.close()