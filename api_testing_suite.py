# api_testing_suite.py
import time
import requests

BASE_URL = "http://127.0.0.1:5000"   # or http://192.168.x.x:5000 if you want to test from another device

def test_health():
    print("[TEST] /health")
    t0 = time.perf_counter()
    r = requests.get(f"{BASE_URL}/health")
    dt = (time.perf_counter() - t0) * 1000

    try:
        data = r.json()
    except Exception:
        print(f"  ❌ Response is not JSON, status={r.status_code}")
        return

    if r.status_code == 200 and data.get("status") in ("ok", "warning"):
        print(f"  ✅ OK (status={data.get('status')}, {dt:.1f} ms)")
    else:
        print(f"  ❌ Failed, status_code={r.status_code}, body={data}")

def test_predict_valid():
    print("[TEST] /predict (valid input)")
    payload = {"text": "ayamnya enak banget, pelayanan ramah"}
    t0 = time.perf_counter()
    r = requests.post(f"{BASE_URL}/predict", json=payload)
    dt = (time.perf_counter() - t0) * 1000

    if r.status_code != 200:
        print(f"  ❌ status_code={r.status_code}, body={r.text}")
        return

    data = r.json()
    ok = (
        "results" in data
        and isinstance(data["results"], list)
        and len(data["results"]) == 1
        and "per_model" in data["results"][0]
    )

    if ok:
        print(f"  ✅ OK ({dt:.1f} ms), models={ [m['model'] for m in data['results'][0]['per_model']] }")
    else:
        print(f"  ❌ Struktur respons tidak sesuai, body={data}")

def test_predict_empty():
    print("[TEST] /predict (empty text)")
    payload = {"text": ""}
    r = requests.post(f"{BASE_URL}/predict", json=payload)

    if r.status_code == 400:
        print("  ✅ OK, error 400 expected for empty input")
    else:
        print(f"  ❌ Expected 400, got {r.status_code}, body={r.text}")

def test_predict_invalid_format():
    print("[TEST] /predict (wrong JSON format)")
    payload = {"wrong_key": "hehe"}  # no 'text' or 'texts' key
    r = requests.post(f"{BASE_URL}/predict", json=payload)

    if r.status_code == 400:
        print("  ✅ OK, 400 for wrong JSON format")
    else:
        print(f"  ❌ Expected 400, got {r.status_code}, body={r.text}")

def test_selftest():
    print("[TEST] /selftest")
    r = requests.get(f"{BASE_URL}/selftest")
    if r.status_code == 200:
        print("  ✅ OK, /selftest running")
    else:
        print(f"  ❌ status_code={r.status_code}, body={r.text}")

def run_all():
    print("=== API TESTING SUITE ===")
    test_health()
    test_predict_valid()
    test_predict_empty()
    test_predict_invalid_format()
    test_selftest()
    print("=== COMPLETED ===")

if __name__ == "__main__":
    run_all()
