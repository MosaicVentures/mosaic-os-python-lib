from enum import Enum


# Statuses for the Live Pipeline in Prod Affinity
class ProdLivePipelineStatus(Enum):
    REACH_OUT = 2164897
    REACH_OUT_SENT = 3706932
    SCHEDULING_FIRST_MEETING = 2840461
    FIRST_MEETING = 119192
    DUE_DILIGENCE = 2185770
    IC = 2185769
    NEGOTIATION = 119199
    LEGAL = 119200
    PRE_MV_INVESTMENT = 329971
    CLOSED = 119201
    LOST = 119203
    DEAD_DEALS = 119204
    REJECTED = 316752
    OTHER = 119205
    BUILD_RELATIONSHIP = 2185476
    OFFER_MADE = 119199
    TRACK = 2185475
    HARD_TO_CRACK = 2787101


# Statuses for the Live Pipeline in Dev Affinity
class DevLivePipelineStatus(Enum):
    REACH_OUT = 8615723
    REACH_OUT_SENT = 8615722
    SCHEDULING_FIRST_MEETING = 8615725
    FIRST_MEETING = 8615724
    DUE_DILIGENCE = 8615726
    IC = 8615727
    NEGOTIATION = None
    LEGAL = 8615825
    PRE_MV_INVESTMENT = 8615728
    CLOSED = 8615729
    LOST = 8615826
    DEAD_DEALS = 8615827
    REJECTED = 8615828
    OTHER = 8615829
    BUILD_RELATIONSHIP = 8615831
    OFFER_MADE = 8615824
    TRACK = 8615730
    HARD_TO_CRACK = 8615830


# Last Meeting Type for Prod and Dev
class ProdLastMeetingType(Enum):
    INITIAL_REVIEW = 11173435
    PITCH_MEETING = 11173436
    FINAL_PITCH = 11173437
    DECISION = 11173438


class DevLastMeetingType(Enum):
    INITIAL_REVIEW = 10852610
    PITCH_MEETING = 10852611
    FINAL_PITCH = 10852612
    DECISION = 10852613


# Affinity config for Prod and Dev
affinity_config = {
    "prod": {
        "lp_list_id": 13926,
        "ecosystem_list_id": 10764,
        "lp_network_list_id": 165583,
        "lp_fields": [139981, 120060, 120059],
        "company_fields": [3542734],
        "lp_field_status": 139981,
        "lp_field_priority": 120060,
        "lp_field_owner": 120059,
        "lp_field_status_values": ProdLivePipelineStatus,
        "lp_field_last_meeting_type": 3913125,
        "lp_field_last_meeting_type_values": ProdLastMeetingType,
        "company_field_ec_flag": 3542734,
        "company_field_ec_flag_value_on": 9111690,
        "company_field_ec_flag_value_off": 9111706,
    },
    "dev": {
        "lp_list_id": 181518,
        "ecosystem_list_id": 216930,
        "lp_network_list_id": 218842,
        "lp_fields": [3443557, 3443561, 3443558],
        "company_fields": [3651213],
        "lp_field_status": 3443557,
        "lp_field_priority": 3443561,
        "lp_field_owner": 3443558,
        "lp_field_status_values": DevLivePipelineStatus,
        "lp_field_last_meeting_type": 3828813,
        "lp_field_last_meeting_type_values": DevLastMeetingType,
        "company_field_ec_flag": 3651213,
        "company_field_ec_flag_value_on": 9999246,
        "company_field_ec_flag_value_off": 9999247,
    },
}

# Scope for Google Calendar API
CALENDAR_SCOPES = ["https://www.googleapis.com/auth/calendar.events.readonly"]

# Affinity API base URL
AFFINITY_API_BASE_URL = "https://api.affinity.co"

# Statuses for the Live Pipeline that means it's an open opportunity
PIPELINE_STATUSES = [
    "REACH_OUT",
    "REACH_OUT_SENT",
    "SCHEDULING_FIRST_MEETING",
    "FIRST_MEETING",
    "DUE_DILIGENCE",
    "IC",
    "OFFER_MADE",
    "LEGAL",
]
