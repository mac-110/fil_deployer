#!/usr/bin/env python3
"""
Test script for encryption/decryption functionality.

This script tests the crypto_utils module to ensure tokens are
properly encrypted and decrypted.
"""

import sys
from pathlib import Path

# Add backend/app to path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from crypto_utils import crypto_manager


def test_basic_encryption():
    """Test basic encryption and decryption"""
    print("🔐 Testing Basic Encryption/Decryption...")

    test_token = "glpat-xxxxxxxxxxxxxxxxxxxx"
    print(f"  Original token: {test_token}")

    # Encrypt
    encrypted = crypto_manager.encrypt(test_token)
    print(f"  Encrypted:      {encrypted[:50]}..." if len(encrypted) > 50 else f"  Encrypted:      {encrypted}")

    # Verify it looks encrypted
    assert crypto_manager.is_encrypted(encrypted), "Token should be detected as encrypted"
    assert encrypted != test_token, "Encrypted token should differ from original"
    assert encrypted.startswith("gAAAAA"), "Fernet tokens should start with gAAAAA"

    # Decrypt
    decrypted = crypto_manager.decrypt(encrypted)
    print(f"  Decrypted:      {decrypted}")

    # Verify
    assert decrypted == test_token, f"Decryption failed: {decrypted} != {test_token}"

    print("  ✅ Basic encryption/decryption works!\n")


def test_empty_string():
    """Test encryption of empty strings"""
    print("🔐 Testing Empty String...")

    empty = ""
    encrypted = crypto_manager.encrypt(empty)
    decrypted = crypto_manager.decrypt(encrypted)

    assert encrypted == "", "Empty string should encrypt to empty"
    assert decrypted == "", "Empty encrypted string should decrypt to empty"

    print("  ✅ Empty string handling works!\n")


def test_is_encrypted_detection():
    """Test detection of encrypted vs plaintext"""
    print("🔐 Testing Encryption Detection...")

    plaintext = "this-is-a-plaintext-token"
    encrypted = crypto_manager.encrypt(plaintext)

    assert not crypto_manager.is_encrypted(plaintext), "Plaintext should not be detected as encrypted"
    assert crypto_manager.is_encrypted(encrypted), "Encrypted text should be detected"
    assert not crypto_manager.is_encrypted(""), "Empty string should not be detected as encrypted"
    assert not crypto_manager.is_encrypted("short"), "Short strings should not be detected as encrypted"

    print("  ✅ Encryption detection works!\n")


def test_multiple_encryptions():
    """Test that same plaintext produces different ciphertexts (IV randomization)"""
    print("🔐 Testing IV Randomization...")

    plaintext = "test-token-12345"
    encrypted1 = crypto_manager.encrypt(plaintext)
    encrypted2 = crypto_manager.encrypt(plaintext)

    # Different ciphertexts (due to random IV)
    assert encrypted1 != encrypted2, "Same plaintext should produce different ciphertexts"

    # But both decrypt to same plaintext
    assert crypto_manager.decrypt(encrypted1) == plaintext
    assert crypto_manager.decrypt(encrypted2) == plaintext

    print(f"  Encryption 1: {encrypted1[:50]}...")
    print(f"  Encryption 2: {encrypted2[:50]}...")
    print("  ✅ IV randomization works!\n")


def test_long_token():
    """Test encryption of long tokens"""
    print("🔐 Testing Long Token...")

    long_token = "A" * 500  # 500 character token
    encrypted = crypto_manager.encrypt(long_token)
    decrypted = crypto_manager.decrypt(encrypted)

    assert decrypted == long_token, "Long token should decrypt correctly"

    print(f"  Original length:  {len(long_token)}")
    print(f"  Encrypted length: {len(encrypted)}")
    print("  ✅ Long token handling works!\n")


def test_special_characters():
    """Test encryption with special characters"""
    print("🔐 Testing Special Characters...")

    special_token = "token!@#$%^&*()_+-=[]{}|;':\",./<>?äöüß"
    encrypted = crypto_manager.encrypt(special_token)
    decrypted = crypto_manager.decrypt(encrypted)

    assert decrypted == special_token, "Special characters should survive encryption"

    print(f"  Original:  {special_token}")
    print(f"  Decrypted: {decrypted}")
    print("  ✅ Special character handling works!\n")


def run_all_tests():
    """Run all encryption tests"""
    print("=" * 60)
    print("🚀 FIL Deployer - Encryption Test Suite")
    print("=" * 60)
    print()

    try:
        test_basic_encryption()
        test_empty_string()
        test_is_encrypted_detection()
        test_multiple_encryptions()
        test_long_token()
        test_special_characters()

        print("=" * 60)
        print("✅ All encryption tests passed!")
        print("=" * 60)
        return 0

    except AssertionError as e:
        print()
        print("=" * 60)
        print(f"❌ Test failed: {e}")
        print("=" * 60)
        return 1

    except Exception as e:
        print()
        print("=" * 60)
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
