import urllib.request
import json

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

print("=== STEP 1: Create Workspace A ===")
status, wsA = req("/workspaces", "POST", {"name": "Workspace Alpha", "description": "First workspace"})
print(f"POST /workspaces -> Status: {status}")
assert status == 201
wsA_id = wsA["id"]

print("\n=== STEP 2: Create Workspace B ===")
status, wsB = req("/workspaces", "POST", {"name": "Workspace Beta", "description": "Second workspace"})
print(f"POST /workspaces -> Status: {status}")
assert status == 201
wsB_id = wsB["id"]

print("\n=== STEP 3: Attempt Duplicate Workspace Name ===")
status, err3 = req("/workspaces", "POST", {"name": "Workspace Alpha"})
print(f"POST /workspaces (duplicate 'Workspace Alpha') -> Status: {status}")
assert status == 409

print("\n=== STEP 4: Attempt Empty String Name ===")
status, err4 = req("/workspaces", "POST", {"name": ""})
print(f"POST /workspaces (name='') -> Status: {status}")
assert status == 422

print("\n=== STEP 5: Attempt Whitespace-Only Name ===")
status, err5 = req("/workspaces", "POST", {"name": "    "})
print(f"POST /workspaces (name='   ') -> Status: {status}")
assert status == 422

print("\n=== STEP 6: Attempt Name = null ===")
status, err6 = req("/workspaces", "POST", {"name": None})
print(f"POST /workspaces (name=null) -> Status: {status}")
assert status == 422

print("\n=== STEP 7: GET Workspace A by ID ===")
status, getA = req(f"/workspaces/{wsA_id}", "GET")
print(f"GET /workspaces/{wsA_id} -> Status: {status}, Name: '{getA['name']}'")
assert status == 200
assert getA["name"] == "Workspace Alpha"

print("\n=== STEP 8: GET All Workspaces ===")
status, all_ws = req("/workspaces", "GET")
print(f"GET /workspaces -> Status: {status}, count={len(all_ws)}")
assert status == 200
assert len(all_ws) >= 2

print("\n=== STEP 9: PATCH Workspace A Description Only ===")
status, p9 = req(f"/workspaces/{wsA_id}", "PATCH", {"description": "Updated Alpha Description"})
print(f"PATCH /workspaces/{wsA_id} -> Status: {status}")
assert status == 200
assert p9["name"] == "Workspace Alpha"
assert p9["description"] == "Updated Alpha Description"

print("\n=== STEP 10: PATCH Workspace A Description to null ===")
status, p10 = req(f"/workspaces/{wsA_id}", "PATCH", {"description": None})
print(f"PATCH /workspaces/{wsA_id} (description=null) -> Status: {status}")
assert status == 200
assert p10["description"] is None

print("\n=== STEP 11: PATCH Workspace A Name ===")
status, p11 = req(f"/workspaces/{wsA_id}", "PATCH", {"name": "Workspace Alpha Renamed"})
print(f"PATCH /workspaces/{wsA_id} (new name) -> Status: {status}")
assert status == 200
assert p11["name"] == "Workspace Alpha Renamed"

print("\n=== STEP 12: Attempt PATCH to Whitespace-Only Name ===")
status, err12 = req(f"/workspaces/{wsA_id}", "PATCH", {"name": "   "})
print(f"PATCH /workspaces/{wsA_id} (name='   ') -> Status: {status}")
assert status == 422

print("\n=== STEP 13: Attempt PATCH Name to null ===")
status, err13 = req(f"/workspaces/{wsA_id}", "PATCH", {"name": None})
print(f"PATCH /workspaces/{wsA_id} (name=null) -> Status: {status}")
assert status == 422

print("\n=== STEP 14: Attempt PATCH to Existing Workspace B Name ===")
status, err14 = req(f"/workspaces/{wsA_id}", "PATCH", {"name": "Workspace Beta"})
print(f"PATCH /workspaces/{wsA_id} (duplicate name 'Workspace Beta') -> Status: {status}")
assert status == 409

print("\n=== STEP 15: Create Real Target inside Workspace A ===")
status, targetA = req("/targets", "POST", {
    "workspace_id": wsA_id,
    "name": "Target in Workspace A",
    "target_category": "DOMAIN",
    "identifier": "target-in-alpha.com"
})
print(f"POST /targets in Workspace A -> Status: {status}")
assert status == 201
targetA_id = targetA["id"]

print("\n=== STEP 16: Delete Workspace A (Cascade Deletion) ===")
status, delA = req(f"/workspaces/{wsA_id}", "DELETE")
print(f"DELETE /workspaces/{wsA_id} -> Status: {status}")
assert status == 204

print("\n=== Verify Child Target Deletion (Option B Cascade) ===")
status, getTargetA = req(f"/targets/{targetA_id}", "GET")
print(f"GET /targets/{targetA_id} after Workspace deletion -> Status: {status}")
assert status == 404

print("\n=== STEP 19: Delete Workspace B ===")
status, delB = req(f"/workspaces/{wsB_id}", "DELETE")
print(f"DELETE /workspaces/{wsB_id} -> Status: {status}")
assert status == 204

print("\n=== STEP 20: GET Deleted Workspace B ===")
status, getB = req(f"/workspaces/{wsB_id}", "GET")
print(f"GET /workspaces/{wsB_id} after deletion -> Status: {status}")
assert status == 404

print("\n=== All API Steps Verified Successfully! ===")