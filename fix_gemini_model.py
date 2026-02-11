#!/usr/bin/env python3
"""
Fix Gemini model name in n8n workflows.
Replace "gemini-2.5-flash-lite-preview-06-17" with "gemini-2.5-flash-lite" (stable version).

Target workflows:
  1. Veo3 5x8초: tS2hcoeJ4ar8hivm
  2. v3: 9YOHS8N1URWlzGWj
"""

import json
import requests
import sys

API_BASE = "https://n8n.srv1345711.hstgr.cloud/api/v1"
API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyZGRiZmViZC00NjIyLTRjMTAtYWU5ZC1mYjFlZGRjZWU5YjIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZWNiOTY5ZjQtNzE5NS00MTIxLWE2YWYtMDg2N2NiNjMyMzI3IiwiaWF0IjoxNzcwNDk2NDEzfQ.Zsw3KmO_lsbfomEmMGFUraSPmzM4NIIcfzCpAkB83J4"

OLD_MODEL = "gemini-2.5-flash-lite-preview-06-17"
NEW_MODEL = "gemini-2.5-flash-lite"

WORKFLOWS = {
    "tS2hcoeJ4ar8hivm": "Veo3 5x8초",
    "9YOHS8N1URWlzGWj": "v3",
}

HEADERS = {
    "X-N8N-API-KEY": API_KEY,
    "Content-Type": "application/json",
}

# Only these fields are accepted by the n8n PUT /workflows/{id} endpoint
UPLOAD_FIELDS = ["name", "nodes", "connections", "settings"]


def fetch_workflow(wf_id: str) -> dict:
    url = f"{API_BASE}/workflows/{wf_id}"
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    return resp.json()


def deep_replace_in_obj(obj, old: str, new: str, path: str = "") -> list:
    changes = []
    if isinstance(obj, dict):
        for key, val in obj.items():
            current_path = f"{path}.{key}" if path else key
            if isinstance(val, str) and old in val:
                new_val = val.replace(old, new)
                obj[key] = new_val
                old_snippet = val if len(val) < 200 else val[:200] + "..."
                new_snippet = new_val if len(new_val) < 200 else new_val[:200] + "..."
                changes.append((current_path, old_snippet, new_snippet))
            else:
                changes.extend(deep_replace_in_obj(val, old, new, current_path))
    elif isinstance(obj, list):
        for idx, item in enumerate(obj):
            current_path = f"{path}[{idx}]"
            if isinstance(item, str) and old in item:
                new_val = item.replace(old, new)
                obj[idx] = new_val
                old_snippet = item if len(item) < 200 else item[:200] + "..."
                new_snippet = new_val if len(new_val) < 200 else new_val[:200] + "..."
                changes.append((current_path, old_snippet, new_snippet))
            else:
                changes.extend(deep_replace_in_obj(item, old, new, current_path))
    return changes


def count_occurrences(obj, target: str) -> int:
    count = 0
    if isinstance(obj, dict):
        for val in obj.values():
            if isinstance(val, str):
                count += val.count(target)
            else:
                count += count_occurrences(val, target)
    elif isinstance(obj, list):
        for item in obj:
            if isinstance(item, str):
                count += item.count(target)
            else:
                count += count_occurrences(item, target)
    return count


def update_workflow(wf_id: str, wf: dict) -> dict:
    url = f"{API_BASE}/workflows/{wf_id}"
    payload = {k: wf[k] for k in UPLOAD_FIELDS if k in wf}
    resp = requests.put(url, headers=HEADERS, json=payload)
    if not resp.ok:
        print(f"    HTTP {resp.status_code}: {resp.text[:500]}")
    resp.raise_for_status()
    return resp.json()


