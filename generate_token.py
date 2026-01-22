#!/usr/bin/env python3
"""
Fyers Token Generator
Generates access token for trading (valid until 6 AM IST next day)
"""

import json
import sys
from fyers_apiv3 import fyersModel

def generate_token():
    """Generate Fyers access token"""
    try:
        # Load config
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        app_id = config.get('app_id')
        app_secret = config.get('app_secret')
        redirect_uri = config.get('redirect_uri')
        
        if not app_id or not app_secret or not redirect_uri:
            print("❌ Error: app_id, app_secret, and redirect_uri required in config.json")
            print("\nPlease add these fields to your config.json:")
            print('  "app_id": "YOUR_APP_ID",')
            print('  "app_secret": "YOUR_APP_SECRET",')
            print('  "redirect_uri": "http://127.0.0.1:8080"')
            return False
        
        # Create session
        session = fyersModel.SessionModel(
            client_id=app_id,
            secret_key=app_secret,
            redirect_uri=redirect_uri,
            response_type="code",
            grant_type="authorization_code"
        )
        
        # Generate auth code URL
        auth_url = session.generate_authcode()
        
        print("=" * 70)
        print("🔐 FYERS TOKEN GENERATION")
        print("=" * 70)
        print("\n1. Open this URL in your browser:")
        print(f"\n   {auth_url}\n")
        print("2. Login to your Fyers account")
        print("3. Copy the entire redirect URL from your browser")
        print("   (It will look like: http://127.0.0.1:8080/?auth_code=...&state=...)")
        print("\n" + "=" * 70)
        
        # Get auth code from user
        redirect_response = input("\nPaste the redirect URL here: ").strip()
        
        if not redirect_response:
            print("❌ No URL provided")
            return False
        
        # Extract auth code
        if 'auth_code=' not in redirect_response:
            print("❌ Invalid URL - auth_code not found")
            return False
        
        try:
            auth_code = redirect_response.split('auth_code=')[1].split('&')[0]
        except IndexError:
            print("❌ Could not extract auth_code from URL")
            return False
        
        # Set auth code
        session.set_token(auth_code)
        
        # Generate access token
        response = session.generate_token()
        
        if 'access_token' not in response:
            print(f"❌ Token generation failed: {response}")
            return False
        
        access_token = response['access_token']
        
        # Update config with new token
        config['access_token'] = access_token
        
        with open('config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        print("\n" + "=" * 70)
        print("✅ SUCCESS! Access token generated and saved to config.json")
        print("=" * 70)
        print(f"\n📅 Token valid until: 6:00 AM IST tomorrow")
        print(f"🔑 Token: {access_token[:20]}...{access_token[-10:]}")
        print("\n💡 You can now run: python main.py")
        print("=" * 70)
        
        return True
        
    except FileNotFoundError:
        print("❌ Error: config.json not found")
        print("\nCreate a config.json file with:")
        print('{')
        print('  "app_id": "YOUR_APP_ID",')
        print('  "app_secret": "YOUR_APP_SECRET",')
        print('  "redirect_uri": "http://127.0.0.1:8080",')
        print('  "access_token": "",')
        print('  "instruments": [')
        print('    {')
        print('      "symbol": "NSE:NIFTY24JAN26000CE",')
        print('      "exchange": "NSE",')
        print('      "lot_size": 25,')
        print('      "product": "INTRADAY"')
        print('    }')
        print('  ]')
        print('}')
        return False
        
    except json.JSONDecodeError:
        print("❌ Error: Invalid JSON in config.json")
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = generate_token()
    sys.exit(0 if success else 1)