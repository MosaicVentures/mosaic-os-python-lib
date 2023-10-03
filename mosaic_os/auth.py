import json
from base64 import urlsafe_b64decode
from typing import Any


def decode_userinfo_from_header(header: str) -> dict[str, Any]:
    """Decode userinfo from header

    Args:
        header (str): X-Apigateway-Api-Userinfo header sent from API Gateway. See
            https://cloud.google.com/api-gateway/docs/authenticating-users-jwt#receiving_authenticated_results_in_your_api

    Returns:
        dict: Dictionary with keys from user's JWT token
    """
    user_info = urlsafe_b64decode(header + "=" * (4 - len(header) % 4))
    return json.loads(user_info)