def process_workflow(wf_id: str, wf_label: str):
    print(f"\n{'='*70}")
    print(f"Processing workflow: {wf_label} (ID: {wf_id})")
    print(f"{'='*70}")

    # Step 1: Fetch
    print("\n[1] Fetching workflow...")
    wf = fetch_workflow(wf_id)
    print(f"    Name: {wf.get('name', 'N/A')}")
    print(f"    Nodes count: {len(wf.get('nodes', []))}")

    # Check activeVersion
    if wf.get("activeVersion"):
        av_count = count_occurrences(wf["activeVersion"], OLD_MODEL)
        print(f"    activeVersion has {av_count} occurrences of old model (read-only, updates on activation)")

    # Count in nodes
    nodes_before = count_occurrences(wf.get("nodes", []), OLD_MODEL)
    full_before = count_occurrences(wf, OLD_MODEL)
    print(f"\n[2] Occurrences of old model name:")
    print(f"    In nodes: {nodes_before}")
    print(f"    In full response (incl. read-only): {full_before}")

    if nodes_before == 0:
        print("    No occurrences in editable nodes. Skipping upload.")
        return

    # Step 3: Replace
    print(f"\n[3] Replacing '{OLD_MODEL}' -> '{NEW_MODEL}'...")

    nodes = wf.get("nodes", [])
    total_changes = []
    for i, node in enumerate(nodes):
        node_name = node.get("name", f"Node[{i}]")
        node_type = node.get("type", "unknown")
        changes = deep_replace_in_obj(node, OLD_MODEL, NEW_MODEL, path=f"nodes[{i}]({node_name})")
        if changes:
            print(f"\n    Node: '{node_name}' (type: {node_type})")
            for path, old_snip, new_snip in changes:
                print(f"      Path: {path}")
                if len(old_snip) > 120:
                    print(f"        OLD: ...{OLD_MODEL}...")
                    print(f"        NEW: ...{NEW_MODEL}...")
                else:
                    print(f"        OLD: {old_snip}")
                    print(f"        NEW: {new_snip}")
            total_changes.extend(changes)

    # Also check settings (just in case)
    if "settings" in wf and wf["settings"]:
        changes = deep_replace_in_obj(wf["settings"], OLD_MODEL, NEW_MODEL, path="settings")
        if changes:
            print(f"\n    Settings:")
            for path, old_snip, new_snip in changes:
                print(f"      {path}: {old_snip} -> {new_snip}")
            total_changes.extend(changes)

    print(f"\n    Total replacements: {len(total_changes)}")

    # Step 4: Upload
    print(f"\n[4] Uploading modified workflow...")
    try:
        result = update_workflow(wf_id, wf)
        print(f"    Upload successful. Updated at: {result.get('updatedAt', 'N/A')}")
    except requests.HTTPError as e:
        print(f"    Upload FAILED: {e}")
        return

    # Step 5: Verify
    print(f"\n[5] Verifying - fetching workflow again...")
    wf_verify = fetch_workflow(wf_id)

    nodes_after_old = count_occurrences(wf_verify.get("nodes", []), OLD_MODEL)
    nodes_after_new = count_occurrences(wf_verify.get("nodes", []), NEW_MODEL)
    print(f"    In nodes - OLD model: {nodes_after_old}")
    print(f"    In nodes - NEW model: {nodes_after_new}")

    if nodes_after_old == 0:
        print(f"    VERIFIED: No remaining instances of '{OLD_MODEL}' in nodes")
    else:
        print(f"    WARNING: {nodes_after_old} instances still remain in nodes!")

    # Check activeVersion
    if wf_verify.get("activeVersion"):
        av_old = count_occurrences(wf_verify["activeVersion"], OLD_MODEL)
        av_new = count_occurrences(wf_verify["activeVersion"], NEW_MODEL)
        print(f"    activeVersion - OLD: {av_old}, NEW: {av_new}")
        if av_old > 0:
            print(f"    NOTE: activeVersion still has old refs - updates when workflow is re-activated.")


def main():
    print("Gemini Model Name Fixer")
    print(f"  Old: {OLD_MODEL}")
    print(f"  New: {NEW_MODEL}")
    print(f"  API: {API_BASE}")

    for wf_id, wf_label in WORKFLOWS.items():
        try:
            process_workflow(wf_id, wf_label)
        except requests.HTTPError as e:
            print(f"\nERROR processing {wf_label} ({wf_id}): {e}")
            if e.response is not None:
                print(f"  Response: {e.response.text[:500]}")
        except Exception as e:
            print(f"\nERROR processing {wf_label} ({wf_id}): {e}")
            import traceback
            traceback.print_exc()

    print(f"\n{'='*70}")
    print("Done!")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
