"""
Credential Vault
Secure credential encryption/decryption for AWS Nitro Enclave usage
"""

import os
import base64
from typing import Dict
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2


class CredentialVault:
    """
    Manages encryption and decryption of user credentials.
    
    In production, credentials are:
    1. Encrypted here with a master key
    2. Stored in Supabase credential_vault table
    3. Decrypted only within AWS Nitro Enclave during cancellation
    
    This prevents credentials from ever being in plaintext in the main backend.
    """
    
    def __init__(self):
        """Initialize vault with encryption key from environment"""
        self.encryption_key = self._get_encryption_key()
        self.fernet = Fernet(self.encryption_key)
    
    def _get_encryption_key(self) -> bytes:
        """
        Get or derive encryption key from environment.
        
        In production:
        - Use AWS KMS or Secrets Manager
        - Key should be stored in Nitro Enclave and never exposed
        
        For development:
        - Use CREDENTIAL_ENCRYPTION_KEY environment variable
        - Generate with: Fernet.generate_key()
        """
        key = os.getenv('CREDENTIAL_ENCRYPTION_KEY')
        
        if not key:
            # Development fallback - derive from password
            # WARNING: In production, use AWS KMS or Secrets Manager
            # This fallback should NEVER be used in production
            password = os.getenv('CREDENTIAL_MASTER_PASSWORD')
            if not password:
                raise ValueError(
                    "CREDENTIAL_ENCRYPTION_KEY or CREDENTIAL_MASTER_PASSWORD must be set. "
                    "Never use default passwords in any environment."
                )
            
            # Use a user-specific salt (in real implementation, store per user)
            # For now, using a fixed salt only for development/testing
            salt = b'subzero-dev-salt-replace-in-prod'
            
            kdf = PBKDF2(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=480000,
            )
            key_bytes = kdf.derive(password.encode())
            key = base64.urlsafe_b64encode(key_bytes)
        else:
            key = key.encode() if isinstance(key, str) else key
        
        return key
    
    def encrypt_credentials(self, credentials: Dict[str, str]) -> bytes:
        """
        Encrypt credentials for storage in database.
        
        Args:
            credentials: Dictionary with keys like 'email', 'password', '2fa_secret', etc.
            
        Returns:
            bytes: Encrypted credentials blob for storage in credential_vault.encrypted_credentials
            
        Example:
            credentials = {
                'email': 'user@example.com',
                'password': 'secret123',
                '2fa_backup_codes': ['code1', 'code2']
            }
            encrypted = vault.encrypt_credentials(credentials)
        """
        # Convert dict to JSON string
        import json
        credentials_json = json.dumps(credentials)
        
        # Encrypt with Fernet (symmetric encryption)
        encrypted_bytes = self.fernet.encrypt(credentials_json.encode())
        
        return encrypted_bytes
    
    def decrypt_credentials(self, encrypted_credentials: bytes) -> Dict[str, str]:
        """
        Decrypt credentials for use (should only happen in Nitro Enclave).
        
        Args:
            encrypted_credentials: Encrypted blob from database
            
        Returns:
            dict: Decrypted credentials
            
        Security Note:
            In production, this function should ONLY be called within AWS Nitro Enclave
            during the cancellation workflow. The decrypted credentials should never
            leave the enclave or be logged.
        """
        import json
        
        # Decrypt with Fernet
        decrypted_bytes = self.fernet.decrypt(encrypted_credentials)
        credentials_json = decrypted_bytes.decode()
        
        # Parse back to dict
        credentials = json.loads(credentials_json)
        
        return credentials
    
    def rotate_key(self, old_key: bytes, new_key: bytes, encrypted_data: bytes) -> bytes:
        """
        Re-encrypt data with a new key (for key rotation).
        
        Args:
            old_key: Previous encryption key
            new_key: New encryption key
            encrypted_data: Data encrypted with old key
            
        Returns:
            bytes: Data re-encrypted with new key
        """
        # Decrypt with old key
        old_fernet = Fernet(old_key)
        decrypted = old_fernet.decrypt(encrypted_data)
        
        # Re-encrypt with new key
        new_fernet = Fernet(new_key)
        re_encrypted = new_fernet.encrypt(decrypted)
        
        return re_encrypted


# Utility functions for common credential operations

def validate_credentials(credentials: Dict[str, str]) -> bool:
    """
    Validate that required credential fields are present.
    
    Args:
        credentials: Credential dictionary
        
    Returns:
        bool: True if valid, False otherwise
    """
    required_fields = ['email', 'password']
    return all(field in credentials for field in required_fields)


def sanitize_credentials_for_logging(credentials: Dict[str, str]) -> Dict[str, str]:
    """
    Create a safe version of credentials for logging (masks sensitive data).
    
    Args:
        credentials: Original credentials
        
    Returns:
        dict: Sanitized version safe for logs
        
    Example:
        >>> sanitize_credentials_for_logging({'email': 'user@example.com', 'password': 'secret'})
        {'email': 'u***@example.com', 'password': '***'}
    """
    sanitized = {}
    
    for key, value in credentials.items():
        if key == 'password' or 'secret' in key.lower():
            sanitized[key] = '***'
        elif key == 'email' and isinstance(value, str) and '@' in value:
            # Mask email: user@example.com -> u***@example.com
            parts = value.split('@')
            sanitized[key] = f"{parts[0][0]}***@{parts[1]}"
        else:
            sanitized[key] = value
    
    return sanitized


# Singleton instance
_vault_instance = None


def get_vault() -> CredentialVault:
    """Get singleton CredentialVault instance"""
    global _vault_instance
    if _vault_instance is None:
        _vault_instance = CredentialVault()
    return _vault_instance
