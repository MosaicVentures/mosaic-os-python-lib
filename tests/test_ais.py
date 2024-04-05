from datetime import datetime

from mosaic_os.ais import affinity_reminder_to_ais
from mosaic_os.crm import AffinityReminderResetType
from mosaic_os.models import ActionItemStatus, CompanyBase


def test_affinity_reminder_to_ais_success():
    affinity_reminder = {
        "id": 15562,
        "type": 1,
        "created_at": "2021-11-22T09:31:52.415-08:00",
        "completed_at": None,
        "content": "Recurring reminder",
        "due_date": "2021-12-22T09:31:52.415-08:00",
        "reset_type": 0,
        "reminder_days": 30,
        "status": 2,
        "creator": {
            "id": 443,
            "type": 1,
            "first_name": "John",
            "last_name": "Doe",
            "primary_email": "john@affinity.co",
            "emails": ["john@affinity.co"],
        },
        "owner": {
            "id": 443,
            "type": 1,
            "first_name": "John",
            "last_name": "Doe",
            "primary_email": "john@affinity.co",
            "emails": ["john@affinity.co"],
        },
        "completer": None,
        "person": None,
        "organization": {
            "id": 4904,
            "name": "organization",
            "domain": None,
            "domains": [],
            "crunchbase_uuid": None,
            "global": False,
        },
        "opportunity": None,
    }

    action_item = affinity_reminder_to_ais(
        affinity_reminder,
        "urn:mosaic-os:service:webhook:affinity",
        "REMIMDER.CREATED",
        company=CompanyBase(
            id=97403,
            name="organization",
            primary_domain="organization.com",
            domains=["organization.com"],
            sp_id="1234",
            crm_id="5678",
        ),
    )

    assert action_item.id is None
    assert action_item.status == ActionItemStatus.OVERDUE
    assert action_item.content == "Recurring reminder"
    assert isinstance(action_item.due_date, datetime)
    assert action_item.creator.email == "john@affinity.co"
    assert action_item.creator.name == "John Doe"
    assert action_item.creator.crm_id == 443
    assert action_item.completer is None
    assert action_item.owner.email == "john@affinity.co"
    assert action_item.owner.name == "John Doe"
    assert action_item.owner.crm_id == 443
    assert not len(action_item.tagged_persons)
    assert action_item.company.id == 97403
    assert action_item.company.name == "organization"
    assert action_item.company.primary_domain == "organization.com"
    assert action_item.company.domains == ["organization.com"]
    assert action_item.company.sp_id == "1234"
    assert action_item.company.crm_id == "5678"
    assert action_item.metadata.source_id == "15562"
    assert action_item.metadata.source == "urn:mosaic-os:service:webhook:affinity"
    assert action_item.metadata.event_type == "REMIMDER.CREATED"
    assert action_item.metadata.crm_reset_type == AffinityReminderResetType.INTERACTION
