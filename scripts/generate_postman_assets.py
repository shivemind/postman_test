#!/usr/bin/env python3
import os
import requests
import json
from typing import Dict, Any

POSTMAN_API_BASE = "https://api.getpostman.com"


def build_environment(name: str) -> Dict[str, Any]:
    """
    Build a Postman environment JSON from environment variables.
    """
    base_url = os.environ.get("SERVICE_BASE_URL", "https://api.example.com")
    api_key = os.environ.get("SERVICE_API_KEY", "demo-key")

    return {
        "name": name,
        "values": [
            {"key": "base_url", "value": base_url, "enabled": True},
            {"key": "api_key", "value": api_key, "enabled": True},
        ],
    }


def build_collection(name: str) -> Dict[str, Any]:
    """
    Build a minimal Postman Collection for demo purposes.
    """
    base_url_var = "{{base_url}}"

    return {
        "info": {
            "name": name,
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
        },
        "item": [
            {
                "name": "Health Check",
                "request": {
                    "method": "GET",
                    "header": [{"key": "X-API-Key", "value": "{{api_key}}"}],
                    "url": {
                        "raw": f"{base_url_var}/health",
                        "host": [base_url_var],
                        "path": ["health"],
                    },
                },
            },
            {
                "name": "Get Users",
                "request": {
                    "method": "GET",
                    "header": [{"key": "X-API-Key", "value": "{{api_key}}"}],
                    "url": {
                        "raw": f"{base_url_var}/users",
                        "host": [base_url_var],
                        "path": ["users"],
                    },
                },
            },
        ],
    }


def upsert_environment(api_key: str, workspace_id: str, env_payload: Dict[str, Any]) -> str:
    headers = {"X-Api-Key": api_key, "Content-Type": "application/json"}
    env_uid = os.environ.get("POSTMAN_ENV_UID")

    if env_uid:
        url = f"{POSTMAN_API_BASE}/environments/{env_uid}"
        resp = requests.put(url, headers=headers, json={"environment": env_payload})
    else:
        url = f"{POSTMAN_API_BASE}/environments?workspace={workspace_id}"
        resp = requests.post(url, headers=headers, json={"environment": env_payload})

    resp.raise_for_status()
    return resp.json()["environment"]["uid"]


def upsert_collection(api_key: str, workspace_id: str, coll_payload: Dict[str, Any]) -> str:
    headers = {"X-Api-Key": api_key, "Content-Type": "application/json"}
    coll_uid = os.environ.get("POSTMAN_COLLECTION_UID")

    if coll_uid:
        url = f"{POSTMAN_API_BASE}/collections/{coll_uid}"
        resp = requests.put(url, headers=headers, json={"collection": coll_payload})
    else:
        url = f"{POSTMAN_API_BASE}/collections?workspace={workspace_id}"
        resp = requests.post(url, headers=headers, json={"collection": coll_payload})

    resp.raise_for_status()
    return resp.json()["collection"]["uid"]


def main():
    api_key = os.environ["POSTMAN_API_KEY"]
    workspace_id = os.environ["POSTMAN_WORKSPACE_ID"]

    env_name = os.environ.get("ENV_NAME", "Enterprise Demo Environment")
    coll_name = os.environ.get("COLLECTION_NAME", "Enterprise Demo Collection")

    print("Building environment payload...")
    env_payload = build_environment(env_name)
    print(json.dumps(env_payload, indent=2))

    print("Building collection payload...")
    coll_payload = build_collection(coll_name)
    print(json.dumps(coll_payload, indent=2))

    print("Upserting environment...")
    env_uid = upsert_environment(api_key, workspace_id, env_payload)

    print("Upserting collection...")
    coll_uid = upsert_collection(api_key, workspace_id, coll_payload)

    print("Done.")
    print(f"Environment UID: {env_uid}")
    print(f"Collection UID: {coll_uid}")


if __name__ == "__main__":
    main()
