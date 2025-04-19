"""
Security Utilities
----------------
Utilities for security and token handling
"""

import os
import secrets
import string


def generate_random_token(length: int = 32) -> str:
    """
    Generate a secure random token
    
    Args:
        length: Length of the token (default: 32)
        
    Returns:
        A random token string
    """
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length)) 