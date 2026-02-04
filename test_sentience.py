#!/usr/bin/env python3
"""
Test script for voidOS Sentience HUD
Verifies all components are working correctly
"""

import requests
import json
import time
import subprocess
import sys
from pathlib import Path

BASE_URL = "http://localhost:5001"
TEST_TIMEOUT = 5

def test_dashboard_load():
    """Test: Dashboard HTML loads"""
    print("🔍 Testing dashboard load...", end=" ")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=TEST_TIMEOUT)
        if response.status_code == 200 and "GHOSTSHELL" in response.text:
            print("✅ PASS")
            return True
        else:
            print(f"❌ FAIL (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ FAIL ({e})")
        return False

def test_api_cycle_kernel():
    """Test: CycleKernel bridge endpoint"""
    print("🔍 Testing /api/cycle-kernel...", end=" ")
    try:
        response = requests.get(f"{BASE_URL}/api/cycle-kernel", timeout=TEST_TIMEOUT)
        data = response.json()
        
        required_fields = ['mode', 'divergence_weight', 'precision_bias', 'velocity', 'core_integrity', 'epoch']
        if all(field in data for field in required_fields):
            print(f"✅ PASS")
            print(f"   Mode: {data['mode']}, Integrity: {data['core_integrity']*100:.1f}%")
            return True
        else:
            print(f"❌ FAIL (Missing fields)")
            return False
    except Exception as e:
        print(f"❌ FAIL ({e})")
        return False

def test_api_apps():
    """Test: Applications list endpoint"""
    print("🔍 Testing /api/apps...", end=" ")
    try:
        response = requests.get(f"{BASE_URL}/api/apps", timeout=TEST_TIMEOUT)
        apps = response.json()
        
        if isinstance(apps, list) and len(apps) > 0:
            print(f"✅ PASS ({len(apps)} apps)")
            for app in apps[:3]:
                print(f"   • {app.get('name')} ({app.get('icon')})")
            return True
        else:
            print(f"❌ FAIL (Empty or invalid response)")
            return False
    except Exception as e:
        print(f"❌ FAIL ({e})")
        return False

def test_api_seed():
    """Test: Seed configuration endpoint"""
    print("🔍 Testing /api/seed...", end=" ")
    try:
        response = requests.get(f"{BASE_URL}/api/seed", timeout=TEST_TIMEOUT)
        seed = response.json()
        
        if 'seed_id' in seed:
            print(f"✅ PASS")
            print(f"   Seed ID: {seed['seed_id']}")
            return True
        else:
            print(f"❌ FAIL (Invalid seed)")
            return False
    except Exception as e:
        print(f"❌ FAIL ({e})")
        return False

def test_api_gemini_insight():
    """Test: Gemini insight generation"""
    print("🔍 Testing /api/gemini-insight...", end=" ")
    try:
        payload = {
            "systemState": {
                "mode": "Balanced",
                "core_integrity": 0.85,
                "divergence_weight": 0.34
            }
        }
        response = requests.post(
            f"{BASE_URL}/api/gemini-insight",
            json=payload,
            timeout=TEST_TIMEOUT
        )
        data = response.json()
        
        if 'insight' in data and len(data['insight']) > 10:
            print(f"✅ PASS")
            print(f"   Insight length: {len(data['insight'])} chars")
            return True
        else:
            print(f"❌ FAIL (Invalid response)")
            return False
    except Exception as e:
        print(f"❌ FAIL ({e})")
        return False

def test_api_gemini_tts():
    """Test: Gemini TTS endpoint"""
    print("🔍 Testing /api/gemini-tts...", end=" ")
    try:
        payload = {"text": "System operating normally"}
        response = requests.post(
            f"{BASE_URL}/api/gemini-tts",
            json=payload,
            timeout=TEST_TIMEOUT
        )
        
        if response.status_code == 200 and response.headers.get('content-type') == 'audio/wav':
            print(f"✅ PASS")
            print(f"   Audio size: {len(response.content)} bytes")
            return True
        else:
            print(f"❌ FAIL (Invalid audio response)")
            return False
    except Exception as e:
        print(f"❌ FAIL ({e})")
        return False

def test_api_trigger_scan():
    """Test: Trigger scan endpoint"""
    print("🔍 Testing /api/trigger-scan...", end=" ")
    try:
        response = requests.post(f"{BASE_URL}/api/trigger-scan", timeout=TEST_TIMEOUT)
        data = response.json()
        
        if 'status' in data:
            print(f"✅ PASS")
            return True
        else:
            print(f"❌ FAIL (Invalid response)")
            return False
    except Exception as e:
        print(f"❌ FAIL ({e})")
        return False

def test_cors_headers():
    """Test: CORS headers present"""
    print("🔍 Testing CORS headers...", end=" ")
    try:
        response = requests.options(f"{BASE_URL}/api/cycle-kernel", timeout=TEST_TIMEOUT)
        
        cors_headers = [
            'access-control-allow-origin',
            'access-control-allow-methods',
            'access-control-allow-headers'
        ]
        
        present = all(h in response.headers for h in cors_headers)
        if present:
            print(f"✅ PASS")
            return True
        else:
            print(f"❌ FAIL (Missing CORS headers)")
            return False
    except Exception as e:
        print(f"❌ FAIL ({e})")
        return False

def main():
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║               voidOS Sentience HUD - Test Suite                              ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    # Check if server is running
    print("📍 Checking server at http://localhost:5001...\n")
    
    try:
        response = requests.get(BASE_URL, timeout=2)
    except:
        print("❌ ERROR: Cannot connect to server!")
        print("\n💡 To start the server, run:")
        print("   python3 voidos_sentience.py\n")
        sys.exit(1)
    
    # Run tests
    tests = [
        test_dashboard_load,
        test_api_cycle_kernel,
        test_api_apps,
        test_api_seed,
        test_api_gemini_insight,
        test_api_gemini_tts,
        test_api_trigger_scan,
        test_cors_headers
    ]
    
    results = []
    for test in tests:
        results.append(test())
        time.sleep(0.2)
    
    # Summary
    print("\n" + "="*80)
    passed = sum(results)
    total = len(results)
    percentage = (passed / total) * 100
    
    print(f"✅ PASSED: {passed}/{total} ({percentage:.0f}%)")
    
    if passed == total:
        print("\n🎉 All tests passed! System is ready.")
        print("\n🌐 Open dashboard: http://localhost:5001")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check the output above.")
    
    print("\n" + "="*80)

if __name__ == '__main__':
    main()
