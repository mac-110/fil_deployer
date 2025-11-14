"""
Encryption and decryption utilities for sensitive data.

Uses Fernet (symmetric encryption) from the cryptography library.
The key is derived from a secret that can be configured via environment variable.
"""

import base64
import hashlib
import os
from cryptography.fernet import Fernet
from typing import Optional


class CryptoManager:
    """Handles encryption and decryption of sensitive data"""

    # Default secret - used as fallback if ENCRYPTION_SECRET is not set
    # For production, ALWAYS set ENCRYPTION_SECRET environment variable!
    _DEFAULT_SECRET = "FIL_DEPLOYER_ENCRYPTION_SECRET_2024_SWISSCOM_SECURE_KEY"

    def __init__(self):
        """Initialize the crypto manager with derived Fernet key"""
        # Get secret from environment variable, fallback to default
        secret = os.getenv("ENCRYPTION_SECRET", self._DEFAULT_SECRET)

        # Log warning if using default secret
        if secret == self._DEFAULT_SECRET:
            print("⚠️  WARNING: Using default encryption secret!")
            print("   For production, set ENCRYPTION_SECRET environment variable.")
        else:
            print("✅ Using custom ENCRYPTION_SECRET from environment")

        self._fernet_key = self._derive_fernet_key(secret)
        self._cipher = Fernet(self._fernet_key)

    @staticmethod
    def _derive_fernet_key(secret: str) -> bytes:
        """
        Derive a Fernet-compatible key from the secret.

        Uses PBKDF2 (Password-Based Key Derivation Function 2) with SHA256
        to create a 32-byte key from the secret string.

        Args:
            secret: The secret string to derive key from

        Returns:
            Base64-encoded 32-byte key suitable for Fernet
        """
        # Use a fixed salt for deterministic key generation
        # In a more advanced setup, this could be randomized and stored separately
        salt = b"fil_deployer_salt_v1"

        # Derive 32 bytes using PBKDF2-HMAC-SHA256
        kdf = hashlib.pbkdf2_hmac(
            'sha256',
            secret.encode('utf-8'),
            salt,
            iterations=100000,
            dklen=32
        )

        # Fernet requires base64-encoded key
        return base64.urlsafe_b64encode(kdf)

    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt a plaintext string.

        Args:
            plaintext: The string to encrypt

        Returns:
            Base64-encoded encrypted string
        """
        if not plaintext:
            return ""

        encrypted_bytes = self._cipher.encrypt(plaintext.encode('utf-8'))
        return encrypted_bytes.decode('utf-8')

    def decrypt(self, encrypted: str) -> str:
        """
        Decrypt an encrypted string.

        Args:
            encrypted: The base64-encoded encrypted string

        Returns:
            Decrypted plaintext string

        Raises:
            cryptography.fernet.InvalidToken: If decryption fails
        """
        if not encrypted:
            return ""

        try:
            decrypted_bytes = self._cipher.decrypt(encrypted.encode('utf-8'))
            return decrypted_bytes.decode('utf-8')
        except Exception as e:
            # Log error but don't expose details
            print(f"Decryption error: {type(e).__name__}")
            raise ValueError("Failed to decrypt token - token may be corrupted or from different encryption key")

    def is_encrypted(self, value: str) -> bool:
        """
        Check if a string appears to be encrypted.

        Fernet tokens start with 'gAAAAA' (base64 encoded header).
        This is a heuristic check, not cryptographically secure validation.

        Args:
            value: String to check

        Returns:
            True if string appears to be Fernet-encrypted
        """
        if not value:
            return False

        # Fernet tokens are base64 and typically start with gAAAAA
        # Length check: Fernet tokens are at least 73 characters
        if len(value) < 73:
            return False

        # Try to detect Fernet token pattern
        try:
            # Fernet tokens start with specific bytes after base64 decode
            return value.startswith('gAAAAA')
        except:
            return False


# Global instance
crypto_manager = CryptoManager()
