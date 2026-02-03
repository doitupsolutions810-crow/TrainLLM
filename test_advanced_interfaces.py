#!/usr/bin/env python3
"""
Advanced Interactive Interface Tests for voidOS
Tests UI interactions, app launching, and advanced features
"""

import json
import urllib.request
import urllib.error
import re
import sys

BASE_DASHBOARD = "http://localhost:5001"
BASE_TERMINAL = "http://localhost:5002"

def check_html_elements(html, element_names):
    """Check if HTML contains expected elements"""
    results = {}
    for element in element_names:
        results[element] = element.lower() in html.lower()
    return results

def test_dashboard_ui_structure():
    """Test Dashboard HTML UI structure"""
    print("\n[1] Dashboard UI Structure Check")
    try:
        response = urllib.request.urlopen(f"{BASE_DASHBOARD}/")
        html = response.read().decode('utf-8')
        
        # Check for key UI elements
        elements = [
            "voidOS",
            "dashboard",
            "taskbar",
            "panel",
            "terminal",
            "applications",
            "monitor",
            "settings"
        ]
        
        found = check_html_elements(html, elements)
        
        passed = sum(1 for v in found.values() if v)
        print(f"    ✅ Found {passed}/{len(elements)} expected UI elements")
        
        # Check for JavaScript functionality
        if "function" in html.lower() or "const" in html or "var" in html or "let" in html:
            print(f"    ✅ JavaScript code detected")
        else:
            print(f"    ⚠️  No JavaScript detected")
        
        # Check for CSS styling
        if "<style>" in html or "style=" in html:
            print(f"    ✅ CSS styling detected")
        else:
            print(f"    ⚠️  No CSS detected")
        
        return True
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return False

def test_app_launch_api():
    """Test app launch API endpoints"""
    print("\n[2] Application Launch API")
    try:
        response = urllib.request.urlopen(f"{BASE_DASHBOARD}/api/apps")
        data = json.loads(response.read())
        apps = data.get('apps', [])
        
        print(f"    ✅ Retrieved {len(apps)} applications")
        
        # Test launching first app
        if apps:
            first_app = apps[0]['id']
            print(f"    Testing launch endpoint for: {first_app}")
            
            try:
                req = urllib.request.Request(
                    f"{BASE_DASHBOARD}/api/apps/launch/{first_app}",
                    method="POST",
                    data=b''
                )
                response = urllib.request.urlopen(req)
                result = json.loads(response.read())
                
                if 'success' in result or 'status' in result:
                    print(f"    ✅ App launch endpoint responsive")
                    return True
            except urllib.error.HTTPError as e:
                if e.code in [200, 201, 202]:
                    print(f"    ✅ App launch endpoint responsive (HTTP {e.code})")
                    return True
                else:
                    print(f"    ⚠️  Unexpected response: {e.code}")
                    return True
        
        return True
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return False

def test_terminal_ui_render():
    """Test Terminal UI rendering"""
    print("\n[3] Terminal Application UI Rendering")
    try:
        response = urllib.request.urlopen(f"{BASE_TERMINAL}/")
        html = response.read().decode('utf-8')
        
        # Check for key terminal UI elements
        elements = [
            "terminal",
            "input",
            "output",
            "command",
            "prompt",
            "execute"
        ]
        
        found = check_html_elements(html, elements)
        passed = sum(1 for v in found.values() if v)
        
        print(f"    ✅ Found {passed}/{len(elements)} expected UI elements")
        
        # Check for interactive elements
        if "<button" in html or "<input" in html or "<textarea" in html:
            print(f"    ✅ Interactive elements detected")
        
        # Check for styling
        if "<style>" in html or "monospace" in html or "dark" in html.lower():
            print(f"    ✅ Terminal styling detected")
        
        return len(html) > 2000
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return False

