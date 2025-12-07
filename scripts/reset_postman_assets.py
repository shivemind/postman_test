#!/usr/bin/env python3
import os
import requests

POSTMAN_API_BASE = "https://api.getpostman.com"


def get_headers(api_key: str):
    return {"X-Api-Key": api_key, "Content-Type": "application/json"}


def list_environments(api_key: str, workspace_id: str):
    url = f"{POSTMAN_API_BASE}/environments?workspace={workspace_id}"
    resp = requests.get(url, headers=get_headers(api_key))
    resp.raise_for_status()
    return resp.json().get("environments", [])


def list_collections(api_key: str, workspace_id: str):
    url = f"{POSTMAN_API_BASE}/collections?workspace={workspace_id}"
    resp = requests.get(url, headers=get_headers(api_key))
    resp.raise_for_status()
    return resp.json().get("collections", [])


def delete_environment(api_key: str, uid: str, name: str):
    url = f"{POSTMAN_API_BASE}/environments/{uid}"
    print(f"🗑 Deleting environment: {name} ({uid})")
    resp = requests.delete(url, headers=get_headers(api_key))
    # Don't blow up the whole job if one delete fails
    try:
        resp.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"   ⚠ Failed to delete environment {name}: {e}")


def delete_collection(api_key: str, uid: str, name: str):
    url = f"{POSTMAN_API_BASE}/collections/{uid}"
    print(f"🗑 Deleting collection: {name} ({uid})")
    resp = requests.delete(url, headers=get_headers(api_key))
    try:
        resp.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"   ⚠ Failed to delete collection {name}: {e}")


def is_demo_env(name: str) -> bool:
    """Define what counts as a 'demo' environment."""
    lowered = name.lower()
    return (
        "demo environment" in lowered
        or "– demo environment" in lowered
        or " - demo environment" in lowered
    )


def is_demo_collection(name: str) -> bool:
    """Define what counts as a 'demo' collection."""
    lowered = name.lower()
    return (
        lowered.startswith("enterprise –")
        or lowered.startswith("enterprise -")
        or "demo collection" in lowered
    )


def main():
    api_key = os.environ["POSTMAN_API_KEY"]
    workspace_id = os.environ["POSTMAN_WORKSPACE_ID"]

    print("🔁 Postman Demo Reset – starting…")
    print(f"Workspace: {workspace_id}")

    # Environments
    envs = list_environments(api_key, workspace_id)
    demo_envs = [e for e in envs if is_demo_env(e.get("name", ""))]

    if not demo_envs:
        print("No demo environments found to delete.")
    else:
        for e in demo_envs:
            delete_environment(api_key, e["uid"], e["name"])

    # Collections
    colls = list_collections(api_key, workspace_id)
    demo_colls = [c for c in colls if is_demo_collection(c.get("name", ""))]

    if not demo_colls:
        print("No demo collections found to delete.")
    else:
        for c in demo_colls:
            delete_collection(api_key, c["uid"], c["name"])

    print("✅ Demo reset script complete.")


if __name__ == "__main__":
    main()
