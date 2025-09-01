"""
Test script to verify app startup
"""

import os
import sys

def test_imports():
    """Test that all required modules can be imported"""
    try:
        print("Testing imports...")
        from src.web.app import create_app
        print(" App imports successful")
        return True
    except Exception as e:
        print(f" Import failed: {e}")
        return False

def test_app_creation():
    """Test that the app can be created"""
    try:
        print("Testing app creation...")
        from src.web.app import create_app
        app, socketio = create_app()
        print("App creation successful")
        return True
    except Exception as e:
        print(f"App creation failed: {e}")
        return False

def test_port_config():
    """Test port configuration"""
    try:
        print("Testing port configuration...")
        port = int(os.environ.get('PORT', 5000))
        print(f" Port configuration: {port}")
        return True
    except Exception as e:
        print(f" Port configuration failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Running startup tests...")
    
    tests = [
        test_imports,
        test_app_creation,
        test_port_config
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print(" All tests passed - app should start successfully")
        return 0
    else:
        print(" Some tests failed - check the errors above")
        return 1

if __name__ == '__main__':
    sys.exit(main())