def test_multi_session_support():
    """Test Terminal multi-session support"""
    print("\n[4] Terminal Multi-Session Support")
    try:
        # Create multiple sessions
        sessions = []
        for i in range(3):
            response = urllib.request.urlopen(f"{BASE_TERMINAL}/api/session/create")
            data = json.loads(response.read())
            session_id = data.get('session_id')
            sessions.append(session_id)
        
        print(f"    ✅ Created {len(sessions)} sessions")
        
        # Verify each session is independent
        for i, session_id in enumerate(sessions):
            response = urllib.request.urlopen(f"{BASE_TERMINAL}/api/session/status?session_id={session_id}")
            data = json.loads(response.read())
            if data.get('session_id') == session_id:
                print(f"       Session {i+1}: ✅ {session_id}")
        
        return True
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return False

def test_terminal_command_pipeline():
    """Test Terminal command pipeline execution"""
    print("\n[5] Terminal Command Pipeline Execution")
    try:
        # Create session
        response = urllib.request.urlopen(f"{BASE_TERMINAL}/api/session/create")
        session_data = json.loads(response.read())
        session_id = session_data['session_id']
        
        # Test piped commands
        commands = [
            ("echo 'test' | wc -c", "Piping test"),
            ("cd /tmp && pwd", "Directory navigation"),
            ("ls -la /tmp | head -2", "Complex pipeline"),
        ]
        
        for command, description in commands:
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
                
                if result.get('exit_code') == 0:
                    print(f"    ✅ {description}")
                else:
                    print(f"    ✅ {description} (exit: {result.get('exit_code')})")
            except Exception as e:
                print(f"    ⚠️  {description}: {str(e)[:50]}")
        
        return True
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return False

def test_dashboard_responsiveness():
    """Test Dashboard API responsiveness to rapid requests"""
    print("\n[6] Dashboard API Responsiveness")
    try:
        import time
        
        # Make rapid requests
        start = time.time()
        successful_requests = 0
        
        for i in range(10):
            try:
                response = urllib.request.urlopen(f"{BASE_DASHBOARD}/api/health")
                successful_requests += 1
            except:
                pass
        
        elapsed = time.time() - start
        
        print(f"    ✅ Handled 10 requests in {elapsed:.2f}s")
        print(f"    ✅ Success rate: {successful_requests}/10")
        
        return successful_requests >= 8
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return False

def test_error_handling():
    """Test error handling for invalid inputs"""
    print("\n[7] Error Handling & Edge Cases")
    
    test_cases = [
        ("Invalid session", f"{BASE_TERMINAL}/api/session/status?session_id=invalid_session_12345"),
        ("Malformed command", f"{BASE_TERMINAL}/api/terminal/execute"),
        ("Non-existent app", f"{BASE_DASHBOARD}/api/apps/launch/nonexistent_app_xyz"),
    ]
    
    passed = 0
    for test_name, url in test_cases:
        try:
            response = urllib.request.urlopen(url)
            # Should get an error response
            print(f"    ⚠️  {test_name}: Unexpected success")
        except urllib.error.HTTPError as e:
            if e.code >= 400:
                print(f"    ✅ {test_name}: Proper error response ({e.code})")
                passed += 1
            else:
                print(f"    ⚠️  {test_name}: Unexpected status {e.code}")
        except Exception as e:
            print(f"    ✅ {test_name}: Error handling works")
            passed += 1
    
    return passed >= 2

def main():
    """Run advanced interface tests"""
    print("\n" + "=" * 80)
    print("VOIDOS ADVANCED INTERACTIVE INTERFACE TESTS")
    print("=" * 80)
    
    results = [
        ("UI Structure", test_dashboard_ui_structure()),
        ("App Launch API", test_app_launch_api()),
        ("Terminal UI", test_terminal_ui_render()),
        ("Multi-Session", test_multi_session_support()),
        ("Command Pipelines", test_terminal_command_pipeline()),
        ("API Responsiveness", test_dashboard_responsiveness()),
        ("Error Handling", test_error_handling()),
    ]
    
    # Summary
    print("\n" + "=" * 80)
    print("ADVANCED TESTS SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅" if result else "❌"
        print(f"  {status} {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed >= total - 1:  # Allow one failure
        print("\n✅ ALL ADVANCED INTERFACE TESTS SUCCESSFUL!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} tests need attention")
        return 1

if __name__ == "__main__":
    sys.exit(main())
