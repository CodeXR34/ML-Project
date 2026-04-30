# -*- coding: utf-8 -*-
"""
test_app.py -- Comprehensive test suite for ExpensePredict AI
Run with: python test_app.py
"""
import sys, os, json, pickle

# ── resolve paths ────────────────────────────────────────────────────────
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)

# Force stdout to UTF-8 so special chars don't crash on Windows
sys.stdout.reconfigure(encoding="utf-8")

# Force CWD so MODEL_PATH ('model.pkl') resolves correctly
os.chdir(BASE)

from app import app

# ── helpers ──────────────────────────────────────────────────────────────
results = []

def check(name, condition, detail=""):
    status = "[PASS]" if condition else "[FAIL]"
    suffix = f"  --> {detail}" if detail else ""
    print(f"  {status}  {name}{suffix}")
    results.append((name, condition))

# =====================================================================
print("\n============================================")
print("  ExpensePredict AI -- Test Suite")
print("============================================\n")

# ── 1. Model file exists ─────────────────────────────────────────────
print("[ 1 ] Model Integrity")
model_path = os.path.join(BASE, "model.pkl")
check("model.pkl exists", os.path.exists(model_path))

# ── 2. Model loads & has required keys ──────────────────────────────
print("\n[ 2 ] Model Contents")
md = None
try:
    with open(model_path, "rb") as f:
        md = pickle.load(f)
    check("model.pkl is a dict",   isinstance(md, dict))
    check("key: 'model'",          "model"    in md)
    check("key: 'le_occ'",         "le_occ"   in md)
    check("key: 'le_city'",        "le_city"  in md)
    check("key: 'features'",       "features" in md)
    if "features" in md:
        check("features is a list", isinstance(md["features"], list),
              f"{len(md['features'])} features")
except Exception as e:
    check("model.pkl loads without error", False, str(e))

# ── 3. Flask routes ──────────────────────────────────────────────────
print("\n[ 3 ] Page Routes")
client = app.test_client()

for route, label in [("/", "Home"), ("/expense", "Track Expense"), ("/history", "History")]:
    r = client.get(route)
    check(f"GET {route} -- {label} returns 200",
          r.status_code == 200, f"status={r.status_code}")

r = client.get("/result")
check("GET /result without session returns 200",
      r.status_code == 200, f"status={r.status_code}")

# ── 4. Predict -- valid payload ──────────────────────────────────────
print("\n[ 4 ] POST /predict -- Valid Payload")
valid_payload = {
    "age": 28,
    "occupation": "Salaried",      # must match training: Business/Freelancer/Salaried/Student
    "monthly_income": 75000,
    "city_type": "Urban",          # must match training: Rural/Semi-Urban/Urban
    "date": "2026-04-30",
    "food": 8000,
    "transport": 3000,
    "rent": 15000,
    "entertainment": 2500,
    "utilities": 1500,
    "shopping": 4000,
    "others": 1000
}

r = client.post(
    "/predict",
    data=json.dumps(valid_payload),
    content_type="application/json"
)
check("POST /predict status 200", r.status_code == 200, f"status={r.status_code}")

try:
    body = r.get_json()
    check("response is JSON",          body is not None)
    check("status == 'success'",       body.get("status") == "success",  f"got: {body}")
    check("redirect field present",    "redirect" in body,               f"keys: {list(body.keys())}")
except Exception as e:
    check("JSON parse", False, str(e))

# ── 5. Predict -- missing required field ────────────────────────────
print("\n[ 5 ] POST /predict -- Missing Required Field")
bad_payload = {k: v for k, v in valid_payload.items() if k != "monthly_income"}
r = client.post("/predict", data=json.dumps(bad_payload), content_type="application/json")
check("Missing field returns 400", r.status_code == 400, f"status={r.status_code}")

# ── 6. Predict -- wrong data type ───────────────────────────────────
print("\n[ 6 ] POST /predict -- Invalid Data Type")
bad_type = {**valid_payload, "age": "not_a_number"}
r = client.post("/predict", data=json.dumps(bad_type), content_type="application/json")
check("Invalid type returns 400", r.status_code == 400, f"status={r.status_code}")

# ── 7. Predict -- empty body ─────────────────────────────────────────
print("\n[ 7 ] POST /predict -- Empty Body")
r = client.post("/predict", data="{}", content_type="application/json")
check("Empty body returns 400", r.status_code == 400, f"status={r.status_code}")

# ── 8. Predict -- unseen label (LabelEncoder will raise ValueError) ──
print("\n[ 8 ] POST /predict -- Unseen Label (unknown occupation/city)")
unknown_payload = {**valid_payload, "occupation": "ZZZ_Unknown_999", "city_type": "Mars"}
r = client.post("/predict", data=json.dumps(unknown_payload), content_type="application/json")
check("Unseen label returns 400 (not 500)", r.status_code == 400,
      f"status={r.status_code}")
body = r.get_json()
check("Unseen label error mentions valid options",
      "Valid options" in (body or {}).get("error", ""),
      f"got: {body}")

# ── 8b. Each valid occupation works ─────────────────────────────────
print("\n[ 8b ] POST /predict -- All Valid Occupations")
for occ in ["Business", "Freelancer", "Salaried", "Student"]:
    payload = {**valid_payload, "occupation": occ}
    r = client.post("/predict", data=json.dumps(payload), content_type="application/json")
    check(f"occupation='{occ}' accepted", r.status_code == 200, f"status={r.status_code}")

# ── 8c. Each valid city works ────────────────────────────────────────
print("\n[ 8c ] POST /predict -- All Valid City Types")
for city in ["Rural", "Semi-Urban", "Urban"]:
    payload = {**valid_payload, "city_type": city}
    r = client.post("/predict", data=json.dumps(payload), content_type="application/json")
    check(f"city_type='{city}' accepted", r.status_code == 200, f"status={r.status_code}")

# ── 9. Template content ──────────────────────────────────────────────
print("\n[ 9 ] Template Content Checks")
home_html = client.get("/").data.decode("utf-8")
check("Home page contains 'ExpensePredict'", "ExpensePredict" in home_html)
check("Home page loads Font Awesome",        "font-awesome"   in home_html)
check("Home page loads style.css",           "style.css"      in home_html)

hist_html = client.get("/history").data.decode("utf-8")
check("History page has stat-cards section", "history-stats"  in hist_html)
check("History page has table",              "history-table"  in hist_html)
check("History page has trend chart canvas", "trendChart"     in hist_html)

# ── Summary ──────────────────────────────────────────────────────────
passed = sum(1 for _, ok in results if ok)
total  = len(results)
failed = [(n, ok) for n, ok in results if not ok]

print("\n============================================")
print(f"  Results: {passed}/{total} passed")
if failed:
    print("  Failed tests:")
    for name, _ in failed:
        print(f"    * {name}")
else:
    print("  All tests passed!")
print("============================================\n")

sys.exit(0 if passed == total else 1)
