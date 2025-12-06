#!/usr/bin/env python3
import os
import requests
import sys
from typing import Optional

POSTMAN_API_BASE = "https://api.getpostman.com"


def get_headers(api_key: str):
    return {"X-Api-Key": api_key, "Content-Type": "application/json"}


def find_collection_uid_by_name(api_key: str, workspace_id: str, name: str) -> Optional[str]:
    url = f"{POSTMAN_API_BASE}/collections?workspace={workspace_id}"
    resp = requests.get(url, headers=get_headers(api_key))
    resp.raise_for_status()
    data = resp.json()
    for c in data.get("collections", []):
        if c.get("name") == name:
            return c.get("uid")
    return None


def find_environment_uid_by_name(api_key: str, workspace_id: str, name: str) -> Optional[str]:
    url = f"{POSTMAN_API_BASE}/environments?workspace={workspace_id}"
    resp = requests.get(url, headers=get_headers(api_key))
    resp.raise_for_status()
    data = resp.json()
    for e in data.get("environments", []):
        if e.get("name") == name:
            return e.get("uid")
    return None


def delete_collection(api_key: str, uid: str):
    url = f"{POSTMAN_API_BASE}/collections/{uid}"
    resp = requests.delete(url, headers=get_headers(api_key))
    if resp.status_code not in (200, 202, 204):
        print(f"Warning: deleting collection {uid} returned {resp.status_code}: {resp.text}", file=sys.stderr)
    else:
        print(f"Deleted collection UID: {uid}")


def delete_environment(api_key: str, uid: str):
    url = f"{POSTMAN_API_BASE}/environments/{uid}"
    resp = requests.delete(url, headers=get_headers(api_key))
    if resp.status_code not in (200, 202, 204):
        print(f"Warning: deleting environment {uid} returned {resp.status_code}: {resp.text}", file=sys.stderr)
    else:
        print(f"Deleted environment UID: {uid}")


def main():
    api_key = os.environ["POSTMAN_API_KEY"]
    workspace_id = os.environ["POSTMAN_WORKSPACE_ID"]

    env_name = os.environ.get("ENV_NAME", "Enterprise Demo Environment")
    coll_name = os.environ.get("COLLECTION_NAME", "Enterprise Demo Collection")

    print(f"Looking for environment named: {env_name}")
    env_uid = find_environment_uid_by_name(api_key, workspace_id, env_name)
    if env_uid:
        delete_environment(api_key, env_uid)
    else:
        print("No matching environment found; nothing to delete.")

    print(f"Looking for collection named: {coll_name}")
    coll_uid = find_collection_uid_by_name(api_key, workspace_id, coll_name)
    if coll_uid:
        delete_collection(api_key, coll_uid)
    else:
        print("No matching collection found; nothing to delete.")

    print("Reset complete.")


if __name__ == "__main__":
    main()
