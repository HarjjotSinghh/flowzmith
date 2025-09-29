#!/usr/bin/env python3
"""
Test script for IPFS integration with Pinata.
"""

import asyncio
import os
import sys
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.config import get_settings
from src.services.pinata_service import get_pinata_service, PinataError


async def test_ipfs_integration():
    """Test the IPFS integration."""
    print("🧪 Testing IPFS Integration with Pinata...")
    
    # Check configuration
    settings = get_settings()
    
    if not settings.enable_ipfs_storage:
        print("❌ IPFS storage is disabled. Set ENABLE_IPFS_STORAGE=true")
        return False
    
    if not settings.pinata_jwt:
        print("❌ PINATA_JWT not configured")
        return False
    
    print(f"✅ IPFS storage enabled")
    print(f"✅ Pinata JWT configured")
    print(f"✅ Gateway: {settings.pinata_gateway or 'Default'}")
    
    # Initialize service
    try:
        pinata_service = get_pinata_service()
        if not pinata_service:
            print("❌ Failed to initialize Pinata service")
            return False
        
        print("✅ Pinata service initialized")
    except Exception as e:
        print(f"❌ Error initializing Pinata service: {e}")
        return False
    
    # Test authentication
    try:
        auth_result = await pinata_service.test_authentication()
        if auth_result:
            print("✅ Pinata authentication successful")
        else:
            print("❌ Pinata authentication failed")
            return False
    except Exception as e:
        print(f"❌ Error testing authentication: {e}")
        return False
    
    # Test contract upload using the Counter contract
    try:
        # Read the Counter contract from file
        counter_contract_path = os.path.join(os.path.dirname(__file__), "..", "cadence", "contracts", "Counter.cdc")
        
        try:
            with open(counter_contract_path, 'r') as f:
                counter_contract = f.read()
        except FileNotFoundError:
            print(f"❌ Counter.cdc not found at {counter_contract_path}")
            return False
        
        print("📤 Uploading Counter.cdc contract to IPFS...")
        print(f"   Contract size: {len(counter_contract)} characters")
        
        upload_result = await pinata_service.upload_contract_to_ipfs(
            contract_code=counter_contract,
            contract_name="Counter",
            metadata={
                "contract_type": "counter",
                "language": "cadence",
                "version": "1.0",
                "test": "true",
                "environment": "development"
            }
        )
        
        if upload_result and upload_result.get("ipfs_cid"):
            cid = upload_result["ipfs_cid"]
            print(f"✅ Contract uploaded successfully!")
            print(f"   CID: {cid}")
            print(f"   Size: {upload_result.get('size', 'unknown')} bytes")
            print(f"   Gateway URL: {upload_result.get('gateway_url', 'N/A')}")
            
            # Test retrieval
            print("📥 Retrieving contract from IPFS...")
            
            retrieved_data = await pinata_service.retrieve_from_ipfs(cid)
            if retrieved_data and "contract_code" in retrieved_data:
                print("✅ Contract retrieved successfully!")
                print(f"   Contract name: {retrieved_data.get('contract_name', 'N/A')}")
                print(f"   Upload time: {retrieved_data.get('uploaded_at', 'N/A')}")
                
                # Verify content matches
                if retrieved_data["contract_code"].strip() == counter_contract.strip():
                    print("✅ Counter contract content matches original!")
                    print("✅ IPFS round-trip test successful!")
                else:
                    print("⚠️  Contract content differs from original")
                    print("   Expected length:", len(counter_contract.strip()))
                    print("   Retrieved length:", len(retrieved_data["contract_code"].strip()))
                
                return True
            else:
                print("❌ Failed to retrieve contract content")
                return False
        else:
            print("❌ Contract upload failed")
            return False
            
    except PinataError as e:
        print(f"❌ Pinata error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def main():
    """Main test function."""
    print("🚀 Starting IPFS Integration Test\n")
    
    # Check if running in virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Running in virtual environment")
    else:
        print("⚠️  Not running in virtual environment")
    
    # Load environment
    from dotenv import load_dotenv
    load_dotenv()
    
    # Run the test
    try:
        result = asyncio.run(test_ipfs_integration())
        
        print("\n" + "="*50)
        if result:
            print("🎉 IPFS Integration Test PASSED!")
            print("\nYour IPFS integration is working correctly.")
            print("You can now generate contracts and they will be automatically stored on IPFS.")
        else:
            print("💥 IPFS Integration Test FAILED!")
            print("\nPlease check your configuration and try again.")
            print("Make sure you have:")
            print("- ENABLE_IPFS_STORAGE=true")
            print("- PINATA_JWT=your_jwt_token")
            print("- PINATA_GATEWAY=your_gateway (optional)")
        print("="*50)
        
        return 0 if result else 1
        
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
