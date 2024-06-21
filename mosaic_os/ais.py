from datetime import datetime

from mosaic_os.models import ActionItem, ActionItemMetadata, CompanyBase, User
from mosaic_os.utils import combine_person_name


def affinity_reminder_to_ais(
    affinity_reminder: dict,
    source_system: str,
    event_type: str,
    updated_at: datetime = None,
    company: CompanyBase = None,
) -> ActionItem:
    return ActionItem(
        id=None,
        status=affinity_reminder["status"],
        content=affinity_reminder["content"],
        due_date=datetime.fromisoformat(affinity_reminder["due_date"]),
        creator=User(
            email=affinity_reminder["creator"]["primary_email"],
            name=combine_person_name(
                affinity_reminder["creator"]["first_name"], affinity_reminder["creator"]["last_name"]
            ),
            crm_id=affinity_reminder["creator"]["id"],
        ),
        completer=(
            User(
                email=affinity_reminder["completer"]["primary_email"],
                name=combine_person_name(
                    affinity_reminder["completer"]["first_name"], affinity_reminder["completer"]["last_name"]
                ),
                crm_id=affinity_reminder["completer"]["id"],
            )
            if affinity_reminder["completer"]
            else None
        ),
        owner=User(
            email=affinity_reminder["owner"]["primary_email"],
            name=combine_person_name(affinity_reminder["owner"]["first_name"], affinity_reminder["owner"]["last_name"]),
            crm_id=affinity_reminder["owner"]["id"],
        ),
        tagged_persons=(
            [
                User(
                    email=affinity_reminder["person"]["primary_email"],
                    name=combine_person_name(
                        affinity_reminder["person"]["first_name"], affinity_reminder["person"]["last_name"]
                    ),
                    crm_id=affinity_reminder["person"]["id"],
                )
            ]
            if affinity_reminder["person"]
            else []
        ),
        tagged_crm_opportunity_id=affinity_reminder["opportunity"]["id"] if affinity_reminder["opportunity"] else None,
        company=company,
        metadata=ActionItemMetadata(
            source_id=str(affinity_reminder["id"]),
            source=source_system,
            event_type=event_type,
            crm_reset_type=affinity_reminder["reset_type"],
        ),
        completed_at=(
            datetime.fromisoformat(affinity_reminder["completed_at"]) if affinity_reminder["completed_at"] else None
        ),
        created_at=datetime.fromisoformat(affinity_reminder["created_at"]),
        updated_at=updated_at,
    )
