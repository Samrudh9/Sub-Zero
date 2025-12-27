#!/usr/bin/env python3
"""
Structural verification script that checks file existence and basic Python syntax
without requiring temporalio to be installed.
"""

import os
import ast

def verify_file_exists(filepath):
    """Check if file exists"""
    if os.path.exists(filepath):
        print(f"   ✓ {filepath} exists")
        return True
    else:
        print(f"   ✗ {filepath} NOT FOUND")
        return False

def verify_python_syntax(filepath):
    """Verify Python file has valid syntax"""
    try:
        with open(filepath, 'r') as f:
            code = f.read()
        ast.parse(code)
        print(f"   ✓ {filepath} has valid Python syntax")
        return True
    except SyntaxError as e:
        print(f"   ✗ {filepath} has syntax error: {e}")
        return False

def verify_function_exists(filepath, function_names):
    """Check if specific functions are defined in the file"""
    try:
        with open(filepath, 'r') as f:
            code = f.read()
        tree = ast.parse(code)
        
        # Find all async function definitions
        functions_found = []
        for node in ast.walk(tree):
            if isinstance(node, ast.AsyncFunctionDef):
                functions_found.append(node.name)
        
        all_found = True
        for func_name in function_names:
            if func_name in functions_found:
                print(f"   ✓ Function '{func_name}' defined")
            else:
                print(f"   ✗ Function '{func_name}' NOT FOUND")
                all_found = False
        
        return all_found
    except Exception as e:
        print(f"   ✗ Error checking functions: {e}")
        return False

print("=" * 60)
print("Sub-Zero Temporal Activities - Structure Verification")
print("=" * 60)

base_dir = os.path.dirname(os.path.abspath(__file__))
all_passed = True

print("\n1. Checking package structure...")
print("-" * 60)
all_passed &= verify_file_exists(f"{base_dir}/__init__.py")
all_passed &= verify_file_exists(f"{base_dir}/activities/__init__.py")
all_passed &= verify_file_exists(f"{base_dir}/activities/browser_activities.py")
all_passed &= verify_file_exists(f"{base_dir}/activities/notification_activities.py")
all_passed &= verify_file_exists(f"{base_dir}/workflows/cancellation_workflow.py")

print("\n2. Checking Python syntax...")
print("-" * 60)
all_passed &= verify_python_syntax(f"{base_dir}/__init__.py")
all_passed &= verify_python_syntax(f"{base_dir}/activities/__init__.py")
all_passed &= verify_python_syntax(f"{base_dir}/activities/browser_activities.py")
all_passed &= verify_python_syntax(f"{base_dir}/activities/notification_activities.py")

print("\n3. Checking browser_activities.py functions...")
print("-" * 60)
all_passed &= verify_function_exists(
    f"{base_dir}/activities/browser_activities.py",
    ["start_cancellation", "inject_2fa_code", "capture_proof"]
)

print("\n4. Checking notification_activities.py functions...")
print("-" * 60)
all_passed &= verify_function_exists(
    f"{base_dir}/activities/notification_activities.py",
    ["send_push_notification"]
)

print("\n5. Checking __init__.py exports...")
print("-" * 60)
with open(f"{base_dir}/activities/__init__.py", 'r') as f:
    init_content = f.read()
    exports_to_check = [
        "start_cancellation",
        "inject_2fa_code", 
        "capture_proof",
        "send_push_notification"
    ]
    for export in exports_to_check:
        if export in init_content:
            print(f"   ✓ '{export}' exported in __init__.py")
        else:
            print(f"   ✗ '{export}' NOT exported in __init__.py")
            all_passed = False

print("\n" + "=" * 60)
if all_passed:
    print("✅ All structural checks passed!")
    print("=" * 60)
    print("\nNote: Actual imports require temporalio to be installed.")
    print("The structure is correct and ready for Temporal runtime.")
else:
    print("❌ Some checks failed!")
    print("=" * 60)
    exit(1)
