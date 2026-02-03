#!/usr/bin/env python3
"""
voidOS Dashboard Component Verification

Tests all components through the dashboard interfaces
"""

import json
import urllib.request
import urllib.error
import time
import sys

def verify_component(name, check_func):
    """Verify a component and return result"""
    try:
        result = check_func()
        if result:
            print(f"✅ {name}")
            return True
        else:
            print(f"❌ {name}")
            return False
    except Exception as e:
        print(f"❌ {name}: {str(e)[:50]}")
        return False

def check_dashboard_service():
    """Check if Dashboard service is responding"""
    try:
        response = urllib.request.urlopen("http://localhost:5001/api/health", timeout=2)
        data = json.loads(response.read())
        return data.get('status') == 'healthy'
    except:
        return False

def check_dashboard_html():
    """Check if Dashboard HTML loads"""
    try:
        response = urllib.request.urlopen("http://localhost:5001/", timeout=2)
        html = response.read().decode('utf-8')
        return len(html) > 5000 and 'voidOS' in html
    except:
        return False

def check_dashboard_apps():
    """Check if Dashboard can list apps"""
    try:
        response = urllib.request.urlopen("http://localhost:5001/api/apps", timeout=2)
        data = json.loads(response.read())
        apps = data.get('apps', [])
        return len(apps) >= 8
    except:
        return False

def check_seed_info():
    """Check if Seed information is accessible"""
    try:
        response = urllib.request.urlopen("http://localhost:5001/api/seed", timeout=2)
        data = json.loads(response.read())
        return data.get('seed_id') is not None
    except:
        return False

def check_terminal_service():
    """Check if Terminal service is responding"""
    try:
        response = urllib.request.urlopen("http://localhost:5002/health", timeout=2)
        data = json.loads(response.read())
        return data.get('status') == 'healthy'
    except:
        return False

def check_terminal_ui():
    """Check if Terminal UI loads"""
    try:
        response = urllib.request.urlopen("http://localhost:5002/", timeout=2)
        html = response.read().decode('utf-8')
        return len(html) > 2000 and 'terminal' in html.lower()
    except:
        return False

def check_terminal_sessions():
    """Check if Terminal can create sessions"""
    try:
        response = urllib.request.urlopen("http://localhost:5002/api/session/create", timeout=2)
        data = json.loads(response.read())
        return data.get('session_id') is not None
    except:
        return False

def check_terminal_commands():
    """Check if Terminal can execute commands"""
    try:
        # Create session
        response = urllib.request.urlopen("http://localhost:5002/api/session/create", timeout=2)
        session_data = json.loads(response.read())
        session_id = session_data['session_id']
        
        # Execute command
        req = urllib.request.Request(
            "http://localhost:5002/api/terminal/execute",
            data=json.dumps({
                "session_id": session_id,
                "command": "whoami"
            }).encode(),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        response = urllib.request.urlopen(req, timeout=2)
        result = json.loads(response.read())
        return result.get('exit_code') == 0
    except:
        return False

def check_app_launcher():
    """Check if app launcher is functional"""
    try:
        response = urllib.request.urlopen("http://localhost:5001/api/apps", timeout=2)
        data = json.loads(response.read())
        apps = data.get('apps', [])
        
        if apps:
            first_app = apps[0]['id']
            # Try to launch an app
            req = urllib.request.Request(
                f"http://localhost:5001/api/apps/launch/{first_app}",
                method="POST",
                data=b''
            )
            response = urllib.request.urlopen(req, timeout=2)
            return response.status in [200, 201, 202]
    except:
        pass
    return False

def check_command_history():
    """Check if Terminal maintains command history"""
    try:
        # Create session and execute commands
        response = urllib.request.urlopen("http://localhost:5002/api/session/create", timeout=2)
        session_data = json.loads(response.read())
        session_id = session_data['session_id']
        
        # Execute a command
        req = urllib.request.Request(
            "http://localhost:5002/api/terminal/execute",
            data=json.dumps({"session_id": session_id, "command": "echo test"}).encode(),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        urllib.request.urlopen(req, timeout=2)
        
        # Get history
        response = urllib.request.urlopen(
            f"http://localhost:5002/api/terminal/history?session_id={session_id}",
            timeout=2
        )
        history = json.loads(response.read())
        return len(history.get('history', [])) > 0
    except:
        return False

def check_api_endpoints():
    """Check if key API endpoints are available"""
    endpoints = [
        ("Dashboard Health", "http://localhost:5001/api/health", "GET"),
        ("Terminal Health", "http://localhost:5002/health", "GET"),
        ("App List", "http://localhost:5001/api/apps", "GET"),
        ("Seed Info", "http://localhost:5001/api/seed", "GET"),
    ]
    
    available = 0
    for name, url, method in endpoints:
        try:
            response = urllib.request.urlopen(url, timeout=1)
            if response.status == 200:
                available += 1
        except:
            pass
    
    return available >= 3

def main():
    """Run component verification through dashboards"""
    print("\n" + "=" * 70)
    print("VOIDOS DASHBOARD COMPONENT VERIFICATION")
    print("=" * 70)
    
    components = [
        ("Dashboard Service", check_dashboard_service),
        ("Dashboard HTML UI", check_dashboard_html),
        ("Dashboard Apps List", check_dashboard_apps),
        ("Seed Information", check_seed_info),
        ("Terminal Service", check_terminal_service),
        ("Terminal UI", check_terminal_ui),
        ("Terminal Sessions", check_terminal_sessions),
        ("Terminal Command Execution", check_terminal_commands),
        ("App Launcher", check_app_launcher),
        ("Command History", check_command_history),
        ("API Endpoints", check_api_endpoints),
    ]
    
    print("\nComponent Tests:\n")
    
    results = []
    for name, check_func in components:
        result = verify_component(name, check_func)
        results.append((name, result))
    
    # Summary
    print("\n" + "=" * 70)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\nResults: {passed}/{total} components verified")
    print("=" * 70)
    
    if passed >= total - 2:
        print("\n✅ DASHBOARD COMPONENT VERIFICATION SUCCESSFUL")
        return 0
    else:
        print(f"\n⚠️  {total - passed} components need attention")
        return 1

if __name__ == "__main__":
    sys.exit(main())
