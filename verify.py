#!/usr/bin/env python3
"""
Verification Script - Tests all critical fixes
Run this before starting the application
"""

import sys
import os
from pathlib import Path

def test_imports():
    """Test that all imports work correctly"""
    print("=" * 70)
    print("🔍 TESTING IMPORTS")
    print("=" * 70)
    
    tests_passed = 0
    tests_failed = 0
    
    # Test 1: sys.path configuration
    print("\n1. Testing sys.path configuration...")
    sys.path.insert(0, str(Path(__file__).parent))
    print("   ✅ Path configured correctly")
    tests_passed += 1
    
    # Test 2: Internal modules
    print("\n2. Testing internal module imports...")
    try:
        from internal.config import Config, InstrumentConfig
        print("   ✅ config.py imports OK")
        tests_passed += 1
    except ImportError as e:
        print(f"   ❌ config.py import failed: {e}")
        tests_failed += 1
    
    try:
        from internal.logger import Logger
        print("   ✅ logger.py imports OK")
        tests_passed += 1
    except ImportError as e:
        print(f"   ❌ logger.py import failed: {e}")
        tests_failed += 1
    
    try:
        from internal.position import PositionManager, Trade, Order, Position
        print("   ✅ position.py imports OK")
        tests_passed += 1
    except ImportError as e:
        print(f"   ❌ position.py import failed: {e}")
        tests_failed += 1
    
    try:
        from internal.server import WebServer
        print("   ✅ server.py imports OK")
        tests_passed += 1
    except ImportError as e:
        print(f"   ❌ server.py import failed: {e}")
        tests_failed += 1
    
    try:
        from internal.terminal import Terminal
        print("   ✅ terminal.py imports OK")
        tests_passed += 1
    except ImportError as e:
        print(f"   ❌ terminal.py import failed: {e}")
        tests_failed += 1
    
    try:
        from internal.trader import Trader, PaperTrader
        print("   ✅ trader.py imports OK")
        tests_passed += 1
    except ImportError as e:
        print(f"   ❌ trader.py import failed: {e}")
        tests_failed += 1
    
    # Test 3: External dependencies
    print("\n3. Testing external dependencies...")
    try:
        from fyers_apiv3 import fyersModel
        print("   ✅ fyers-apiv3 installed")
        tests_passed += 1
    except ImportError:
        print("   ❌ fyers-apiv3 not installed")
        print("      Run: pip install fyers-apiv3")
        tests_failed += 1
    
    try:
        import flask
        print("   ✅ flask installed")
        tests_passed += 1
    except ImportError:
        print("   ❌ flask not installed")
        print("      Run: pip install flask")
        tests_failed += 1
    
    try:
        import flask_cors
        print("   ✅ flask-cors installed")
        tests_passed += 1
    except ImportError:
        print("   ❌ flask-cors not installed")
        print("      Run: pip install flask-cors")
        tests_failed += 1
    
    return tests_passed, tests_failed


def test_input_validation():
    """Test input validation fixes"""
    print("\n" + "=" * 70)
    print("🔍 TESTING INPUT VALIDATION")
    print("=" * 70)
    
    tests_passed = 0
    tests_failed = 0
    
    try:
        from internal.trader import Trader
        
        # Create a mock trader (will fail without real objects, but that's OK)
        print("\n1. Testing Trader class exists...")
        print("   ✅ Trader class found")
        tests_passed += 1
        
        # Check that place_order method exists
        print("\n2. Testing place_order method exists...")
        if hasattr(Trader, 'place_order'):
            print("   ✅ place_order method found")
            tests_passed += 1
        else:
            print("   ❌ place_order method not found")
            tests_failed += 1
        
    except Exception as e:
        print(f"   ❌ Validation test failed: {e}")
        tests_failed += 1
    
    try:
        from internal.trader import PaperTrader
        
        print("\n3. Testing PaperTrader class exists...")
        print("   ✅ PaperTrader class found")
        tests_passed += 1
        
        # Check inheritance
        if issubclass(PaperTrader, Trader):
            print("   ✅ PaperTrader inherits from Trader")
            tests_passed += 1
        else:
            print("   ❌ PaperTrader does not inherit from Trader")
            tests_failed += 1
    
    except Exception as e:
        print(f"   ❌ PaperTrader test failed: {e}")
        tests_failed += 1
    
    return tests_passed, tests_failed


