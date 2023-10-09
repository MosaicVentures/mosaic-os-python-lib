import json
import logging
from datetime import datetime
from os import environ
from uuid import uuid4

from google.cloud.datastore import Client, Entity
from google.oauth2 import service_account
from googleapiclient.discovery import build

from mosaic_os.constants import CALENDAR_SCOPES

logger = logging.getLogger(__name__)

db = Client()


def get_calendar_service(user_email: str):
    """Get a calendar service for a specific user

    Note: This requires a service account with domain-wide delegation enabled and service account JSON
    credentials stored in the environment variable `CALENDAR_SERVICE_ACCOUNT`.

    Args:
        user_email (str): Email address of user

    Returns:
        A Resource object with methods for interacting with the service.
    """
    source_credentials = service_account.Credentials.from_service_account_info(
        json.loads(environ["CALENDAR_SERVICE_ACCOUNT"]), scopes=CALENDAR_SCOPES
    )
    updated_credentials = source_credentials.with_subject(user_email)
    return build("calendar", "v3", credentials=updated_credentials)


def subscribe_channel(calendar_id: str):
    """Subscribe to a calendar

    Note: Environment variables `WEBHOOK_TOKEN` and `WEBHOOK_URL` must be set.

    Args:
        calendar_id (str): Calendar ID to subscribe to which is the email address of the calendar
    """
    logger.info(f"Subscribing to calendar {calendar_id}")
    calendar_service = get_calendar_service(calendar_id)

    # generate a unique ID for this subscription
    webhook_id = str(uuid4())
    body = {
        "id": webhook_id,
        "type": "web_hook",
        "token": environ["WEBHOOK_TOKEN"],
        "address": environ["WEBHOOK_URL"],  # the URL of your webhook
    }

    # Make the watch request
    data = calendar_service.events().watch(calendarId=calendar_id, body=body).execute()
    set_webhook_calendar(webhook_id, calendar_id, data)


def set_webhook_calendar(webhook_id: str, calendar_id: str, data) -> Entity:
    key = db.key("CalendarWebhook", calendar_id)
    entity = db.get(key) or Entity(key=key)
    if "created" not in entity:
        entity["created"] = datetime.utcnow().isoformat()
    entity["calendar_id"] = calendar_id
    entity["webhook_id"] = webhook_id
    for key, value in data.items():
        entity[f"_{key}"] = value
    # set expiry to int
    entity["_expiration"] = int(entity["_expiration"])
    db.put(entity)
    return entity
