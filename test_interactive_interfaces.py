#!/usr/bin/env python3
"""
Comprehensive Interactive Interface Test Suite for voidOS
Tests all interactive components: Dashboard, Terminal, APIs, and Applications
"""

import json
import urllib.request
import urllib.error
import time
import sys

BASE_DASHBOARD = "http://localhost:5001"
BASE_TERMINAL = "http://localhost:5002"

def test_dashboard_health():
    """Test Dashboard health endpoint"""
    print("\n[1] Dashboard Health Check")
    try:
        response = urllib.request.urlopen(f"{BASE_DASHBOARD}/api/health")
        data = json.loads(response.read())
        print(f"    ✅ Status: {data['status']}")
        print(f"    ✅ Seed ID: {data.get('seed_id', 'N/A')}")
        return True
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return False

def test_dashboard_html():
    """Test Dashboard HTML page loads"""
    print("\n[2] Dashboard HTML Page Load")
    try:
        response = urllib.request.urlopen(f"{BASE_DASHBOARD}/")
        html = response.read().decode('utf-8')
        if len(html) > 1000:
            print(f"    ✅ Dashboard HTML loaded ({len(html)} bytes)")
            return True
        else:
            print(f"    ❌ Dashboard HTML too small ({len(html)} bytes)")
            return False
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return False

def test_dashboard_apps():
    """Test Dashboard apps API"""
    print("\n[3] List Applications")
    try:
        response = urllib.request.urlopen(f"{BASE_DASHBOARD}/api/apps")
        data = json.loads(response.read())
        apps = data.get('apps', [])
        print(f"    ✅ Found {len(apps)} applications")
        for i, app in enumerate(apps[:5], 1):
            print(f"       {i}. {app.get('name')} ({app.get('id')}): {app.get('status')}")
        return len(apps) > 0
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return False

def test_dashboard_apps_status():
    """Test Dashboard apps status API"""
    print("\n[4] Get All Applications Status")
    try:
        response = urllib.request.urlopen(f"{BASE_DASHBOARD}/api/apps/status")
        data = json.loads(response.read())
        status_data = data.get('status', {})
        print(f"    ✅ Retrieved status for {len(status_data)} apps")
        return True
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return False

def test_seed_info():
    """Test Seed information endpoint"""
    print("\n[5] Get Seed Information")
    try:
        response = urllib.request.urlopen(f"{BASE_DASHBOARD}/api/seed")
        data = json.loads(response.read())
        print(f"    ✅ Seed ID: {data.get('seed_id', 'N/A')}")
        print(f"    ✅ Genesis Epoch: {data.get('genesis_epoch', 'N/A')}")
        merkle = str(data.get('merkle_verification', 'N/A'))
        print(f"    ✅ Merkle Root: {merkle[:32]}...")
        return True
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return False

def test_terminal_health():
    """Test Terminal Application health"""
    print("\n[6] Terminal Application Health Check")
    try:
        response = urllib.request.urlopen(f"{BASE_TERMINAL}/health")
        data = json.loads(response.read())
        print(f"    ✅ Status: {data['status']}")
        print(f"    ✅ App: {data.get('app', 'N/A')}")
        return True
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return False

def test_terminal_session():
    """Test Terminal session creation"""
    print("\n[7] Terminal Session Creation")
    try:
        response = urllib.request.urlopen(f"{BASE_TERMINAL}/api/session/create")
        data = json.loads(response.read())
        session_id = data.get('session_id')
        print(f"    ✅ Session created: {session_id}")
        created_at = data.get('created_at', 'N/A')
        print(f"    ✅ Created at: {created_at}")
        return session_id
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return None

def test_terminal_session_status(session_id):
    """Test Terminal session status"""
    print("\n[8] Terminal Session Status")
    try:
        response = urllib.request.urlopen(f"{BASE_TERMINAL}/api/session/status?session_id={session_id}")
        data = json.loads(response.read())
        print(f"    ✅ Session ID: {data.get('session_id', 'N/A')}")
        print(f"    ✅ Created: {data.get('created_at', 'N/A')}")
        print(f"    ✅ PWD: {data.get('pwd', 'N/A')}")
        return True
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return False

