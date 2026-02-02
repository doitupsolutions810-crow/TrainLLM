#!/usr/bin/env python3
import sys
sys.path.insert(0, 'TrainLLM')
from voidos_app_launcher import AppLauncher
launcher = AppLauncher()
apps = launcher.list_apps()
print("VOIDS DASHBOARD SYSTEM TEST")
print("="*60)
print(f"Total Apps: {len(apps)}")
for app in apps:
    print(f"  - {app['name']} ({app['id']})")
print("="*60)
print("✅ SYSTEM OPERATIONAL")