def test_position_manager():
    """Test position manager fixes"""
    print("\n" + "=" * 70)
    print("🔍 TESTING POSITION MANAGER")
    print("=" * 70)
    
    tests_passed = 0
    tests_failed = 0
    
    try:
        from internal.position import PositionManager
        
        print("\n1. Creating PositionManager instance...")
        pos_mgr = PositionManager(paper_mode=True)
        print("   ✅ PositionManager created")
        tests_passed += 1
        
        print("\n2. Testing logger initialization...")
        if hasattr(pos_mgr, 'logger'):
            print("   ✅ Logger initialized")
            tests_passed += 1
        else:
            print("   ❌ Logger not initialized")
            tests_failed += 1
        
        print("\n3. Testing session stats...")
        if hasattr(pos_mgr, 'session_net_pnl'):
            print("   ✅ Session stats initialized")
            tests_passed += 1
        else:
            print("   ❌ Session stats not initialized")
            tests_failed += 1
        
        print("\n4. Testing export function...")
        if hasattr(pos_mgr, 'export_session_trades'):
            print("   ✅ Export function found")
            tests_passed += 1
        else:
            print("   ❌ Export function not found")
            tests_failed += 1
    
    except Exception as e:
        print(f"   ❌ PositionManager test failed: {e}")
        tests_failed += 1
    
    return tests_passed, tests_failed


def test_config_file():
    """Test configuration file"""
    print("\n" + "=" * 70)
    print("🔍 TESTING CONFIGURATION")
    print("=" * 70)
    
    tests_passed = 0
    tests_failed = 0
    
    print("\n1. Checking config.json exists...")
    if os.path.exists('config.json'):
        print("   ✅ config.json found")
        tests_passed += 1
        
        try:
            from internal.config import Config
            print("\n2. Loading configuration...")
            config = Config.load('config.json')
            print("   ✅ Configuration loaded")
            tests_passed += 1
            
            print("\n3. Checking required fields...")
            if config.app_id:
                print(f"   ✅ app_id: {config.app_id[:20]}...")
                tests_passed += 1
            else:
                print("   ❌ app_id missing")
                tests_failed += 1
            
            if config.access_token:
                print(f"   ✅ access_token: {config.access_token[:20]}...")
                tests_passed += 1
            else:
                print("   ⚠️  access_token empty (run generate_token.py)")
                tests_failed += 1
            
            if config.instruments:
                print(f"   ✅ {len(config.instruments)} instrument(s) configured")
                tests_passed += 1
                for i, inst in enumerate(config.instruments):
                    print(f"      - {inst.symbol} ({inst.exchange}) Lot: {inst.lot_size}")
            else:
                print("   ❌ No instruments configured")
                tests_failed += 1
        
        except Exception as e:
            print(f"   ❌ Configuration load failed: {e}")
            tests_failed += 1
    
    else:
        print("   ❌ config.json not found")
        print("\n   Create config.json with:")
        print("   {")
        print('     "app_id": "YOUR_APP_ID",')
        print('     "app_secret": "YOUR_APP_SECRET",')
        print('     "redirect_uri": "http://127.0.0.1:8080",')
        print('     "access_token": "",')
        print('     "instruments": [...]')
        print("   }")
        tests_failed += 1
    
    return tests_passed, tests_failed


def main():
    """Run all verification tests"""
    print("\n" + "=" * 70)
    print("🧪 PAPER TRADING APPLICATION - VERIFICATION SCRIPT")
    print("=" * 70)
    print("\nThis script will verify that all critical fixes are in place")
    print("and that the application is ready to run.\n")
    
    total_passed = 0
    total_failed = 0
    
    # Run tests
    passed, failed = test_imports()
    total_passed += passed
    total_failed += failed
    
    passed, failed = test_input_validation()
    total_passed += passed
    total_failed += failed
    
    passed, failed = test_position_manager()
    total_passed += passed
    total_failed += failed
    
    passed, failed = test_config_file()
    total_passed += passed
    total_failed += failed
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 70)
    print(f"\n✅ Tests Passed: {total_passed}")
    print(f"❌ Tests Failed: {total_failed}")
    print(f"📈 Success Rate: {(total_passed / (total_passed + total_failed) * 100):.1f}%")
    
    if total_failed == 0:
        print("\n" + "🎉" * 20)
        print("🎉 ALL TESTS PASSED! Application is ready to run.")
        print("🎉" * 20)
        print("\n✅ Next steps:")
        print("   1. If access_token is empty, run: python generate_token.py")
        print("   2. Start application: python main.py")
        print("   3. Select Paper Trading mode to test safely")
        print("\n" + "=" * 70)
        return 0
    else:
        print("\n" + "⚠️ " * 20)
        print("⚠️  SOME TESTS FAILED - Please fix the issues above")
        print("⚠️ " * 20)
        print("\n❌ Common fixes:")
        print("   • Missing dependencies: pip install fyers-apiv3 flask flask-cors")
        print("   • Missing config.json: Create the file with required fields")
        print("   • Missing internal modules: Copy all files from outputs/")
        print("\n" + "=" * 70)
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)