def test_terminal_pwd(session_id):
    """Test Terminal get PWD"""
    print("\n[9] Terminal Get Current Directory")
    try:
        response = urllib.request.urlopen(f"{BASE_TERMINAL}/api/terminal/pwd?session_id={session_id}")
        data = json.loads(response.read())
        pwd = data.get('pwd', 'N/A')
        print(f"    ✅ Current directory: {pwd}")
        return True
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return False

def test_terminal_execute(session_id, command):
    """Test Terminal command execution"""
    print(f"\n[10] Terminal Execute: {command}")
    try:
        req = urllib.request.Request(
            f"{BASE_TERMINAL}/api/terminal/execute",
            data=json.dumps({
                "session_id": session_id,
                "command": command
            }).encode(),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        response = urllib.request.urlopen(req)
        result = json.loads(response.read())
        output = result.get('output', '').strip()
        exit_code = result.get('exit_code', -1)
        print(f"    ✅ Exit code: {exit_code}")
        print(f"    ✅ Output: {output[:100]}")
        return exit_code == 0
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return False

def test_terminal_history(session_id):
    """Test Terminal command history"""
    print("\n[11] Terminal Command History")
    try:
        response = urllib.request.urlopen(f"{BASE_TERMINAL}/api/terminal/history?session_id={session_id}")
        data = json.loads(response.read())
        history = data.get('history', [])
        print(f"    ✅ History contains {len(history)} commands")
        for cmd in history:
            print(f"       - {cmd}")
        return True
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("VOIDOS INTERACTIVE INTERFACES - COMPREHENSIVE TEST SUITE")
    print("=" * 80)
    
    results = {
        "dashboard": [],
        "terminal": [],
        "success": 0,
        "total": 0
    }
    
    # Dashboard Tests
    print("\n" + "-" * 80)
    print("DASHBOARD TESTS")
    print("-" * 80)
    results["dashboard"].append(("Health Check", test_dashboard_health()))
    results["dashboard"].append(("HTML Load", test_dashboard_html()))
    results["dashboard"].append(("List Apps", test_dashboard_apps()))
    results["dashboard"].append(("Apps Status", test_dashboard_apps_status()))
    results["dashboard"].append(("Seed Info", test_seed_info()))
    
    # Terminal Tests
    print("\n" + "-" * 80)
    print("TERMINAL APPLICATION TESTS")
    print("-" * 80)
    results["terminal"].append(("Health Check", test_terminal_health()))
    
    session_id = test_terminal_session()
    if session_id:
        results["terminal"].append(("Session Create", True))
        results["terminal"].append(("Session Status", test_terminal_session_status(session_id)))
        results["terminal"].append(("Get PWD", test_terminal_pwd(session_id)))
        results["terminal"].append(("Execute whoami", test_terminal_execute(session_id, "whoami")))
        results["terminal"].append(("Execute pwd", test_terminal_execute(session_id, "pwd")))
        results["terminal"].append(("Execute ls", test_terminal_execute(session_id, "ls -la | head -3")))
        results["terminal"].append(("Command History", test_terminal_history(session_id)))
    else:
        results["terminal"].append(("Session Create", False))
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    for test_name, test_results in [("Dashboard", results["dashboard"]), ("Terminal", results["terminal"])]:
        print(f"\n{test_name}:")
        passed = sum(1 for _, result in test_results if result)
        total = len(test_results)
        print(f"  Passed: {passed}/{total}")
        for name, result in test_results:
            status = "✅" if result else "❌"
            print(f"    {status} {name}")
    
    total_passed = sum(1 for tests in [results["dashboard"], results["terminal"]] for _, result in tests if result)
    total_tests = len(results["dashboard"]) + len(results["terminal"])
    
    print(f"\nOverall: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("\n🎉 ALL INTERACTIVE INTERFACES FUNCTIONING CORRECTLY! 🎉")
        return 0
    else:
        print(f"\n⚠️  {total_tests - total_passed} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
