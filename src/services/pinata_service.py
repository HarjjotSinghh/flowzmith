"""
Pinata IPFS service for storing contract code on IPFS.
"""

import json
import logging
from typing import Dict, Any, Optional, Union
from datetime import datetime
import requests
from io import BytesIO
from tenacity import retry, stop_after_attempt, wait_exponential

from ..config import get_settings

logger = logging.getLogger(__name__)


class PinataError(Exception):
    """Base exception for Pinata operations."""
    pass


class PinataService:
    """Service for interacting with Pinata IPFS storage."""
    
    def __init__(self):
        self.settings = get_settings()
        self.base_url = "https://api.pinata.cloud"
        self.upload_url = "https://uploads.pinata.cloud/v3/files"
        self.gateway_url = f"https://{self.settings.pinata_gateway}" if self.settings.pinata_gateway else None
        
        if not self.settings.pinata_jwt:
            raise PinataError("PINATA_JWT not configured")
        
        self.headers = {
            "Authorization": f"Bearer {self.settings.pinata_jwt}"
        }
    
    async def test_authentication(self) -> bool:
        """Test Pinata API authentication."""
        try:
            response = requests.get(
                f"{self.base_url}/data/testAuthentication",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Pinata authentication successful: {data.get('message', '')}")
                return True
            else:
                logger.error(f"Pinata authentication failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to test Pinata authentication: {e}")
            return False
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def upload_contract_to_ipfs(
        self,
        contract_code: str,
        contract_name: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Upload contract code to IPFS via Pinata using v3 API.
        
        Args:
            contract_code: The Cadence contract code to upload
            contract_name: Name of the contract for identification
            metadata: Additional metadata to store with the contract
            
        Returns:
            Dictionary containing IPFS CID, pin ID, and other metadata
        """
        try:
            # Prepare the contract data
            contract_data = {
                "contract_name": contract_name,
                "contract_code": contract_code,
                "uploaded_at": datetime.utcnow().isoformat(),
                "metadata": metadata or {}
            }
            
            # Convert to JSON string
            json_data = json.dumps(contract_data, indent=2)
            
            # Create a temporary file-like object
            contract_file = BytesIO(json_data.encode('utf-8'))
            filename = f"{contract_name}.json"
            
            # Prepare multipart form data for file upload
            files = {
                'file': (filename, contract_file, 'application/json')
            }
            
            # Prepare form data for v3 API
            data = {
                'name': f"{contract_name} - Smart Contract",
                'network': 'private'  # Use private network for better performance
            }
            
            # Add keyvalues metadata if provided
            if metadata:
                keyvalues = {
                    "contract_name": contract_name,
                    "type": "smart_contract",
                    "language": "cadence",
                    "uploaded_by": "flowzmith",
                    "timestamp": datetime.utcnow().isoformat()
                }
                keyvalues.update(metadata)
                data['keyvalues'] = json.dumps(keyvalues)
            
            # Upload to Pinata using v3 API
            response = requests.post(
                self.upload_url,
                headers=self.headers,
                files=files,
                data=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # v3 API returns data in 'data' field
                if "data" not in result or "cid" not in result["data"]:
                    raise ValueError("Unexpected response format: 'cid' missing")
                
                data_info = result["data"]
                
                upload_result = {
                    "ipfs_cid": data_info["cid"],
                    "pin_id": data_info.get("id", ""),  # v3 API returns file ID
                    "size": data_info.get("size", 0),
                    "timestamp": data_info.get("created_at", datetime.utcnow().isoformat()),
                    "gateway_url": f"{self.gateway_url}/ipfs/{data_info['cid']}" if self.gateway_url else None,
                    "pinata_metadata": {
                        "name": data.get('name'),
                        "keyvalues": json.loads(data.get('keyvalues', '{}'))
                    },
                    "upload_status": "success"
                }
                
                logger.info(f"Successfully uploaded contract '{contract_name}' to IPFS: {data_info['cid']}")
                return upload_result
                
            else:
                error_msg = f"Failed to upload to IPFS: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise PinataError(error_msg)
                
        except Exception as e:
            logger.error(f"Error uploading contract to IPFS: {e}")
            raise PinataError(f"IPFS upload failed: {e}")
    
    async def upload_json_to_ipfs(
        self,
        json_data: Dict[str, Any],
        name: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Upload JSON data directly to IPFS via Pinata.
        
        Args:
            json_data: The JSON data to upload
            name: Name for the uploaded content
            metadata: Additional metadata
            
        Returns:
            Dictionary containing IPFS CID and metadata
        """
        try:
            # Prepare pinata metadata
            pinata_metadata = {
                "name": name,
                "keyvalues": {
                    "type": "json_data",
                    "uploaded_by": "flowzmith",
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
            
            if metadata:
                pinata_metadata["keyvalues"].update(metadata)
            
            # Prepare the request payload
            payload = {
                "pinataContent": json_data,
                "pinataMetadata": pinata_metadata,
                "pinataOptions": {
                    "cidVersion": 1
                }
            }
            
            response = requests.post(
                f"{self.base_url}/pinning/pinJSONToIPFS",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                return {
                    "ipfs_cid": result["IpfsHash"],
                    "size": result["PinSize"],
                    "timestamp": result["Timestamp"],
                    "gateway_url": f"{self.gateway_url}/ipfs/{result['IpfsHash']}",
                    "pinata_metadata": pinata_metadata,
                    "upload_status": "success"
                }
            else:
                error_msg = f"Failed to upload JSON to IPFS: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise PinataError(error_msg)
                
        except Exception as e:
            logger.error(f"Error uploading JSON to IPFS: {e}")
            raise PinataError(f"JSON IPFS upload failed: {e}")
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def retrieve_from_ipfs(self, cid: str) -> Dict[str, Any]:
        """
        Retrieve content from IPFS using the CID.
        
        Args:
            cid: The IPFS Content Identifier
            
        Returns:
            The retrieved content as a dictionary
        """
        try:
            # Try multiple gateway URLs in order of preference
            gateway_urls = []
            
            # First, try the configured custom gateway
            if self.gateway_url:
                gateway_urls.append(self.gateway_url)
            
            # Then try the public Pinata gateway
            gateway_urls.append("https://gateway.pinata.cloud")
            
            # Finally, try the IPFS.io public gateway as last resort
            gateway_urls.append("https://ipfs.io")
            
            last_error = None
            
            for gateway_url in gateway_urls:
                try:
                    url = f"{gateway_url}/ipfs/{cid}"
                    logger.info(f"Trying to retrieve from: {url}")
                    
                    response = requests.get(url, timeout=30)
                    
                    if response.status_code == 200:
                        try:
                            return response.json()
                        except json.JSONDecodeError:
                            # If not JSON, return as text
                            return {"content": response.text, "type": "text"}
                    else:
                        last_error = f"Gateway {gateway_url} returned {response.status_code}: {response.text}"
                        logger.warning(last_error)
                        continue
                        
                except requests.RequestException as e:
                    last_error = f"Gateway {gateway_url} failed: {e}"
                    logger.warning(last_error)
                    continue
            
            # If all gateways failed, raise the last error
            if last_error:
                raise PinataError(f"All gateways failed. Last error: {last_error}")
            else:
                raise PinataError("No gateways available")
                
        except Exception as e:
            logger.error(f"Error retrieving from IPFS: {e}")
            raise PinataError(f"IPFS retrieval failed: {e}")
    
    async def unpin_from_ipfs(self, cid: str) -> bool:
        """
        Unpin content from Pinata (remove from IPFS storage).
        
        Args:
            cid: The IPFS Content Identifier to unpin
            
        Returns:
            True if successfully unpinned, False otherwise
        """
        try:
            response = requests.delete(
                f"{self.base_url}/pinning/unpin/{cid}",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"Successfully unpinned {cid} from IPFS")
                return True
            else:
                logger.error(f"Failed to unpin from IPFS: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error unpinning from IPFS: {e}")
            return False
    
    async def list_pinned_files(
        self,
        limit: int = 10,
        offset: int = 0,
        metadata_filter: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        List pinned files from Pinata.
        
        Args:
            limit: Number of files to return
            offset: Offset for pagination
            metadata_filter: Filter by metadata key-value pairs
            
        Returns:
            List of pinned files with metadata
        """
        try:
            params = {
                "pageLimit": limit,
                "pageOffset": offset,
                "status": "pinned"
            }
            
            # Add metadata filters if provided
            if metadata_filter:
                for key, value in metadata_filter.items():
                    params[f"metadata[keyvalues][{key}]"] = value
            
            response = requests.get(
                f"{self.base_url}/data/pinList",
                headers=self.headers,
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                error_msg = f"Failed to list pinned files: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise PinataError(error_msg)
                
        except Exception as e:
            logger.error(f"Error listing pinned files: {e}")
            raise PinataError(f"Failed to list pinned files: {e}")
    
    async def get_pin_metadata(self, cid: str) -> Dict[str, Any]:
        """
        Get metadata for a pinned file.
        
        Args:
            cid: The IPFS Content Identifier
            
        Returns:
            Metadata for the pinned file
        """
        try:
            params = {
                "hashContains": cid,
                "status": "pinned",
                "pageLimit": 1
            }
            
            response = requests.get(
                f"{self.base_url}/data/pinList",
                headers=self.headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("rows") and len(data["rows"]) > 0:
                    return data["rows"][0]
                else:
                    raise PinataError(f"No pinned file found with CID: {cid}")
            else:
                error_msg = f"Failed to get pin metadata: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise PinataError(error_msg)
                
        except Exception as e:
            logger.error(f"Error getting pin metadata: {e}")
            raise PinataError(f"Failed to get pin metadata: {e}")


# Global instance
_pinata_service: Optional[PinataService] = None


def get_pinata_service() -> Optional[PinataService]:
    """Get the global Pinata service instance."""
    global _pinata_service
    
    settings = get_settings()
    
    if not settings.enable_ipfs_storage:
        return None
    
    if _pinata_service is None:
        try:
            _pinata_service = PinataService()
        except PinataError as e:
            logger.error(f"Failed to initialize Pinata service: {e}")
            return None
    
    return _pinata_service
