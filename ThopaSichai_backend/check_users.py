#!/usr/bin/env python
"""
User and Token Management Script
Run this to see all registered users and their tokens
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, '/home/bipul/Bipul/ThopaSichai/ThopaSichai_backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ThopaSichai_backend.settings')
django.setup()

from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.utils import timezone

print("=" * 70)
print("📊 THOPA SICHAI - USER & TOKEN MANAGEMENT")
print("=" * 70)
print()

# List all users
users = User.objects.all()
print(f"👥 Total Users: {users.count()}")
print("-" * 70)

for user in users:
    print(f"\n🔹 User ID: {user.id}")
    print(f"   Username: {user.username}")
    print(f"   Email: {user.email}")
    print(f"   Full Name: {user.first_name} {user.last_name}")
    print(f"   Is Staff: {'Yes' if user.is_staff else 'No'}")
    print(f"   Is Active: {'Yes' if user.is_active else 'No'}")
    print(f"   Joined: {user.date_joined.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   Last Login: {user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else 'Never'}")
    
    # Get user's token
    try:
        token = Token.objects.get(user=user)
        print(f"   🔑 Token: {token.key}")
        print(f"   Token Created: {token.created.strftime('%Y-%m-%d %H:%M:%S')}")
    except Token.DoesNotExist:
        print(f"   🔑 Token: None (user hasn't logged in)")
    
    print("-" * 70)

# Show token statistics
print("\n📈 TOKEN STATISTICS")
print("-" * 70)
total_tokens = Token.objects.all().count()
print(f"Total Active Tokens: {total_tokens}")

if total_tokens > 0:
    print("\nActive Sessions:")
    for token in Token.objects.all():
        print(f"  • {token.user.username}: {token.key[:20]}...")

print("\n" + "=" * 70)
print("✅ Report Complete!")
print("=" * 70)
