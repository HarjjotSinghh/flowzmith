#!/usr/bin/env python3
"""
Script to verify the public key derived from the private key matches the account.
"""

import os
from dotenv import load_dotenv
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import Encoding, NoEncryption, PrivateFormat, PublicFormat

# Load environment variables
load_dotenv()

def derive_public_key_from_private(private_key_hex):
    """Derive public key from private key."""
    try:
        # Remove 0x prefix if present
        if private_key_hex.startswith('0x'):
            private_key_hex = private_key_hex[2:]
        
        # Convert hex to bytes
        private_key_bytes = bytes.fromhex(private_key_hex)
        
        # Create private key object
        private_key = ec.derive_private_key(
            int.from_bytes(private_key_bytes, 'big'),
            ec.SECP256K1()
        )
        
        # Get public key
        public_key = private_key.public_key()
        
        # Serialize public key to uncompressed format (Flow uses this)
        public_key_bytes = public_key.public_bytes(
            encoding=Encoding.X962,
            format=PublicFormat.UncompressedPoint
        )
        
        # Remove the 0x04 prefix (uncompressed point indicator)
        public_key_hex = public_key_bytes[1:].hex()
        
        return public_key_hex
        
    except Exception as e:
        print(f"Error deriving public key: {e}")
        return None

def main():
    # Get credentials from environment
    private_key = os.getenv('FLOW_PRIVATE_KEY')
    account_address = os.getenv('FLOW_ACCOUNT_ADDRESS')
    
    print(f"Account Address: {account_address}")
    print(f"Private Key: {private_key}")
    print()
    
    # Derive public key
    derived_public_key = derive_public_key_from_private(private_key)
    
    if derived_public_key:
        print(f"Derived Public Key: {derived_public_key}")
        print()
        
        # Expected public key from account info
        expected_public_key = "db014e6d642c42fd2c9a96be1cf20506243c60ac764f7852a182b26d556e1197f0bffa78eadcaf44d95c9b6e658ec20288fefd59b84f1044ebc6367199c783f1"
        
        print(f"Expected Public Key: {expected_public_key}")
        print()
        
        if derived_public_key.lower() == expected_public_key.lower():
            print("✅ Keys match! The private key is correct for this account.")
        else:
            print("❌ Keys don't match! The private key doesn't correspond to this account.")
            print()
            print("This means either:")
            print("1. The private key is incorrect")
            print("2. The account address is incorrect")
            print("3. The account has a different key at index 0")
    else:
        print("❌ Failed to derive public key")

if __name__ == "__main__":
    main()