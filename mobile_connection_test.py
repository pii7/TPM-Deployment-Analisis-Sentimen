import requests
import time
import socket

def get_lan_ip() -> str:
    """
    Detect the active LAN IP (Wi-Fi).
    If it fails, will fallback to 127.0.0.1
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Connect to Google DNS (no data sent, just check routing)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def test_frontend(host: str, port: int = 8000, timeout: float = 5.0):
    url = f"http://{host}:{port}/"
    print(f"\n[TEST] Accessing Frontend: {url}")
    try:
        t0 = time.time()
        r = requests.get(url, timeout=timeout)
        dt = (time.time() - t0) * 1000
        if r.status_code == 200:
            print(f"  ✅ SUCCESS! Frontend responded in {dt:.1f} ms")
        else:
            print(f"  ❌ FAILED! Status code {r.status_code}")
    except Exception as e:
        print(f"  ❌ ERROR: Cannot connect. Make sure server is running on 0.0.0.0 not localhost.")
        print(f"     Error details: {e}")

def test_api_predict(host: str, port: int = 5000, timeout: float = 5.0):
    url = f"http://{host}:{port}/predict"
    print(f"\n[TEST] Accessing API /predict: {url}")
    try:
        # Example payload for testing
        payload = {"text": "The chicken is very delicious, really tasty!"}
        
        t0 = time.time()
        r = requests.post(url, json=payload, timeout=timeout)
        dt = (time.time() - t0) * 1000
        
        if r.status_code == 200:
            data = r.json()
            print(f"  ✅ SUCCESS! API responded in {dt:.1f} ms")
            # Try to get model info if available
            try:
                models = [m['model'] for m in data.get('results', [{}])[0].get('per_model', [])]
                print(f"     Models that responded: {models}")
            except:
                pass
        else:
            print(f"  ❌ FAILED! Status code {r.status_code}")
            print(f"     Response: {r.text[:100]}...")
    except Exception as e:
        print(f"  ❌ ERROR: Cannot connect to API.")
        print(f"     Error details: {e}")

if __name__ == "__main__":
    print("=== MOBILE CONNECTION DIAGNOSTIC ===")
    
    # 1. Detect IP first
    target_ip = get_lan_ip()
    print(f"[INFO] Laptop IP detected: {target_ip}")
    print("----------------------------------------")

    # 2. Run tests to that IP (Dynamic)
    #    This simulates connection from your phone.
    test_frontend(target_ip, 8000)
    test_api_predict(target_ip, 5000)

    print("\n----------------------------------------")
    print("CONCLUSION:")
    if target_ip == "127.0.0.1":
        print("⚠️  Laptop is not connected to Wifi/Hotspot, or detection failed.")
    else:
        print(f"If the tests above ✅ (Green Check), then on your phone open:")
        print(f"👉 http://{target_ip}:8000")
    
    print("=== DONE ===")