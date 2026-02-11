#!/usr/bin/env python3
"""
Add Webhook triggers to n8n workflows so they can be triggered externally.

Workflows:
  1. Veo3 5x8초 (tS2hcoeJ4ar8hivm) -> webhook path: lumix-veo3-trigger
  2. v3 (9YOHS8N1URWlzGWj)          -> webhook path: lumix-v3-trigger

Each webhook:
  - GET method
  - responseMode: onReceived (respond immediately with 200)
  - Connected to the same first node that the manual trigger connects to
"""

import json
import requests
import uuid

API_BASE = "https://n8n.srv1345711.hstgr.cloud/api/v1"
API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyZGRiZmViZC00NjIyLTRjMTAtYWU5ZC1mYjFlZGRjZWU5YjIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZWNiOTY5ZjQtNzE5NS00MTIxLWE2YWYtMDg2N2NiNjMyMzI3IiwiaWF0IjoxNzcwNDk2NDEzfQ.Zsw3KmO_lsbfomEmMGFUraSPmzM4NIIcfzCpAkB83J4"

HEADERS = {
    "X-N8N-API-KEY": API_KEY,
    "Content-Type": "application/json",
}

WORKFLOWS = [
    {
        "id": "tS2hcoeJ4ar8hivm",
        "name": "Veo3 5x8초",
        "webhook_path": "lumix-veo3-trigger",
    },
    {
        "id": "9YOHS8N1URWlzGWj",
        "name": "v3",
        "webhook_path": "lumix-v3-trigger",
    },
]


def fetch_workflow(workflow_id: str) -> dict:
    """Fetch a workflow by ID."""
    url = f"{API_BASE}/workflows/{workflow_id}"
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    return resp.json()


def find_manual_trigger_connections(workflow: dict) -> list:
    """
    Find the node(s) that the manual trigger connects to.
    Returns a list of target node names.
    """
    nodes = workflow.get("nodes", [])
    connections = workflow.get("connections", {})

    # Find the manual trigger node name
    manual_trigger_name = None
    for node in nodes:
        node_type = node.get("type", "")
        node_name = node.get("name", "")
        if node_type == "n8n-nodes-base.manualTrigger":
            manual_trigger_name = node_name
            break

    if not manual_trigger_name:
        # Fallback: look for name patterns
        for node in nodes:
            node_name = node.get("name", "")
            if "수동" in node_name or "Manual" in node_name or "Execute workflow" in node_name:
                manual_trigger_name = node_name
                break

    if not manual_trigger_name:
        # Last resort: any trigger node
        for node in nodes:
            if "trigger" in node.get("type", "").lower():
                manual_trigger_name = node["name"]
                break

    if not manual_trigger_name:
        print("  ERROR: No trigger node found!")
        return []

    print(f"  Manual trigger node: '{manual_trigger_name}'")

    trigger_connections = connections.get(manual_trigger_name, {})
    target_nodes = []

    main_outputs = trigger_connections.get("main", [])
    for output_group in main_outputs:
        for conn in output_group:
            target_nodes.append(conn["node"])

    print(f"  Manual trigger connects to: {target_nodes}")
    return target_nodes


def create_webhook_node(webhook_path: str, existing_nodes: list) -> dict:
    """Create a webhook node definition."""
    min_y = min((n.get("position", [0, 0])[1] for n in existing_nodes), default=300)
    min_x = min((n.get("position", [0, 0])[0] for n in existing_nodes), default=200)

    return {
        "parameters": {
            "httpMethod": "GET",
            "path": webhook_path,
            "responseMode": "onReceived",
            "options": {
                "responseCode": 200,
            },
        },
        "id": str(uuid.uuid4()),
        "name": "Webhook Trigger",
        "type": "n8n-nodes-base.webhook",
        "typeVersion": 2,
        "position": [min_x, min_y - 200],
        "webhookId": webhook_path,
    }


def update_workflow(workflow_id: str, workflow_data: dict) -> dict:
    """Update a workflow via PUT. Note: 'active' is read-only, must not be in body."""
    url = f"{API_BASE}/workflows/{workflow_id}"

    payload = {
        "name": workflow_data["name"],
        "nodes": workflow_data["nodes"],
        "connections": workflow_data["connections"],
        "settings": workflow_data.get("settings", {}),
    }

    if "staticData" in workflow_data:
        payload["staticData"] = workflow_data["staticData"]

    resp = requests.put(url, headers=HEADERS, json=payload)
    if resp.status_code != 200:
        print(f"  PUT failed: {resp.status_code}")
        print(f"  Response: {resp.text[:500]}")
    resp.raise_for_status()
    return resp.json()


