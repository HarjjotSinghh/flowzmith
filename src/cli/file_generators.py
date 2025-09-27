"""
File generators for Flow project components.
Generates transactions, scripts, tests, and flow.json files for contracts.
"""

import json
from typing import Dict, Any, List
from pathlib import Path
import os

from dotenv import load_dotenv
load_dotenv()


class FlowFileGenerator:
    """Generates Flow project files based on contract type and requirements."""
    
    def __init__(self):
        self.contract_types = {
            "token": "FungibleToken",
            "nft": "NonFungibleToken", 
            "defi": "DeFi",
            "marketplace": "Marketplace",
            "governance": "Governance",
            "utility": "Utility",
            "custom": "Custom"
        }
    
    def generate_flow_json(self, contract_name: str, contract_type: str, network: str = "emulator") -> Dict[str, Any]:
        """Generate flow.json configuration file."""
        
        # Configure accounts based on network
        if network == "emulator":
            accounts = {
                "emulator-account": {
                    "address": os.getenv("FLOW_ACCOUNT_ADDRESS", "f8d6e0586b0a20c7"),
                    "key": os.getenv("FLOW_PRIVATE_KEY", "2619878f0e2ff438d17551c297ddce204f27c861e99a6965d493b0a8b8e1b1a5")
                }
            }
            deployments = {
                "emulator": {
                    "emulator-account": [contract_name]
                }
            }
        else:
            accounts = {
                "default": {
                    "address": "$FLOW_ACCOUNT_ADDRESS",
                    "key": "$FLOW_PRIVATE_KEY"
                }
            }
            deployments = {
                "testnet": {
                    "default": [contract_name]
                },
                "mainnet": {
                    "default": [contract_name]
                }
            }
        
        return {
            "version": "1.0",
            "contracts": {
                contract_name: {
                    "source": f"./contracts/{contract_name}.cdc",
                    "aliases": {
                        "emulator": "0xf8d6e0586b0a20c7",
                        "testnet": "0x01",
                        "mainnet": "0x01"
                    }
                },
                "FungibleToken": {
                    "source": "",
                    "aliases": {
                        "emulator": "0xee82856bf20e2aa6",
                        "testnet": "0x9a0766d93b6608b7",
                        "mainnet": "0xf233dcee88fe0abe"
                    }
                },
                "NonFungibleToken": {
                    "source": "",
                    "aliases": {
                        "emulator": "0xf8d6e0586b0a20c7",
                        "testnet": "0x631e88ae7f1d7c20",
                        "mainnet": "0x1d7e57aa55817448"
                    }
                }
            },
            "networks": {
                "emulator": "127.0.0.1:3569",
                "testnet": "access.devnet.nodes.onflow.org:9000",
                "mainnet": "access.mainnet.nodes.onflow.org:9000"
            },
            "accounts": accounts,
            "deployments": deployments
        }
    
    def generate_transactions(self, contract_name: str, contract_type: str) -> Dict[str, str]:
        """Generate transaction files based on contract type."""
        transactions = {}
        
        if contract_type.lower() == "token":
            transactions.update(self._generate_token_transactions(contract_name))
        elif contract_type.lower() == "nft":
            transactions.update(self._generate_nft_transactions(contract_name))
        elif contract_type.lower() == "defi":
            transactions.update(self._generate_defi_transactions(contract_name))
        elif contract_type.lower() == "marketplace":
            transactions.update(self._generate_marketplace_transactions(contract_name))
        elif contract_type.lower() == "governance":
            transactions.update(self._generate_governance_transactions(contract_name))
        else:
            transactions.update(self._generate_generic_transactions(contract_name))
        
        return transactions
    
    def generate_scripts(self, contract_name: str, contract_type: str) -> Dict[str, str]:
        """Generate script files based on contract type."""
        scripts = {}
        
        if contract_type.lower() == "token":
            scripts.update(self._generate_token_scripts(contract_name))
        elif contract_type.lower() == "nft":
            scripts.update(self._generate_nft_scripts(contract_name))
        elif contract_type.lower() == "defi":
            scripts.update(self._generate_defi_scripts(contract_name))
        elif contract_type.lower() == "marketplace":
            scripts.update(self._generate_marketplace_scripts(contract_name))
        elif contract_type.lower() == "governance":
            scripts.update(self._generate_governance_scripts(contract_name))
        else:
            scripts.update(self._generate_generic_scripts(contract_name))
        
        return scripts
    
    def generate_tests(self, contract_name: str, contract_type: str) -> Dict[str, str]:
        """Generate test files based on contract type."""
        tests = {}
        
        if contract_type.lower() == "token":
            tests.update(self._generate_token_tests(contract_name))
        elif contract_type.lower() == "nft":
            tests.update(self._generate_nft_tests(contract_name))
        elif contract_type.lower() == "defi":
            tests.update(self._generate_defi_tests(contract_name))
        elif contract_type.lower() == "marketplace":
            tests.update(self._generate_marketplace_tests(contract_name))
        elif contract_type.lower() == "governance":
            tests.update(self._generate_governance_tests(contract_name))
        else:
            tests.update(self._generate_generic_tests(contract_name))
        
        return tests
    
    # Token-specific generators
    def _generate_token_transactions(self, contract_name: str) -> Dict[str, str]:
        """Generate token-specific transactions."""
        return {
            "mint_tokens": f'''import FungibleToken from 0xFungibleToken
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
}}''',
            "transfer_tokens": f'''import FungibleToken from 0xFungibleToken
import {contract_name} from 0x01

transaction(amount: UFix64, to: Address) {{
    let vault: auth(FungibleToken.Withdraw) &{contract_name}.Vault

    prepare(signer: auth(BorrowValue) &Account) {{
        self.vault = signer.storage.borrow<auth(FungibleToken.Withdraw) &{contract_name}.Vault>(
            from: {contract_name}.VaultStoragePath
        ) ?? panic("Could not borrow reference to the owner's Vault!")
    }}

    execute {{
        let receiver = getAccount(to)
            .capabilities.borrow<&{{FungibleToken.Receiver}}>({contract_name}.ReceiverPublicPath)
            ?? panic("Could not borrow receiver reference to the recipient's Vault")

        let sentVault <- self.vault.withdraw(amount: amount)
        receiver.deposit(from: <-sentVault)
    }}
}}''',
            "setup_account": f'''import FungibleToken from 0xFungibleToken
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
}}'''
        }
    
    def _generate_token_scripts(self, contract_name: str) -> Dict[str, str]:
        """Generate token-specific scripts."""
        return {
            "get_balance": f'''import FungibleToken from 0xFungibleToken
import {contract_name} from 0x01

access(all) fun main(account: Address): UFix64 {{
    let vaultRef = getAccount(account)
        .capabilities.borrow<&{{FungibleToken.Balance}}>({contract_name}.BalancePublicPath)
        ?? panic("Could not borrow Balance reference to the Vault")

    return vaultRef.balance
}}''',
            "get_supply": f'''import {contract_name} from 0x01

access(all) fun main(): UFix64 {{
    return {contract_name}.totalSupply
}}''',
            "check_account_setup": f'''import FungibleToken from 0xFungibleToken
import {contract_name} from 0x01

access(all) fun main(account: Address): Bool {{
    let receiverRef = getAccount(account)
        .capabilities.get<&{{FungibleToken.Receiver}}>({contract_name}.ReceiverPublicPath)
        .check()
    
    let balanceRef = getAccount(account)
        .capabilities.get<&{{FungibleToken.Balance}}>({contract_name}.BalancePublicPath)
        .check()
    
    return receiverRef && balanceRef
}}'''
        }
    
    def _generate_token_tests(self, contract_name: str) -> Dict[str, str]:
        """Generate token-specific tests."""
        return {
            "test_token_deployment": f'''import Test
import {contract_name} from "../contracts/{contract_name}.cdc"

access(all) fun testContractDeployment() {{
    let account = Test.createAccount()
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
}}'''
        }
    
    # NFT-specific generators
    def _generate_nft_transactions(self, contract_name: str) -> Dict[str, str]:
        """Generate NFT-specific transactions."""
        return {
            "mint_nft": f'''import NonFungibleToken from 0xNonFungibleToken
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
}}''',
            "transfer_nft": f'''import NonFungibleToken from 0xNonFungibleToken
import {contract_name} from 0x01

transaction(recipient: Address, withdrawID: UInt64) {{
    let withdrawRef: auth(NonFungibleToken.Withdraw) &{contract_name}.Collection

    prepare(signer: auth(BorrowValue) &Account) {{
        self.withdrawRef = signer.storage.borrow<auth(NonFungibleToken.Withdraw) &{contract_name}.Collection>(
            from: {contract_name}.CollectionStoragePath
        ) ?? panic("Could not borrow a reference to the owner's collection")
    }}

    execute {{
        let recipient = getAccount(recipient)
        let depositRef = recipient
            .capabilities.borrow<&{{NonFungibleToken.CollectionPublic}}>({contract_name}.CollectionPublicPath)
            ?? panic("Could not borrow a reference to the recipient's collection")

        let nft <- self.withdrawRef.withdraw(withdrawID: withdrawID)
        depositRef.deposit(token: <-nft)
    }}
}}''',
            "setup_collection": f'''import NonFungibleToken from 0xNonFungibleToken
import {contract_name} from 0x01

transaction {{
    prepare(signer: auth(BorrowValue, IssueStorageCapabilityController, PublishCapability, SaveValue) &Account) {{
        if signer.storage.borrow<&{contract_name}.Collection>(from: {contract_name}.CollectionStoragePath) == nil {{
            let collection <- {contract_name}.createEmptyCollection(nftType: Type<@{contract_name}.NFT>())
            signer.storage.save(<-collection, to: {contract_name}.CollectionStoragePath)

            let collectionCap = signer.capabilities.storage.issue<&{{NonFungibleToken.CollectionPublic}}>({contract_name}.CollectionStoragePath)
            signer.capabilities.publish(collectionCap, at: {contract_name}.CollectionPublicPath)
        }}
    }}
}}'''
        }
    
    def _generate_nft_scripts(self, contract_name: str) -> Dict[str, str]:
        """Generate NFT-specific scripts."""
        return {
            "get_collection_ids": f'''import NonFungibleToken from 0xNonFungibleToken
import {contract_name} from 0x01

access(all) fun main(account: Address): [UInt64] {{
    let collection = getAccount(account)
        .capabilities.borrow<&{{NonFungibleToken.CollectionPublic}}>({contract_name}.CollectionPublicPath)
        ?? panic("Could not borrow a reference to the collection")

    return collection.getIDs()
}}''',
            "get_nft_metadata": f'''import NonFungibleToken from 0xNonFungibleToken
import {contract_name} from 0x01

access(all) fun main(account: Address, itemID: UInt64): {{String: String}} {{
    let collection = getAccount(account)
        .capabilities.borrow<&{{NonFungibleToken.CollectionPublic}}>({contract_name}.CollectionPublicPath)
        ?? panic("Could not borrow a reference to the collection")

    let nft = collection.borrowNFT(itemID)
    return nft.getMetadata()
}}''',
            "get_total_supply": f'''import {contract_name} from 0x01

access(all) fun main(): UInt64 {{
    return {contract_name}.totalSupply
}}'''
        }
    
    def _generate_nft_tests(self, contract_name: str) -> Dict[str, str]:
        """Generate NFT-specific tests."""
        return {
            "test_nft_deployment": f'''import Test
import {contract_name} from "../contracts/{contract_name}.cdc"

access(all) fun testContractDeployment() {{
    let account = Test.createAccount()
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
}}'''
        }
    
    # Generic generators for other contract types
    def _generate_generic_transactions(self, contract_name: str) -> Dict[str, str]:
        """Generate generic transactions."""
        return {
            "deploy_contract": f'''import {contract_name} from 0x01

transaction() {{
    prepare(signer: auth(BorrowValue) &Account) {{
        log("Contract {contract_name} deployed successfully")
    }}

    execute {{
        log("Executing deployment transaction")
    }}
}}''',
            "interact_contract": f'''import {contract_name} from 0x01

transaction() {{
    prepare(signer: auth(BorrowValue) &Account) {{
        log("Interacting with contract {contract_name}")
    }}

    execute {{
        log("Contract interaction completed")
    }}
}}'''
        }
    
    def _generate_generic_scripts(self, contract_name: str) -> Dict[str, str]:
        """Generate generic scripts."""
        return {
            "read_contract_data": f'''import {contract_name} from 0x01

access(all) fun main(): String {{
    return "Contract {contract_name} is deployed and accessible"
}}''',
            "check_contract_status": f'''import {contract_name} from 0x01

access(all) fun main(): Bool {{
    return true
}}'''
        }
    
    def _generate_generic_tests(self, contract_name: str) -> Dict[str, str]:
        """Generate generic tests."""
        return {
            "test_deployment": f'''import Test
import {contract_name} from "../contracts/{contract_name}.cdc"

access(all) fun testContractDeployment() {{
    let account = Test.createAccount()
    let err = Test.deployContract(
        name: "{contract_name}",
        path: "../contracts/{contract_name}.cdc",
        arguments: []
    )
    Test.expect(err, Test.beNil())
}}'''
        }
    
    # Placeholder methods for other contract types
    def _generate_defi_transactions(self, contract_name: str) -> Dict[str, str]:
        return self._generate_generic_transactions(contract_name)
    
    def _generate_defi_scripts(self, contract_name: str) -> Dict[str, str]:
        return self._generate_generic_scripts(contract_name)
    
    def _generate_defi_tests(self, contract_name: str) -> Dict[str, str]:
        return self._generate_generic_tests(contract_name)
    
    def _generate_marketplace_transactions(self, contract_name: str) -> Dict[str, str]:
        return self._generate_generic_transactions(contract_name)
    
    def _generate_marketplace_scripts(self, contract_name: str) -> Dict[str, str]:
        return self._generate_generic_scripts(contract_name)
    
    def _generate_marketplace_tests(self, contract_name: str) -> Dict[str, str]:
        return self._generate_generic_tests(contract_name)
    
    def _generate_governance_transactions(self, contract_name: str) -> Dict[str, str]:
        return self._generate_generic_transactions(contract_name)
    
    def _generate_governance_scripts(self, contract_name: str) -> Dict[str, str]:
        return self._generate_generic_scripts(contract_name)
    
    def _generate_governance_tests(self, contract_name: str) -> Dict[str, str]:
        return self._generate_generic_tests(contract_name)