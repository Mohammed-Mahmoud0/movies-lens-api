"""
Simple script to test Redis cache connection
Run this after installing redis: pip install redis
"""
from django.core.cache import cache

# Test 1: Set a value
cache.set('test_key', 'Hello Redis!', timeout=60)
print("✓ Set value in cache")

# Test 2: Get the value
value = cache.get('test_key')
print(f"✓ Got value from cache: {value}")

# Test 3: Delete the value
cache.delete('test_key')
print("✓ Deleted value from cache")

# Test 4: Check if deleted
value = cache.get('test_key')
print(f"✓ After deletion: {value}")

print("\n✅ Redis cache is working correctly!")