def activate_workflow(workflow_id: str) -> dict:
    """Activate a workflow via POST /activate endpoint."""
    url = f"{API_BASE}/workflows/{workflow_id}/activate"
    resp = requests.post(url, headers=HEADERS)
    if resp.status_code != 200:
        print(f"  Activate failed: {resp.status_code}")
        print(f"  Response: {resp.text[:500]}")
    resp.raise_for_status()
    return resp.json()


def process_workflow(wf_info: dict):
    """Process a single workflow: fetch, add webhook, update, activate."""
    wf_id = wf_info["id"]
    wf_name = wf_info["name"]
    webhook_path = wf_info["webhook_path"]

    print(f"\n{'='*60}")
    print(f"Processing workflow: {wf_name} ({wf_id})")
    print(f"{'='*60}")

    # 1. Fetch the workflow
    print("\n[1] Fetching workflow...")
    workflow = fetch_workflow(wf_id)
    print(f"  Fetched: {workflow['name']}")
    print(f"  Nodes: {len(workflow['nodes'])}")
    print(f"  Active: {workflow.get('active', False)}")

    # 2. Remove any existing webhook nodes (to replace cleanly)
    existing_webhooks = [n for n in workflow["nodes"] if n.get("type") == "n8n-nodes-base.webhook"]
    if existing_webhooks:
        print(f"  Removing {len(existing_webhooks)} existing webhook node(s)...")
        existing_webhook_names = {n["name"] for n in existing_webhooks}
        workflow["nodes"] = [n for n in workflow["nodes"] if n.get("type") != "n8n-nodes-base.webhook"]
        for name in existing_webhook_names:
            if name in workflow["connections"]:
                del workflow["connections"][name]

    # 3. Find where manual trigger connects to
    print("\n[2] Finding manual trigger connections...")
    target_nodes = find_manual_trigger_connections(workflow)

    if not target_nodes:
        print("  ERROR: Could not find target nodes. Skipping.")
        return None

    # 4. Create webhook node
    print(f"\n[3] Creating webhook node (path: {webhook_path})...")
    webhook_node = create_webhook_node(webhook_path, workflow["nodes"])

    # Ensure unique name
    existing_names = {n["name"] for n in workflow["nodes"]}
    if webhook_node["name"] in existing_names:
        webhook_node["name"] = f"Webhook Trigger ({webhook_path})"
    print(f"  Node name: {webhook_node['name']}")

    workflow["nodes"].append(webhook_node)

    # 5. Add connections from webhook to targets
    print(f"\n[4] Connecting webhook -> {target_nodes}")
    conn_list = [{"node": t, "type": "main", "index": 0} for t in target_nodes]
    workflow["connections"][webhook_node["name"]] = {"main": [conn_list]}

    # 6. Update workflow via PUT (without 'active' field)
    print("\n[5] Updating workflow via PUT...")
    result = update_workflow(wf_id, workflow)
    print(f"  Updated! Nodes: {len(result.get('nodes', []))}")

    # 7. Activate workflow
    print("\n[6] Activating workflow...")
    activated = activate_workflow(wf_id)
    print(f"  Active: {activated.get('active', False)}")

    webhook_url = f"https://n8n.srv1345711.hstgr.cloud/webhook/{webhook_path}"
    print(f"\n  Webhook URL: {webhook_url}")
    return webhook_url


def main():
    print("=" * 60)
    print("Adding Webhook Triggers to n8n Workflows")
    print("=" * 60)

    webhook_urls = []

    for wf_info in WORKFLOWS:
        try:
            url = process_workflow(wf_info)
            if url:
                webhook_urls.append((wf_info["name"], url))
        except requests.exceptions.HTTPError as e:
            print(f"\n  HTTP ERROR: {e}")
            if e.response is not None:
                print(f"  Response body: {e.response.text[:500]}")
        except Exception as e:
            print(f"\n  ERROR: {e}")
            import traceback
            traceback.print_exc()

    # Summary
    print(f"\n\n{'='*60}")
    print("SUMMARY - Webhook URLs")
    print("=" * 60)
    for name, url in webhook_urls:
        print(f"  {name}: {url}")

    if len(webhook_urls) == len(WORKFLOWS):
        print("\nAll workflows updated successfully!")
    else:
        print(f"\nWARNING: Only {len(webhook_urls)}/{len(WORKFLOWS)} workflows were updated.")


if __name__ == "__main__":
    main()
