#!/usr/bin/env python3
import os
import json
import requests

POSTMAN_API_BASE = "https://api.getpostman.com"

def get_headers(api_key):
    return {"X-Api-Key": api_key, "Content-Type": "application/json"}

def build_environment(name, base_url, api_key_value):
    return {
        "name": name,
        "values": [
            {"key": "base_url", "value": base_url, "enabled": True},
            {"key": "api_key", "value": api_key_value, "enabled": True},
        ],
    }

def build_simple_collection(name, base_url, endpoints):
    items = []
    for path in endpoints:
        items.append({
            "name": f"GET {path}",
            "request": {
                "method": "GET",
                "header": [{"key": "X-API-Key", "value": "{{api_key}}"}],
                "url": {
                    "raw": f"{{{{base_url}}}}{path}",
                    "host": ["{{base_url}}"],
                    "path": path.lstrip("/").split("/")
                }
            }
        })

    return {
        "info": {
            "name": name,
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        },
        "item": items
    }

def upsert_environment(api_key, workspace_id, env_payload):
    url = f"{POSTMAN_API_BASE}/environments?workspace={workspace_id}"
    resp = requests.post(url, headers=get_headers(api_key), json={"environment": env_payload})
    resp.raise_for_status()
    return resp.json()["environment"]["uid"]

def upsert_collection(api_key, workspace_id, coll_payload):
    url = f"{POSTMAN_API_BASE}/collections?workspace={workspace_id}"
    resp = requests.post(url, headers=get_headers(api_key), json={"collection": coll_payload})
    resp.raise_for_status()
    return resp.json()["collection"]["uid"]

def main():
    api_key = os.environ["POSTMAN_API_KEY"]
    workspace_id = os.environ["POSTMAN_WORKSPACE_ID"]

    customer = os.environ.get("CUSTOMER_NAME", "Customer")
    base_url = os.environ.get("BASE_URL", "https://api.example.com")
    api_key_value = os.environ.get("API_KEY_VALUE", "demo-key")
    endpoints = os.environ.get("ENDPOINTS", "/health,/users").split(",")

    env_name = f"{customer} – Demo Environment"
    coll_name = f"Enterprise – {customer} Demo Collection"

    print(f"🏗 Creating environment for {customer}")
    env_payload = build_environment(env_name, base_url, api_key_value)

    print(f"🏗 Creating collection for {customer}")
    coll_payload = build_simple_collection(coll_name, base_url, endpoints)

    env_uid = upsert_environment(api_key, workspace_id, env_payload)
    coll_uid = upsert_collection(api_key, workspace_id, coll_payload)

    print("✅ Demo setup complete")
    print(f"Environment UID: {env_uid}")
    print(f"Collection UID:  {coll_uid}")

if __name__ == "__main__":
    main()
