#!/usr/bin/env python3
"""
Test script for Telegram authentication flows
"""
import requests
import time
from typing import Optional

BASE_URL = "https://movokio.com/api/v1/auth"
# For local testing, use:
# BASE_URL = "http://localhost:8000/api/v1/auth"


class TelegramAuthTester:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
    
    def test_token_flow(self, token: str):
        """
        Test manual token verification flow
        
        Before running this:
        1. Open @MovoKioBot in Telegram
        2. Send /login command
        3. Copy the 6-character token
        4. Pass it to this method
        """
        print(f"\n{'='*60}")
        print("Testing Token Verification Flow")
        print(f"{'='*60}")
        
        print(f"\n1. Verifying token: {token}")
        response = requests.post(
            f"{self.base_url}/telegram/verify-token",
            json={"token": token}
        )
        
        if response.status_code == 200:
            data = response.json()
            self.access_token = data.get("access_token")
            self.refresh_token = data.get("refresh_token")
            
            print("✓ Token verified successfully!")
            print(f"  - User ID: {data['user']['user_id']}")
            print(f"  - Telegram ID: {data['user']['telegram_id']}")
            print(f"  - Is new user: {data['is_new_user']}")
            print(f"  - Access token: {self.access_token[:20]}...")
            print(f"  - Refresh token: {self.refresh_token[:20]}...")
            
            return True
        else:
            print(f"✗ Failed to verify token")
            print(f"  Status: {response.status_code}")
            print(f"  Error: {response.json()}")
            return False
    
    def test_authenticated_request(self):
        """
        Test making an authenticated request with the JWT token
        """
        if not self.access_token:
            print("\n✗ No access token available. Complete token verification first.")
            return False
        
        print(f"\n{'='*60}")
        print("Testing Authenticated Request")
        print(f"{'='*60}")
        
        print("\n2. Fetching user profile...")
        response = requests.get(
            f"{self.base_url.replace('/auth', '')}/users/me",
            headers={"Authorization": f"Bearer {self.access_token}"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✓ Successfully fetched user profile!")
            print(f"  - User ID: {data['user_id']}")
            print(f"  - Telegram ID: {data.get('telegram_id')}")
            print(f"  - Credits: {data.get('credits', 0)}")
            return True
        else:
            print(f"✗ Failed to fetch profile")
            print(f"  Status: {response.status_code}")
            print(f"  Error: {response.text}")
            return False
    
    def test_token_refresh(self):
        """
        Test refreshing the access token
        """
        if not self.refresh_token:
            print("\n✗ No refresh token available.")
            return False
        
        print(f"\n{'='*60}")
        print("Testing Token Refresh")
        print(f"{'='*60}")
        
        print("\n3. Refreshing access token...")
        response = requests.post(
            f"{self.base_url}/refresh",
            json={"refresh_token": self.refresh_token}
        )
        
        if response.status_code == 200:
            data = response.json()
            old_token = self.access_token[:20]
            self.access_token = data.get("access_token")
            self.refresh_token = data.get("refresh_token")
            
            print("✓ Token refreshed successfully!")
            print(f"  - Old token: {old_token}...")
            print(f"  - New token: {self.access_token[:20]}...")
            return True
        else:
            print(f"✗ Failed to refresh token")
            print(f"  Status: {response.status_code}")
            print(f"  Error: {response.json()}")
            return False
    
    def test_webhook_setup(self):
        """
        Test webhook configuration status
        """
        print(f"\n{'='*60}")
        print("Checking Webhook Status")
        print(f"{'='*60}")
        
        bot_token = "8062210028:AAHt1fAFf3WVZnpdiDPOPOPMgOs4g3ZXu6s"
        
        print("\nFetching webhook info...")
        response = requests.get(
            f"https://api.telegram.org/bot{bot_token}/getWebhookInfo"
        )
        
        if response.status_code == 200:
            data = response.json()
            if data['ok']:
                result = data['result']
                print("✓ Webhook info retrieved!")
                print(f"  - URL: {result.get('url', 'Not set')}")
                print(f"  - Pending updates: {result.get('pending_update_count', 0)}")
                print(f"  - Last error: {result.get('last_error_message', 'None')}")
                
                if not result.get('url'):
                    print("\n⚠ Warning: Webhook URL is not set!")
                    print("  Run this command to set it:")
                    print(f"  curl -X POST 'https://api.telegram.org/bot{bot_token}/setWebhook' \\")
                    print(f"    -d 'url=https://movokio.com/api/v1/auth/telegram/webhook'")
                
                return True
        
        print(f"✗ Failed to get webhook info")
        return False


def main():
    """
    Main test runner
    """
    tester = TelegramAuthTester()
    
    print("\n" + "="*60)
    print("Telegram Authentication Test Suite")
    print("="*60)
    
    # Test 1: Check webhook status
    tester.test_webhook_setup()
    
    # Test 2: Token flow
    print("\n\n" + "="*60)
    print("Manual Token Login Test")
    print("="*60)
    print("\nInstructions:")
    print("1. Open Telegram and find @MovoKioBot")
    print("2. Send the command: /login")
    print("3. Copy the 6-character token you receive")
    print("4. Enter it below")
    print()
    
    token = input("Enter your token from Telegram (or press Enter to skip): ").strip()
    
    if token:
        if tester.test_token_flow(token):
            # Test authenticated requests
            tester.test_authenticated_request()
            
            # Test token refresh
            tester.test_token_refresh()
    else:
        print("\nSkipping token flow test.")
    
    # Summary
    print("\n\n" + "="*60)
    print("Test Summary")
    print("="*60)
    print("\nFor Automatic Login (Mini App):")
    print("  - Configure your web app with Telegram Web App SDK")
    print("  - Use window.Telegram.WebApp.initData")
    print("  - Send to /api/v1/auth/telegram/auto-login")
    print("\nFor Manual Token Login:")
    print("  - User sends /login to @MovoKioBot")
    print("  - User enters token on your website")
    print("  - Your site calls /api/v1/auth/telegram/verify-token")
    print()


if __name__ == "__main__":
    main()
