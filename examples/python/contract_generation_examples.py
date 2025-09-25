#!/usr/bin/env python3
"""
Contract Generation Examples

This file demonstrates various contract generation patterns and best practices
for the Smart Contract LLM Builder platform.
"""

import os
import sys
import json
from datetime import datetime

# Add the parent directory to the path to import our client
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from smart_contract_client import SmartContractClient, FlowNetwork


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")


def print_contract_result(result, title: str = None):
    """Print contract generation result."""
    if title:
        print(f"\n{title}:")
    print(f"Submission ID: {result.id}")
    print(f"Status: {result.status}")
    print(f"Generated at: {result.created_at}")

    if result.generated_config:
        config = result.generated_config
        print(f"Config ID: {config['id']}")
        print(f"Validation: {config['validation_status']}")
        print(f"Provider: {config['llm_metadata']['provider']}")
        print(f"Model: {config['llm_metadata']['model']}")
        print(f"Tokens: {config['llm_metadata']['tokens_used']}")


def main():
    """Main function demonstrating contract generation patterns."""

    print_section("Smart Contract LLM Builder - Contract Generation Examples")

    # Initialize client
    client = SmartContractClient(
        base_url="http://localhost:8000/api/v1",
        email=os.getenv('SMART_CONTRACT_EMAIL', 'user@example.com'),
        password=os.getenv('SMART_CONTRACT_PASSWORD', 'password')
    )

    try:
        # Authenticate
        print("Authenticating...")
        client.login()
        print("✅ Authentication successful")

        # Example 1: Basic NFT Contract
        print_section("Example 1: Basic NFT Contract")
        nft_description = """
        Create a simple NFT contract with the following features:
        - Unique NFT IDs with sequential numbering
        - Metadata storage (name, description, image URL)
        - Only contract owner can mint new NFTs
        - Users can transfer NFTs to other accounts
        - Public function to check NFT ownership
        - Event emissions for minting and transfers
        """

        nft_result = client.generate_contract(
            description=nft_description,
            network=FlowNetwork.TESTNET,
            pre_conditions={
                "accounts": {"owner": "0x123"}
            },
            post_conditions={
                "deployed_contracts": ["SimpleNFT"],
                "created_resources": ["NFT", "Collection"],
                "expected_functions": ["mint", "transfer", "getOwner", "getMetadata"]
            }
        )
        print_contract_result(nft_result, "Basic NFT Contract")

        # Example 2: Fungible Token with Advanced Features
        print_section("Example 2: Advanced Fungible Token")
        token_description = """
        Create an advanced fungible token contract with these features:
        - Total supply of 10,000,000 tokens with 18 decimal places
        - Initial minting to contract creator
        - Standard FungibleToken interface compliance
        - Vault resource with deposit/withdraw/burn capabilities
        - Admin resource for minting new tokens
        - Events for Mint, Burn, Deposit, Withdraw, Transfer
        - Public capabilities for the vault
        - Pause functionality controlled by admin
        - Fee mechanism for transfers (1% fee)
        """

        token_result = client.generate_contract(
            description=token_description,
            network=FlowNetwork.TESTNET,
            pre_conditions={
                "tokens": {
                    "total_supply": 10000000,
                    "decimals": 18,
                    "token_name": "AdvancedToken",
                    "symbol": "ATK"
                }
            },
            post_conditions={
                "deployed_contracts": ["AdvancedToken"],
                "created_resources": ["Vault", "Admin", "FeeCollector"],
                "expected_functions": ["mint", "burn", "transfer", "balance", "pause", "unpause"]
            }
        )
        print_contract_result(token_result, "Advanced Fungible Token")

        # Example 3: NFT Marketplace
        print_section("Example 3: NFT Marketplace")
        marketplace_description = """
        Create an NFT marketplace contract with the following features:
        - NFT owners can list their NFTs for sale
        - Buyers can purchase listed NFTs using FLOW tokens
        - Marketplace takes 2.5% commission on each sale
        - Auction functionality with bidding system
        - Fixed price and auction listings
        - Cancel listing functionality for sellers
        - Withdraw funds for sellers
        - Events for listing, purchase, auction start/end, bid
        - Admin controls for fee management
        """

        marketplace_result = client.generate_contract(
            description=marketplace_description,
            network=FlowNetwork.TESTNET,
            pre_conditions={
                "accounts": {
                    "marketplace_admin": "0x123",
                    "fee_collector": "0x456"
                },
                "tokens": {
                    "payment_token": "A.123.FungibleToken"
                }
            },
            post_conditions={
                "deployed_contracts": ["NFTMarketplace"],
                "created_resources": ["Marketplace", "Listing", "Auction"],
                "expected_functions": ["listNFT", "buyNFT", "startAuction", "placeBid", "endAuction", "cancelListing", "withdrawFunds"]
            }
        )
        print_contract_result(marketplace_result, "NFT Marketplace")

        # Example 4: Staking Contract
        print_section("Example 4: Token Staking Contract")
        staking_description = """
        Create a token staking contract with these features:
        - Users can stake tokens for predefined periods (30, 90, 180, 365 days)
        - Different APY rates based on staking duration (5%, 8%, 12%, 15%)
        - Early unstaking with 10% penalty
        - Rewards compound daily
        - Minimum stake amount of 100 tokens
        - Maximum total stake limit of 1,000,000 tokens
        - Admin can adjust APY rates
        - Events for stake, unstake, reward distribution
        - Emergency pause functionality
        """

        staking_result = client.generate_contract(
            description=staking_description,
            network=FlowNetwork.TESTNET,
            pre_conditions={
                "tokens": {
                    "staking_token": "A.123.StakingToken",
                    "rewards_token": "A.123.RewardsToken"
                },
                "rates": {
                    "30_days": 0.05,
                    "90_days": 0.08,
                    "180_days": 0.12,
                    "365_days": 0.15
                }
            },
            post_conditions={
                "deployed_contracts": ["StakingContract"],
                "created_resources": ["StakingPool", "StakePosition", "RewardCalculator"],
                "expected_functions": ["stake", "unstake", "claimRewards", "getAPY", "getStakedAmount", "calculateRewards"]
            }
        )
        print_contract_result(staking_result, "Token Staking Contract")

        # Example 5: DAO Governance Contract
        print_section("Example 5: DAO Governance Contract")
        dao_description = """
        Create a DAO governance contract with the following features:
        - Governance token required for voting
        - Token holders can create proposals
        - Voting power based on token holdings
        - Minimum voting period of 3 days
        - Quorum requirement of 20% for proposal validity
        - Majority approval (50%+1) for proposal execution
        - Proposal types: Parameter changes, fund transfers, contract upgrades
        - Timelock for executed proposals (24 hours)
        - Admin can veto malicious proposals
        - Delegation functionality for voting
        - Events for proposal creation, voting, execution
        """

        dao_result = client.generate_contract(
            description=dao_description,
            network=FlowNetwork.TESTNET,
            pre_conditions={
                "tokens": {
                    "governance_token": "A.123.GovernanceToken"
                },
                "parameters": {
                    "min_voting_period": 259200,  # 3 days in seconds
                    "quorum_requirement": 0.20,
                    "majority_threshold": 0.50,
                    "timelock_duration": 86400  # 24 hours in seconds
                }
            },
            post_conditions={
                "deployed_contracts": ["DAOContract"],
                "created_resources": ["Proposal", "Vote", "Timelock"],
                "expected_functions": ["createProposal", "vote", "executeProposal", "delegate", "undelegate", "vetoProposal"]
            }
        )
        print_contract_result(dao_result, "DAO Governance Contract")

        # Example 6: Multi-Signature Wallet
        print_section("Example 6: Multi-Signature Wallet")
        multisig_description = """
        Create a multi-signature wallet contract with these features:
        - Support for 2-of-3, 3-of-5, and other threshold configurations
        - Owners can submit transactions for approval
        - Required number of confirmations to execute transactions
        - Transaction types: FLOW transfers, token transfers, contract calls
        - Time lock for executed transactions (optional)
        - Daily transaction limit
        - Emergency shutdown by majority owners
        - Add/remove owners with threshold approval
        - Change threshold with threshold approval
        - Events for transaction submission, confirmation, execution
        - Transaction history tracking
        """

        multisig_result = client.generate_contract(
            description=multisig_description,
            network=FlowNetwork.TESTNET,
            pre_conditions={
                "accounts": {
                    "owners": ["0x123", "0x456", "0x789"]
                },
                "parameters": {
                    "threshold": 2,
                    "daily_limit": 1000.0,
                    "timelock": 3600  # 1 hour in seconds
                }
            },
            post_conditions={
                "deployed_contracts": ["MultiSigWallet"],
                "created_resources": ["Transaction", "Confirmation", "Wallet"],
                "expected_functions": ["submitTransaction", "confirmTransaction", "executeTransaction", "addOwner", "removeOwner", "changeThreshold", "emergencyShutdown"]
            }
        )
        print_contract_result(multisig_result, "Multi-Signature Wallet")

        # Example 7: Decentralized Exchange (DEX)
        print_section("Example 7: Decentralized Exchange")
        dex_description = """
        Create a decentralized exchange contract with these features:
        - Automated Market Maker (AMM) model
        - Liquidity pools for token pairs
        - Constant product formula (x * y = k)
        - Liquidity providers can add/remove liquidity
        - Users can swap tokens with 0.3% fee
        - Fee distribution to liquidity providers
        - Price oracle functionality
        - Flash loan protection
        - Admin controls for fee management
        - Events for swaps, liquidity additions/removals
        - TWAP (Time-Weighted Average Price) oracle
        """

        dex_result = client.generate_contract(
            description=dex_description,
            network=FlowNetwork.TESTNET,
            pre_conditions={
                "tokens": {
                    "base_token": "A.123.BaseToken",
                    "quote_token": "A.123.QuoteToken"
                },
                "parameters": {
                    "fee_rate": 0.003,  # 0.3%
                    "min_liquidity": 100.0,
                    "max_slippage": 0.05  # 5%
                }
            },
            post_conditions={
                "deployed_contracts": ["DecentralizedExchange"],
                "created_resources": ["LiquidityPool", "Swap", "LiquidityPosition"],
                "expected_functions": ["addLiquidity", "removeLiquidity", "swapTokens", "getPrice", "getReserves", "calculateSwapAmount"]
            }
        )
        print_contract_result(dex_result, "Decentralized Exchange")

        # Example 8: Gaming NFT Contract
        print_section("Example 8: Gaming NFT Contract")
        gaming_description = """
        Create a gaming NFT contract with the following features:
        - Character NFTs with attributes (level, experience, health, attack, defense)
        - Equipment NFTs (weapons, armor, items) with stat bonuses
        - Crafting system to combine items
        - Battle system for character vs character combat
        - Experience and leveling system
        - Guild system for grouping players
        - Tournament functionality with prizes
        - Random item generation with rarity (common, rare, epic, legendary)
        - Events for battles, leveling, crafting, tournaments
        - Admin functions for game balance adjustments
        """

        gaming_result = client.generate_contract(
            description=gaming_description,
            network=FlowNetwork.TESTNET,
            pre_conditions={
                "accounts": {
                    "game_admin": "0x123",
                    "tournament_manager": "0x456"
                },
                "parameters": {
                    "max_level": 100,
                    "base_experience": 100,
                    "experience_multiplier": 1.5
                }
            },
            post_conditions={
                "deployed_contracts": ["GameNFT"],
                "created_resources": ["Character", "Equipment", "Guild", "Tournament"],
                "expected_functions": ["mintCharacter", "mintEquipment", "battle", "craftItem", "joinGuild", "createTournament", "levelUp", "equipItem"]
            }
        )
        print_contract_result(gaming_result, "Gaming NFT Contract")

        # Example 9: Real Estate NFT Contract
        print_section("Example 9: Real Estate NFT Contract")
        real_estate_description = """
        Create a real estate NFT contract with these features:
        - Property NFTs representing real-world real estate
        - Property metadata (address, size, value, type, images)
        - Rental agreement functionality
        - Property ownership history tracking
        - Mortgage/smart loan integration
        - Property valuation updates by authorized oracles
        - Fractional ownership support
        - Property management fees
        - Legal document attachments (hashed and verified)
        - Events for property transfers, rentals, valuations
        - Compliance with real estate regulations
        """

        real_estate_result = client.generate_contract(
            description=real_estate_description,
            network=FlowNetwork.TESTNET,
            pre_conditions={
                "accounts": {
                    "property_manager": "0x123",
                    "valuation_oracle": "0x456",
                    "legal_verifier": "0x789"
                },
                "parameters": {
                    "management_fee": 0.02,  # 2%
                    "min_property_value": 10000.0,
                    "max_ownership_percentage": 0.10  # 10% max fractional ownership
                }
            },
            post_conditions={
                "deployed_contracts": ["RealEstateNFT"],
                "created_resources": ["Property", "RentalAgreement", "Mortgage", "Valuation"],
                "expected_functions": ["mintProperty", "createRental", "transferProperty", "updateValuation", "createMortgage", "payRent", "forecloseMortgage"]
            }
        )
        print_contract_result(real_estate_result, "Real Estate NFT Contract")

        # Example 10: Supply Chain Contract
        print_section("Example 10: Supply Chain Contract")
        supply_chain_description = """
        Create a supply chain tracking contract with these features:
        - Product NFTs representing physical items
        - Supply chain stage tracking (manufacturing, shipping, delivery)
        - QR code integration for physical verification
        - Authenticity verification and anti-counterfeiting
        - Environmental impact tracking (carbon footprint)
        - Quality control checkpoints
        - Recall functionality for defective products
        - Supplier reputation system
- Insurance integration for lost/damaged goods
- Events for stage transitions, quality checks, recalls
- Regulatory compliance tracking
        """

        supply_chain_result = client.generate_contract(
            description=supply_chain_description,
            network=FlowNetwork.TESTNET,
            pre_conditions={
                "accounts": {
                    "manufacturer": "0x123",
                    "shipper": "0x456",
                    "retailer": "0x789",
                    "insurer": "0xabc"
                },
                "parameters": {
                    "quality_threshold": 0.95,
                    "insurance_rate": 0.01,
                    "recall_compensation": 0.80
                }
            },
            post_conditions={
                "deployed_contracts": ["SupplyChain"],
                "created_resources": ["Product", "Shipment", "QualityCheck", "InsurancePolicy"],
                "expected_functions": ["manufactureProduct", "shipProduct", "deliverProduct", "qualityCheck", "verifyAuthenticity", "initiateRecall", "fileInsuranceClaim"]
            }
        )
        print_contract_result(supply_chain_result, "Supply Chain Contract")

        print_section("Summary")
        print("🎉 Contract generation examples completed!")
        print(f"\nGenerated {10} different contract types:")
        print("1. Basic NFT Contract")
        print("2. Advanced Fungible Token")
        print("3. NFT Marketplace")
        print("4. Token Staking Contract")
        print("5. DAO Governance Contract")
        print("6. Multi-Signature Wallet")
        print("7. Decentralized Exchange")
        print("8. Gaming NFT Contract")
        print("9. Real Estate NFT Contract")
        print("10. Supply Chain Contract")

        print(f"\nBest practices demonstrated:")
        print("✅ Clear, specific contract descriptions")
        print("✅ Proper pre-conditions and post-conditions")
        print("✅ Detailed feature specifications")
        print("✅ Security considerations")
        print("✅ Event emissions")
        print("✅ Admin controls")
        print("✅ Parameter configuration")
        print("✅ Resource definitions")

        print(f"\nEach contract is ready for deployment to testnet!")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()