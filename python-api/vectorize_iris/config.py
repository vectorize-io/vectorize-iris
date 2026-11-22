"""
Where the client sends requests: the API root that /files and /extraction hang off.
"""

import os
from typing import Optional, Tuple

from vectorize_iris.exceptions import VectorizeIrisError

DEFAULT_API_URL = "https://api.vectorize.io"


def resolve(
    api_token: Optional[str],
    org_id: Optional[str],
    base_url: Optional[str],
) -> Tuple[str, str]:
    """
    Return (api_token, base_url) from the arguments, falling back to the environment.

    With a base URL (argument or VECTORIZE_IRIS_BASE_URL), requests go to it as given and no
    organization ID is needed: Hindsight Inference takes the organization from the key, e.g.
    base_url="https://inference.hindsight.vectorize.io/v1". Without one, requests go to
    https://api.vectorize.io/v1/org/{org_id}, which needs VECTORIZE_ORG_ID.
    """
    api_token = api_token or os.getenv("VECTORIZE_TOKEN")
    base_url = base_url or os.getenv("VECTORIZE_IRIS_BASE_URL")
    if base_url:
        if not api_token:
            raise VectorizeIrisError(
                "Missing credentials. Set VECTORIZE_TOKEN or pass api_token."
            )
        return api_token, base_url.rstrip("/")

    org_id = org_id or os.getenv("VECTORIZE_ORG_ID")
    if not api_token or not org_id:
        raise VectorizeIrisError(
            "Missing credentials. Set VECTORIZE_TOKEN and VECTORIZE_ORG_ID "
            "environment variables or pass them as parameters."
        )
    return api_token, f"{DEFAULT_API_URL}/v1/org/{org_id}"
