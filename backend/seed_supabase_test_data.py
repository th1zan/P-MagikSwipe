#!/usr/bin/env python3
"""
Script to seed Supabase with test data for integration tests.
Run this before running integration tests that require real Supabase data.
"""

import sys
import os
sys.path.append('.')

from services.supabase_service import supabase_service

def create_test_universe():
    """Create a test universe in Supabase for integration testing."""

    if not supabase_service.is_connected:
        print("❌ Supabase not connected. Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY.")
        return False

    test_universe_data = {
        "id": 999999,  # Use a high ID to avoid conflicts
        "name": "Test Universe",
        "slug": "test-integration-universe",
        "thumbnail_url": None,
        "is_public": True,
        "background_music": None,
        "background_color": "#1a1a2e",
        "supabase_id": 999999
    }

    try:
        result = supabase_service.upsert_univers(test_universe_data)
        print(f"✅ Created test universe: {result}")
        return True
    except Exception as e:
        print(f"❌ Failed to create test universe: {e}")
        return False

if __name__ == "__main__":
    print("🌱 Seeding Supabase with test data...")
    success = create_test_universe()
    if success:
        print("✅ Test data seeded successfully")
        sys.exit(0)
    else:
        print("❌ Failed to seed test data")
        sys.exit(1)