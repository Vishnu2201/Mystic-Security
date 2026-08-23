import urllib.request
import json
import sys

base = "http://localhost:8000/api/v1"

def req(path, method="GET", data=None):
    url = f"{base}{path}"
    body = json.dumps(data).encode("utf-8") if data is not None else None
    headers = {"Content-Type": "application/json"} if data is not None else {}
    request = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request) as resp:
            content = resp.read().decode("utf-8")
            return resp.status, json.loads(content) if content else None
    except urllib.error.HTTPError as e:
        content = e.read().decode("utf-8")
        return e.code, json.loads(content) if content else None

print("=== STEP 1: Create Workspace ===")
status, ws = req("/workspaces", "POST", {"name": "E2E Target Test Workspace", "description": "Temp E2E Workspace"})
print(f"POST /workspaces -> {status}, id={ws['id']}")
ws_id = ws["id"]

print("\n=== STEP 2: Create Target with IP ===")
target_payload = {
    "workspace_id": ws_id,
    "name": "Verification Target",
    "target_category": "DOMAIN",
    "identifier": "e2e-verify-domain.com",
    "description": "Original description",
    "ip_address": "192.168.50.10"
}
status, target = req("/targets", "POST", target_payload)
print(f"POST /targets -> {status}")
print(f"Returned ip_address: {repr(target.get('ip_address'))} (type: {type(target.get('ip_address')).__name__})")
target_id = target["id"]

print("\n=== STEP 3: GET Target by ID ===")
status, target_get = req(f"/targets/{target_id}", "GET")
print(f"GET /targets/{target_id} -> {status}")
print(f"Fetched ip_address: {repr(target_get.get('ip_address'))}")

print("\n=== STEP 4: GET Targets List ===")
status, target_list = req("/targets", "GET")
print(f"GET /targets -> {status}, count={len(target_list)}")

print("\n=== STEP 5: PATCH Name Only ===")
status, patched1 = req(f"/targets/{target_id}", "PATCH", {"name": "Verification Target Updated"})
print(f"PATCH /targets/{target_id} -> {status}")
print(f"Name: {patched1.get('name')}")
print(f"Preserved Description: {repr(patched1.get('description'))}")
print(f"Preserved IP Address: {repr(patched1.get('ip_address'))}")

print("\n=== STEP 6: PATCH Nullable Fields to NULL ===")
status, patched2 = req(f"/targets/{target_id}", "PATCH", {"description": None, "ip_address": None, "network_range": None})
print(f"PATCH /targets/{target_id} (nulls) -> {status}")
print(f"Description: {repr(patched2.get('description'))}")
print(f"IP Address: {repr(patched2.get('ip_address'))}")
print(f"Network Range: {repr(patched2.get('network_range'))}")

print("\n=== STEP 7: PATCH Non-nullable Name to NULL ===")
status, patch_err = req(f"/targets/{target_id}", "PATCH", {"name": None})
print(f"PATCH /targets/{target_id} (name: null) -> {status}")

print("\n=== STEP 9: DELETE Target ===")
status, del_resp = req(f"/targets/{target_id}", "DELETE")
print(f"DELETE /targets/{target_id} -> {status}")

print("\n=== STEP 10: GET Deleted Target ===")
status, get_del = req(f"/targets/{target_id}", "GET")
print(f"GET /targets/{target_id} after delete -> {status}")

print("\n=== STEP 11: Delete Workspace Cleanup ===")
status, del_ws = req(f"/workspaces/{ws_id}", "DELETE")
print(f"DELETE /workspaces/{ws_id} -> {status}")