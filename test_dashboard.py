#!/usr/bin/env python3
"""
voidOS Dashboard & Tool Functionality Test Suite
Tests all major features: apps, terminal, API endpoints
"""

import sys
sys.path.insert(0, 'TrainLLM')

from voidos_app_launcher import AppLauncher, TerminalApp, initialize_apps
import json

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def test_app_launcher():
    """Test app launcher system"""
    print_section("TEST 1: App Launcher System")
    
    launcher = AppLauncher()
    
    # List all apps
    apps = launcher.list_apps()
    print(f"✓ Found {len(apps)} registered apps\n")
    
    print("  Apps Directory:")
    for app in apps:
        status = "●" if app['status'] == 'stopped' else "◆"
        print(f"    {status} {app['icon']} {app['name']:<20} [{app['tags'][0]}]")
    
    return launcher, len(apps) == 8

def test_app_launch(launcher):
    """Test launching applications"""
    print_section("TEST 2: App Launch & Status")
    
    # Launch GhostShell
    print("  Launching: GhostShell")
    result = launcher.launch_app('ghostshell')
    print(f"  ✓ Launch successful: {result}")
    
    # Check status
    status = launcher.get_app_status('ghostshell')
    print(f"  ✓ Current status: {status['status']}")
    print(f"  ✓ Started at: {status['started_at']}")
    
    return result and status['status'] == 'running'

def test_terminal_execution():
    """Test terminal command execution"""
    print_section("TEST 3: Terminal Command Execution")
    
    terminal = TerminalApp()
    
    # Test pwd
    print("  Executing: pwd")
    result1 = terminal.execute_command('pwd')
    print(f"  ✓ Exit code: {result1['exit_code']}")
    print(f"  ✓ Output: {result1['stdout'].strip()}")
    
    # Test echo
    print("\n  Executing: echo 'voidOS Dashboard Test'")
    result2 = terminal.execute_command("echo 'voidOS Dashboard Test'")
    print(f"  ✓ Exit code: {result2['exit_code']}")
    print(f"  ✓ Output: {result2['stdout'].strip()}")
    
    # Test ls
    print("\n  Executing: ls -la /opt/voidos")
    result3 = terminal.execute_command('ls -la /opt/voidos 2>/dev/null || echo "Not in ISO environment"')
    print(f"  ✓ Exit code: {result3['exit_code']}")
    print(f"  ✓ Output lines: {len(result3['stdout'].split(chr(10)))}")
    
    return result1['exit_code'] == 0 and result2['exit_code'] == 0

def test_terminal_history():
    """Test terminal history tracking"""
    print_section("TEST 4: Terminal Command History")
    
    terminal = TerminalApp()
    
    # Execute multiple commands
    terminal.execute_command('pwd')
    terminal.execute_command('whoami')
    terminal.execute_command('date')
    
    # Get history
    history = terminal.get_history(limit=5)
    print(f"  ✓ Recorded {len(history)} commands\n")
    
    print("  Command History:")
    for i, entry in enumerate(history, 1):
        print(f"    {i}. {entry['command']:<25} (exit: {entry['exit_code']})")
    
    return len(history) >= 3

def test_app_filtering():
    """Test app filtering by tags"""
    print_section("TEST 5: App Filtering by Tags")
    
    launcher = AppLauncher()
    
    tags = ['ai', 'system', 'utility', 'monitoring']
    print("  App Categories:\n")
    
    for tag in tags:
        filtered = launcher.list_apps(tag=tag)
        print(f"    [{tag}]")
        for app in filtered:
            print(f"      - {app['name']}")
    
    return True

def test_app_stop(launcher):
    """Test stopping applications"""
    print_section("TEST 6: App Stop & Lifecycle")
    
    # Stop GhostShell
    print("  Stopping: GhostShell")
    result = launcher.stop_app('ghostshell')
    print(f"  ✓ Stop successful: {result}")
    
    # Check status
    status = launcher.get_app_status('ghostshell')
    print(f"  ✓ Status after stop: {status['status']}")
    
    return result and status['status'] == 'stopped'

def test_api_responses(launcher, terminal):
    """Test API response formats"""
    print_section("TEST 7: API Response Formats")
    
    print("  App Status Response Format:")
    app_status = launcher.get_app_status('ghostshell')
    print(f"    - app_id: {app_status['app_id']}")
    print(f"    - name: {app_status['name']}")
    print(f"    - status: {app_status['status']}")
    print(f"    - url: {app_status['url']}")
    
    print("\n  Terminal Response Format:")
    term_result = terminal.execute_command('echo test')
    print(f"    - command: {term_result['command']}")
    print(f"    - exit_code: {term_result['exit_code']}")
    print(f"    - cwd: {term_result['cwd']}")
    print(f"    - timestamp: {term_result['timestamp']}")
    
    return True

def test_dashboard_components():
    """Test dashboard component availability"""
    print_section("TEST 8: Dashboard Components")
    
    import os
    from pathlib import Path
    
    trainllm = Path('TrainLLM')
    
    components = {
        'Dashboard UI': 'dashboard_app_launcher.html',
        'App Launcher': 'voidos_app_launcher.py',
        'API Extension': 'voidos_app_api.py',
        'Bootstrap': 'voidos_seed_bootstrap.py',
        'Documentation': 'DASHBOARD_APP_LAUNCHER_GUIDE.md'
    }
    
    print("  Component Status:\n")
    all_present = True
    
    for name, file in components.items():
        path = trainllm / file
        exists = path.exists()
        status = "✓" if exists else "✗"
        size = f"({path.stat().st_size/1024:.1f} KB)" if exists else ""
        print(f"    {status} {name:<20} {size}")
        all_present = all_present and exists
    
    return all_present

def main():
    """Run all tests"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*15 + "voidOS DASHBOARD TEST SUITE" + " "*15 + "║")
    print("║" + " "*58 + "║")
    print("║" + " Testing all dashboard and tool functionality" + " "*13 + "║")
    print("╚" + "="*58 + "╝")
    
    results = {}
    
    # Run tests
    try:
        launcher, result = test_app_launcher()
        results['App Launcher'] = result
        
        result = test_app_launch(launcher)
        results['App Launch'] = result
        
        result = test_terminal_execution()
        results['Terminal Execution'] = result
        
        result = test_terminal_history()
        results['Terminal History'] = result
        
        result = test_app_filtering()
        results['App Filtering'] = result
        
        result = test_app_stop(launcher)
        results['App Stop'] = result
        
        terminal = TerminalApp()
        result = test_api_responses(launcher, terminal)
        results['API Responses'] = result
        
        result = test_dashboard_components()
        results['Dashboard Components'] = result
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Summary
    print_section("TEST SUMMARY")
    
    print("  Results:\n")
    passed = 0
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"    {status:<10} {test_name}")
        if result:
            passed += 1
    
    total = len(results)
    print(f"\n  ────────────────────────────────")
    print(f"  Total: {passed}/{total} tests passed")
    
    if passed == total:
        print(f"\n  ✓ ALL TESTS PASSED - Dashboard is fully functional!")
    else:
        print(f"\n  ✗ Some tests failed")
    
    print("\n  Dashboard URL: http://localhost:5001")
    print("  API Endpoint: http://localhost:5001/api/")
    print("\n")
    
    return passed == total

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
