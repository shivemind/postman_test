import os
import requests
import json
from typing import Dict, Any

POSTMAN_API_BASE_URL = "https://api.getpostman.com"

def build_environment(name: str) -> Dict[str, Any]:
    """Builds a Postman environment configuration."""

    base_url = os.environ.get("SERVICE_BASE_URL", "https://api.example.com")
    api_key = os.environ.get("SERVICE_API_KEY", "dummy-api-key")

    env_payload = {
        "name": name,
        "values": [
            {
                "key": "base_url",
                "value": base_url,
                "enabled": True
            },
            {
                "key": "api_key",
                "value": api_key,
                "enabled": True
            }
        ]               
    }

    return env_payload


    def build_collection(name: str) -> Dict[str, Any]:
        """Builds a Postman collection configuration."""

        collection_payload = {
            "info": {
                "name": name,
                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
            },
            "item": [
                {
                    "name": "Health Check",
                    "request": {
                        "method": "GET",
                        "header": [
                            {
                                "key": "X-API-KEY",
                                "value": "{{api_key}}",
                                
                            }
                        ],
                        "url": {
                            "raw": f"{{base_url}}/health",
                            "host": ["base_url"],
                            "path": ["health"]
                        }
                    }
                },
                {
                    "name" : "Get Users",
                    "request": {
                        "method": "GET",
                        "header": [
                            {
                                "key": "X-API-KEY",
                                "value": "{{api_key}}",
                                "type": "text"
                            }
                        ],
                        "url": {
                            "raw": f"{{base_url}}/users",
                            "host": ["base_url_var"],
                            "path": ["users"]
                        }
                    }
                }
            ]
        }

        return collection_payload

def upsert_collection(api_key: str, workspace_id: str, coll_payload: Dict[str, Any]) -> str:
    """
    Create or update a collection in Postman.
    If POSTMAN_COLLECTION_UID is set, update that collection; otherwise create a new one.
    """
    headers = {"X-Api-Key": api_key, "Content-Type": "application/json"}

    coll_uid = os.environ.get("POSTMAN_COLLECTION_UID")
    if coll_uid:
        print(f"Updating existing Postman collection: {coll_uid}")
        url = f"{POSTMAN_API_BASE}/collections/{coll_uid}"
        body = {"collection": coll_payload}
        resp = requests.put(url, headers=headers, json=body)
    else:
        print("Creating new Postman collection")
        url = f"{POSTMAN_API_BASE}/collections?workspace={workspace_id}"
        body = {"collection": coll_payload}
        resp = requests.post(url, headers=headers, json=body)

    resp.raise_for_status()
    data = resp.json()
    new_uid = data["collection"]["uid"]
    print(f"Collection UID: {new_uid}")
    return new_uid

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

    print("Upserting environment in Postman...")
    env_uid = upsert_environment(api_key, workspace_id, env_payload)

    print("Upserting collection in Postman...")
    coll_uid = upsert_collection(api_key, workspace_id, coll_payload)

    print("Done.")
    print(f"Environment UID: {env_uid}")
    print(f"Collection UID: {coll_uid}")


if __name__ == "__main__":
    main()
