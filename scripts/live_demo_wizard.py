#!/usr/bin/env python3
import os
import json
import requests
from typing import Dict, Any

POSTMAN_API_BASE = "https://api.getpostman.com"


def get_headers(api_key: str):
    return {"X-Api-Key": api_key, "Content-Type": "application/json"}


def build_environment(name: str, base_url: str, api_key_value: str) -> Dict[str, Any]:
    return {
        "name": name,
        "values": [
            {"key": "base_url", "value": base_url, "enabled": True},
            {"key": "api_key", "value": api_key_value, "enabled": True},
        ],
    }


def build_simple_collection(name: str, base_url: str, endpoints: list[str]) -> Dict[str, Any]:
    items = []
    for path in endpoints:
        items.append(
            {
                "name": f"GET {path}",
                "request": {
                    "method": "GET",
                    "header": [{"key": "X-API-Key", "value": "{{api_key}}"}],
                    "url": {
                        "raw": f"{{{{base_url}}}}{path}",
                        "host": ["{{base_url}}"],
                        "path": [p for p in path.lstrip("/").split("/")],
                    },
                },
            }
        )

    return {
        "info": {
            "name": name,
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
        },
        "item": items,
    }


def build_collection_from_openapi(
    api_key: str, workspace_id: str, name: str, openapi_url_or_path: str
) -> Dict[str, Any]:
    # Accept either URL or local file path
    if openapi_url_or_path.startswith("http"):
        resp = requests.get(openapi_url_or_path)
        resp.raise_for_status()
        spec_content = resp.text
    else:
        with open(openapi_url_or_path, "r", encoding="utf-8") as f:
            spec_content = f.read()

    url = f"{POSTMAN_API_BASE}/import/openapi?workspace={workspace_id}"
    payload = {
        "type": "string",
        "input": spec_content,
        "name": name,
    }
    resp = requests.post(url, headers=get_headers(api_key), json=payload)
    resp.raise_for_status()
    data = resp.json()
    return data.get("collections", [])[0]["collection"]


def upsert_environment(api_key: str, workspace_id: str, env_payload: Dict[str, Any]) -> str:
    url = f"{POSTMAN_API_BASE}/environments?workspace={workspace_id}"
    resp = requests.post(url, headers=get_headers(api_key), json={"environment": env_payload})
    resp.raise_for_status()
    return resp.json()["environment"]["uid"]


def upsert_collection(api_key: str, workspace_id: str, coll_payload: Dict[str, Any]) -> str:
    url = f"{POSTMAN_API_BASE}/collections?workspace={workspace_id}"
    resp = requests.post(url, headers=get_headers(api_key), json={"collection": coll_payload})
    resp.raise_for_status()
    return resp.json()["collection"]["uid"]


def main():
    # Reuse your existing env vars for auth/workspace
    api_key = os.environ["POSTMAN_API_KEY"]
    workspace_id = os.environ["POSTMAN_WORKSPACE_ID"]

    print("🧙 Live Demo Wizard – Postman Enterprise Sync")
    customer_name = input("Customer / project name (e.g., Acme Freight): ").strip() or "Customer Demo"
    env_name = f"{customer_name} – Demo Environment"
    coll_name = f"Enterprise – {customer_name} Demo Collection"

    base_url = input("Base API URL (e.g., https://api.acme.com): ").strip() or "https://api.example.com"
    api_key_value = (
        input("Sample API key or token placeholder (optional, press Enter for 'demo-key'): ").strip() or "demo-key"
    )

    use_openapi = input("Do you have an OpenAPI spec? (y/N): ").strip().lower() == "y"

    if use_openapi:
        openapi_source = input("OpenAPI URL or local path: ").strip()
    else:
        openapi_source = None

    endpoints: list[str] = []
    if not use_openapi:
        print("Enter 1–3 key endpoint paths (e.g., /health, /users). Leave blank to finish.")
        while True:
            p = input("Endpoint path: ").strip()
            if not p:
                break
            if not p.startswith("/"):
                p = "/" + p
            endpoints.append(p)
        if not endpoints:
            endpoints = ["/health"]

    print("\n🔧 Building environment...")
    env_payload = build_environment(env_name, base_url, api_key_value)

    print("🔧 Building collection...")
    if use_openapi and openapi_source:
        coll_payload = build_collection_from_openapi(api_key, workspace_id, coll_name, openapi_source)
    else:
        coll_payload = build_simple_collection(coll_name, base_url, endpoints)

    print("\n📤 Creating environment in Postman...")
    env_uid = upsert_environment(api_key, workspace_id, env_payload)

    print("📤 Creating collection in Postman...")
    coll_uid = upsert_collection(api_key, workspace_id, coll_payload)

    ids = {"environment_uid": env_uid, "collection_uid": coll_uid}
    with open("postman_ids_live_demo.json", "w", encoding="utf-8") as f:
        json.dump(ids, f)

    print("\n✅ Done.")
    print(f"Environment created: {env_name} (UID: {env_uid})")
    print(f"Collection created:  {coll_name} (UID: {coll_uid})")
    print("You can now refresh the workspace in Postman and demo against their real-ish setup.")



if __name__ == "__main__":
    main()
