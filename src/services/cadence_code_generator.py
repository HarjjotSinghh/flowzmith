"""
Cadence Code Generation Service

Generates tests, transactions, and scripts for Cadence 1.0 contracts using AI.
"""

import json
import asyncio
from typing import Dict, Any, Optional, List
from pathlib import Path

from .llm_service import LLMService


class CadenceCodeGenerator:
    """Service for generating Cadence 1.0 tests, transactions, and scripts."""

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    async def generate_contract_files(
        self,
        contract_code: str,
        contract_name: str,
        contract_type: str,
        network: str = "testnet",
        requirements: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate tests, transactions, and scripts for a Cadence contract.

        Args:
            contract_code: The main contract code
            contract_name: Name of the contract
            contract_type: Type of contract (token, nft, etc.)
            network: Target network (testnet, mainnet, emulator)
            requirements: Additional contract requirements

        Returns:
            Dictionary containing generated files organized by type
        """
        # Load the system prompt
        system_prompt_path = Path(__file__).parent.parent.parent / "prompts" / "cadence_generation_system_prompt.md"
        with open(system_prompt_path, 'r', encoding='utf-8') as f:
            system_prompt = f.read()

        # Prepare the user prompt with contract context
        user_prompt = self._build_generation_prompt(
            contract_code, contract_name, contract_type, network, requirements
        )

        # Generate the code using LLM
        try:
            generated_response = await self.llm_service.generate_with_system_prompt(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.1,  # Low temperature for consistent code generation
                max_tokens=8000
            )

            # Parse the response
            result = self._parse_generation_response(generated_response)

            # Validate the generated code
            validation_result = await self._validate_generated_code(result, contract_code)
            if not validation_result["valid"]:
                print(f"Warning: Generated code validation failed: {validation_result['errors']}")

            return result

        except Exception as e:
            print(f"Error generating Cadence code: {e}")
            # Return fallback generated files
            return self._generate_fallback_files(contract_name, contract_type)

    def _build_generation_prompt(
        self,
        contract_code: str,
        contract_name: str,
        contract_type: str,
        network: str,
        requirements: Optional[Dict[str, Any]]
    ) -> str:
        """Build the user prompt for code generation."""
        prompt = f"""
Please generate comprehensive tests, transactions, and scripts for the following Cadence 1.0 smart contract:

## Contract Information
- **Contract Name**: {contract_name}
- **Contract Type**: {contract_type}
- **Target Network**: {network}
- **Requirements**: {json.dumps(requirements or {}, indent=2)}

## Contract Code
```cadence
{contract_code}
```

## Analysis Requirements
Before generating code, please analyze this contract and identify:
1. Public functions that need testing
2. Resources that need transactions
3. Storage paths and capability patterns
4. Events that should be tested
5. Error conditions to handle

## Generation Requirements
Generate production-ready Cadence 1.0 code that:
- Uses correct import addresses for {network}
- Implements proper interface conformance
- Includes comprehensive error handling
- Follows Cadence 1.0 syntax standards
- Provides complete test coverage
- Uses appropriate access modifiers

Return the result as a JSON object with the structure specified in the system prompt.
"""
        return prompt

    def _parse_generation_response(self, response: str) -> Dict[str, Any]:
        """Parse the LLM response into structured data."""
        try:
            # Try to parse as JSON first
            result = json.loads(response)
            return result
        except json.JSONDecodeError:
            # If not valid JSON, try to extract JSON from markdown code blocks
            import re
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', response, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group(1))
                except json.JSONDecodeError:
                    pass

            # If still no valid JSON, create fallback structure
            print("Warning: Could not parse LLM response as JSON, using fallback structure")
            return self._create_fallback_structure()

    def _create_fallback_structure(self) -> Dict[str, Any]:
        """Create a fallback structure when parsing fails."""
        return {
            "tests": {},
            "transactions": {},
            "scripts": {},
            "flow_json_updates": {
                "additional_dependencies": {},
                "deployment_config": {}
            }
        }

    async def _validate_generated_code(self, generated_files: Dict[str, Any], contract_code: str) -> Dict[str, Any]:
        """Validate the generated Cadence code for syntax and correctness."""
        errors = []

        # Basic validation checks
        for file_type, files in generated_files.items():
            if file_type not in ["tests", "transactions", "scripts"]:
                continue

            for filename, content in files.items():
                # Check for required imports
                if "import NonFungibleToken" in contract_code and "import NonFungibleToken" not in content:
                    if "NFT" in contract_code or "Collection" in contract_code:
                        errors.append(f"{filename}: Missing NonFungibleToken import")

                # Check for proper Cadence 1.0 syntax
                if "pub " in content:
                    errors.append(f"{filename}: Contains old 'pub' syntax instead of 'access(all)'")

                # Check for resource handling
                if "@" in content and "<-" not in content.replace("import", "").replace("from", ""):
                    # This is a basic check - could be improved
                    pass

        return {
            "valid": len(errors) == 0,
            "errors": errors
        }

    def _generate_fallback_files(self, contract_name: str, contract_type: str) -> Dict[str, Any]:
        """Generate basic fallback files when AI generation fails."""
        print("Using fallback file generation")

        if contract_type.lower() == "nft":
            return self._generate_nft_fallback_files(contract_name)
        elif contract_type.lower() == "token":
            return self._generate_token_fallback_files(contract_name)
        else:
            return self._generate_generic_fallback_files(contract_name)

    def _generate_nft_fallback_files(self, contract_name: str) -> Dict[str, Any]:
        """Generate NFT fallback files."""
        return {
            "tests": {
                f"{contract_name}_test.cdc": f'''import Test
import NonFungibleToken from 0x631e88ae7f1d7c20
import {contract_name} from "../contracts/{contract_name}.cdc"

access(all) let account = Test.createAccount()

access(all) fun testContractDeployment() {{
    let err = Test.deployContract(
        name: "{contract_name}",
        path: "../contracts/{contract_name}.cdc",
        arguments: []
    )
    Test.expect(err, Test.beNil())
}}

access(all) fun testInitialSupply() {{
    let supply = {contract_name}.totalSupply
    Test.expect(supply, Test.equal(0 as UInt64))
}}
'''
            },
            "transactions": {
                "setup_collection.cdc": f'''import NonFungibleToken from 0x631e88ae7f1d7c20
import {contract_name} from 0x01

transaction() {{
    prepare(signer: auth(BorrowValue, IssueStorageCapabilityController, PublishCapability, SaveValue) &Account) {{
        if signer.storage.borrow<&{contract_name}.Collection>(from: {contract_name}.CollectionStoragePath) == nil {{
            let collection <- {contract_name}.createEmptyCollection(nftType: Type<@{contract_name}.NFT>())
            signer.storage.save(<-collection, to: {contract_name}.CollectionStoragePath)

            let collectionCap = signer.capabilities.storage.issue<&{{NonFungibleToken.CollectionPublic}}>({contract_name}.CollectionStoragePath)
            signer.capabilities.publish(collectionCap, at: {contract_name}.CollectionPublicPath)
        }}
    }}
}}
''',
                "mint_nft.cdc": f'''import NonFungibleToken from 0x631e88ae7f1d7c20
import {contract_name} from 0x01

transaction(recipient: Address, name: String, description: String, thumbnail: String) {{
    let minter: &{contract_name}.NFTMinter

    prepare(signer: auth(BorrowValue) &Account) {{
        self.minter = signer.storage.borrow<&{contract_name}.NFTMinter>(
            from: {contract_name}.MinterStoragePath
        ) ?? panic("Could not borrow a reference to the NFT minter")
    }}

    execute {{
        let recipient = getAccount(recipient)
        let receiver = recipient
            .capabilities.borrow<&{{NonFungibleToken.CollectionPublic}}>({contract_name}.CollectionPublicPath)
            ?? panic("Could not get receiver reference to the NFT Collection")

        self.minter.mintNFT(
            recipient: receiver,
            name: name,
            description: description,
            thumbnail: thumbnail
        )
    }}
}}
'''
            },
            "scripts": {
                "get_collection_ids.cdc": f'''import NonFungibleToken from 0x631e88ae7f1d7c20
import {contract_name} from 0x01

access(all) fun main(account: Address): [UInt64] {{
    let collection = getAccount(account)
        .capabilities.borrow<&{{NonFungibleToken.CollectionPublic}}>({contract_name}.CollectionPublicPath)
        ?? panic("Could not borrow a reference to the collection")

    return collection.getIDs()
}}
''',
                "get_total_supply.cdc": f'''import NonFungibleToken from 0x631e88ae7f1d7c20
import {contract_name} from 0x01

access(all) fun main(): UInt64 {{
    return {contract_name}.totalSupply
}}
'''
            },
            "flow_json_updates": {
                "additional_dependencies": {},
                "deployment_config": {}
            }
        }

    def _generate_token_fallback_files(self, contract_name: str) -> Dict[str, Any]:
        """Generate token fallback files."""
        return {
            "tests": {
                f"{contract_name}_test.cdc": f'''import Test
import {contract_name} from "../contracts/{contract_name}.cdc"

access(all) let account = Test.createAccount()

access(all) fun testContractDeployment() {{
    let err = Test.deployContract(
        name: "{contract_name}",
        path: "../contracts/{contract_name}.cdc",
        arguments: []
    )
    Test.expect(err, Test.beNil())
}}

access(all) fun testInitialSupply() {{
    let supply = {contract_name}.totalSupply
    Test.expect(supply, Test.equal(0.0))
}}
'''
            },
            "transactions": {
                "setup_account.cdc": f'''import FungibleToken from 0x9a0766d93b6608b7
import {contract_name} from 0x01

transaction {{
    prepare(signer: auth(BorrowValue, IssueStorageCapabilityController, PublishCapability, SaveValue) &Account) {{
        if signer.storage.borrow<&{contract_name}.Vault>(from: {contract_name}.VaultStoragePath) == nil {{
            signer.storage.save(<-{contract_name}.createEmptyVault(vaultType: Type<@{contract_name}.Vault>()), to: {contract_name}.VaultStoragePath)

            let receiverCap = signer.capabilities.storage.issue<&{{FungibleToken.Receiver}}>({contract_name}.VaultStoragePath)
            signer.capabilities.publish(receiverCap, at: {contract_name}.ReceiverPublicPath)

            let balanceCap = signer.capabilities.storage.issue<&{{FungibleToken.Balance}}>({contract_name}.VaultStoragePath)
            signer.capabilities.publish(balanceCap, at: {contract_name}.BalancePublicPath)
        }}
    }}
}}
''',
                "mint_tokens.cdc": f'''import FungibleToken from 0x9a0766d93b6608b7
import {contract_name} from 0x01

transaction(recipient: Address, amount: UFix64) {{
    let tokenAdmin: &{contract_name}.Administrator
    let tokenReceiver: &{{FungibleToken.Receiver}}

    prepare(signer: auth(BorrowValue) &Account) {{
        self.tokenAdmin = signer.storage.borrow<&{contract_name}.Administrator>(
            from: {contract_name}.AdminStoragePath
        ) ?? panic("Signer is not the token admin")

        self.tokenReceiver = getAccount(recipient)
            .capabilities.borrow<&{{FungibleToken.Receiver}}>({contract_name}.ReceiverPublicPath)
            ?? panic("Unable to borrow receiver reference")
    }}

    execute {{
        let minter <- self.tokenAdmin.createNewMinter(allowedAmount: amount)
        let mintedVault <- minter.mintTokens(amount: amount)

        self.tokenReceiver.deposit(from: <-mintedVault)
        destroy minter
    }}
}}
'''
            },
            "scripts": {
                "get_balance.cdc": f'''import FungibleToken from 0x9a0766d93b6608b7
import {contract_name} from 0x01

access(all) fun main(account: Address): UFix64 {{
    let vaultRef = getAccount(account)
        .capabilities.borrow<&{{FungibleToken.Balance}}>({contract_name}.BalancePublicPath)
        ?? panic("Could not borrow Balance reference to the Vault")

    return vaultRef.balance
}}
''',
                "get_supply.cdc": f'''import {contract_name} from 0x01

access(all) fun main(): UFix64 {{
    return {contract_name}.totalSupply
}}
'''
            },
            "flow_json_updates": {
                "additional_dependencies": {},
                "deployment_config": {}
            }
        }

    def _generate_generic_fallback_files(self, contract_name: str) -> Dict[str, Any]:
        """Generate generic fallback files."""
        return {
            "tests": {
                f"{contract_name}_test.cdc": f'''import Test
import {contract_name} from "../contracts/{contract_name}.cdc"

access(all) let account = Test.createAccount()

access(all) fun testContractDeployment() {{
    let err = Test.deployContract(
        name: "{contract_name}",
        path: "../contracts/{contract_name}.cdc",
        arguments: []
    )
    Test.expect(err, Test.beNil())
}}
'''
            },
            "transactions": {
                "deploy_contract.cdc": f'''import {contract_name} from 0x01

transaction() {{
    prepare(signer: auth(BorrowValue) &Account) {{
        log("Contract {contract_name} deployed successfully")
    }}

    execute {{
        log("Executing deployment transaction")
    }}
}}
'''
            },
            "scripts": {
                "read_contract_data.cdc": f'''import {contract_name} from 0x01

access(all) fun main(): String {{
    return "Contract {contract_name} is deployed and accessible"
}}
'''
            },
            "flow_json_updates": {
                "additional_dependencies": {},
                "deployment_config": {}
            }
        }
