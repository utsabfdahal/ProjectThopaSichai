#!/usr/bin/env python
"""
Database Viewer - View PostgreSQL database contents
Usage: python view_db.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ThopaSichai_backend.settings')
django.setup()

from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.db import connection

def print_separator():
    print("=" * 80)

def show_users():
    print_separator()
    print("👥 ALL USERS")
    print_separator()
    
    users = User.objects.all()
    print(f"Total Users: {users.count()}\n")
    
    for user in users:
        print(f"ID: {user.id}")
        print(f"Username: {user.username}")
        print(f"Email: {user.email}")
        print(f"Staff: {'Yes' if user.is_staff else 'No'}")
        print(f"Superuser: {'Yes' if user.is_superuser else 'No'}")
        print(f"Active: {'Yes' if user.is_active else 'No'}")
        print(f"Joined: {user.date_joined}")
        print(f"Last Login: {user.last_login or 'Never'}")
        
        # Check for token
        try:
            token = Token.objects.get(user=user)
            print(f"🔑 Token: {token.key}")
            print(f"Token Created: {token.created}")
        except Token.DoesNotExist:
            print("🔑 Token: No token (not logged in)")
        
        print("-" * 80)

def show_tokens():
    print_separator()
    print("🔑 ALL TOKENS")
    print_separator()
    
    tokens = Token.objects.all()
    print(f"Total Tokens: {tokens.count()}\n")
    
    for token in tokens:
        print(f"Token: {token.key}")
        print(f"User: {token.user.username}")
        print(f"Created: {token.created}")
        print("-" * 80)

def show_database_info():
    print_separator()
    print("📊 DATABASE INFORMATION")
    print_separator()
    
    with connection.cursor() as cursor:
        # Get database name
        cursor.execute("SELECT current_database();")
        db_name = cursor.fetchone()[0]
        print(f"Database: {db_name}")
        
        # Get all tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        print(f"\nTables ({len(tables)}):")
        for table in tables:
            # Get row count (use quotes for case-sensitive table names)
            cursor.execute(f'SELECT COUNT(*) FROM "{table[0]}";')
            count = cursor.fetchone()[0]
            print(f"  - {table[0]}: {count} rows")
    
    print_separator()

def main():
    print("\n" + "=" * 80)
    print("🗄️  THOPASICHAI DATABASE VIEWER")
    print("=" * 80 + "\n")
    
    show_database_info()
    print()
    show_users()
    print()
    show_tokens()
    
    print("\n" + "=" * 80)
    print("✅ Database Status: Connected to PostgreSQL")
    print("=" * 80 + "\n")

if __name__ == '__main__':
    main()
