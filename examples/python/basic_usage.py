#!/usr/bin/env python3
"""
Basic usage example for Smart Contract LLM Builder

This example demonstrates the most common use cases:
1. User authentication
2. Contract generation from natural language
3. Contract deployment
4. Monitoring deployment status
"""

import os
import sys
import time
from datetime import datetime

# Add the parent directory to the path to import our client
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from smart_contract_client import SmartContractClient, FlowNetwork, APIError, AuthenticationError, DeploymentError


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")


def print_result(result: dict, title: str = None):
    """Print a formatted result."""
    if title:
        print(f"\n{title}:")
    print(json.dumps(result, indent=2, default=str))


def main():
    """Main function demonstrating basic usage."""

    print_section("Smart Contract LLM Builder - Basic Usage Example")

    # Initialize client
    print("Initializing Smart Contract Client...")
    client = SmartContractClient(
        base_url="http://localhost:8000/api/v1",
        email=os.getenv('SMART_CONTRACT_EMAIL', 'user@example.com'),
        password=os.getenv('SMART_CONTRACT_PASSWORD', 'password')
    )

    try:
        # Step 1: Authenticate
        print_section("1. User Authentication")
        print("Logging in...")

        try:
            auth_result = client.login()
            print("✅ Login successful!")
            print(f"User: {auth_result['data']['user']['email']}")
            print(f"Token expires in: {auth_result['data']['expires_in']} seconds")
        except AuthenticationError as e:
            print(f"❌ Authentication failed: {e}")
            print("Please check your credentials and try again.")
            return

        # Step 2: Get user information
        print_section("2. User Information")
        try:
            user_info = client.get_user_info()
            print("✅ User information retrieved:")
            print(f"   ID: {user_info.id}")
            print(f"   Email: {user_info.email}")
            print(f"   Persona Type: {user_info.persona_type}")
            print(f"   Full Name: {user_info.full_name}")
            print(f"   Organization: {user_info.organization}")
            print(f"   Account Active: {user_info.is_active}")
            print(f"   Member Since: {user_info.created_at}")
        except APIError as e:
            print(f"❌ Failed to get user info: {e}")

        # Step 3: Generate a simple NFT contract
        print_section("3. Contract Generation - Simple NFT")
        print("Generating NFT contract from natural language...")

        nft_description = """
        Create a simple NFT contract with the following features:
        - Each NFT has a unique ID and metadata (name, description, image URL)
        - Only contract owner can mint new NFTs
        - Users can transfer their NFTs to other accounts
        - Include a function to get NFT metadata by ID
        - Include a function to check if an account owns a specific NFT
        - Emit events for minting and transfers
        """

        try:
            nft_submission = client.generate_contract(
                description=nft_description,
                network=FlowNetwork.TESTNET,
                pre_conditions={
                    "accounts": {
                        "owner": "0x123"
                    }
                },
                post_conditions={
                    "deployed_contracts": ["SimpleNFT"],
                    "created_resources": ["NFT", "Collection"],
                    "expected_functions": ["mint", "transfer", "getMetadata", "ownsNFT"]
                }
            )

            print("✅ NFT contract generated successfully!")
            print(f"   Submission ID: {nft_submission.id}")
            print(f"   Status: {nft_submission.status}")
            print(f"   Input Type: {nft_submission.input_type.value}")
            print(f"   Created At: {nft_submission.created_at}")

            # Display generated contract info
            if nft_submission.generated_config:
                config = nft_submission.generated_config
                print(f"   Config ID: {config['id']}")
                print(f"   Validation Status: {config['validation_status']}")
                print(f"   LLM Provider: {config['llm_metadata']['provider']}")
                print(f"   Tokens Used: {config['llm_metadata']['tokens_used']}")
                print(f"   Generation Time: {config['llm_metadata']['generation_time_ms']}ms")

        except APIError as e:
            print(f"❌ Contract generation failed: {e}")
            return

        # Step 4: Generate a token contract
        print_section("4. Contract Generation - Fungible Token")
        print("Generating token contract from natural language...")

        token_description = """
        Create a fungible token contract with the following features:
        - Total supply of 1,000,000 tokens
        - Initial supply minted to contract creator
        - Standard transfer functionality with balance checking
        - Mint function that only the admin can call
        - Burn function allowing users to destroy their tokens
        - Events for minting, burning, and transfers
        - Public capabilities for the vault
        """

        try:
            token_submission = client.generate_contract(
                description=token_description,
                network=FlowNetwork.TESTNET,
                pre_conditions={
                    "tokens": {
                        "total_supply": 1000000,
                        "token_name": "MyToken"
                    }
                },
                post_conditions={
                    "deployed_contracts": ["FungibleToken"],
                    "created_resources": ["Vault", "Admin"],
                    "expected_functions": ["transfer", "mint", "burn", "balance"]
                }
            )

            print("✅ Token contract generated successfully!")
            print(f"   Submission ID: {token_submission.id}")
            print(f"   Status: {token_submission.status}")

        except APIError as e:
            print(f"❌ Token contract generation failed: {e}")

        # Step 5: Deploy the NFT contract
        print_section("5. Contract Deployment")
        print("Deploying NFT contract to testnet...")

        try:
            # Get the config ID from the generated contract
            config_id = nft_submission.generated_config['id']

            deployment = client.deploy_contract(
                submission_id=nft_submission.id,
                network=FlowNetwork.TESTNET,
                config_id=config_id,
                gas_limit=1000
            )

            print("✅ Contract deployment initiated!")
            print(f"   Deployment ID: {deployment.id}")
            print(f"   Status: {deployment.status.value}")
            print(f"   Network: {deployment.network}")
            print(f"   Gas Limit: 1000")
            print(f"   Started At: {deployment.created_at}")

            # If deployment is successful, show additional details
            if deployment.status.value == "SUCCESS":
                print(f"   Transaction Hash: {deployment.transaction_hash}")
                print(f"   Contract Address: {deployment.contract_address}")
                print(f"   Gas Used: {deployment.gas_used}")
                print(f"   Execution Time: {deployment.execution_time_ms}ms")
            elif deployment.status.value == "FAILED":
                print(f"   Error: {deployment.error_details}")
                print(f"   Log Content: {deployment.log_content}")

        except APIError as e:
            print(f"❌ Contract deployment failed: {e}")

        # Step 6: List user's contracts
        print_section("6. Contract History")
        try:
            contracts = client.list_contract_submissions(limit=5)
            print("✅ Retrieved contract history:")
            print(f"   Total Contracts: {contracts['data']['total']}")
            print(f"   Showing: {len(contracts['data']['submissions'])} contracts")

            for contract in contracts['data']['submissions']:
                print(f"\n   Contract ID: {contract['id']}")
                print(f"   Type: {contract['input_type']}")
                print(f"   Status: {contract['status']}")
                print(f"   Created: {contract['created_at']}")

        except APIError as e:
            print(f"❌ Failed to get contract history: {e}")

        # Step 7: Search documentation
        print_section("7. Documentation Search")
        try:
            search_results = client.search_documentation(
                query="How to create resources in Cadence",
                limit=5,
                use_semantic_search=True
            )

            print("✅ Documentation search completed:")
            print(f"   Total Results: {search_results['data']['total_results']}")
            print(f"   Search Time: {search_results['data']['search_time_ms']}ms")
            print(f"   Showing Results: {len(search_results['data']['results'])}")

            for i, doc in enumerate(search_results['data']['results'][:3], 1):
                print(f"\n   {i}. {doc['title']}")
                print(f"      Type: {doc['content_type']}")
                print(f"      Source: {doc['source']}")
                print(f"      Relevance: {doc['relevance_score']:.2f}")
                print(f"      Preview: {doc['content'][:100]}...")

        except APIError as e:
            print(f"❌ Documentation search failed: {e}")

        # Step 8: Get system statistics
        print_section("8. System Statistics")
        try:
            stats = client.get_statistics()
            print("✅ System statistics retrieved:")

            # User statistics
            user_stats = stats['data']['users']
            print(f"\n   Users:")
            print(f"      Total: {user_stats['total']}")
            print(f"      Active: {user_stats['active']}")
            print(f"      Developers: {user_stats['by_persona_type']['DEVELOPER']}")
            print(f"      Business Users: {user_stats['by_persona_type']['BUSINESS_USER']}")

            # Contract statistics
            contract_stats = stats['data']['contracts']
            print(f"\n   Contracts:")
            print(f"      Total Submissions: {contract_stats['total_submissions']}")
            print(f"      Successful Deployments: {contract_stats['successful_deployments']}")
            print(f"      Success Rate: {contract_stats['success_rate']:.1%}")

            # System statistics
            system_stats = stats['data']['system']
            print(f"\n   System:")
            print(f"      Version: {system_stats['version']}")
            print(f"      Uptime: {system_stats['uptime']}")
            print(f"      Last Deployed: {system_stats['last_deployed']}")

        except APIError as e:
            print(f"❌ Failed to get statistics: {e}")

        # Step 9: Get learning insights
        print_section("9. Learning Insights")
        try:
            insights = client.get_learning_insights(limit=5)
            print("✅ Learning insights retrieved:")

            learning_stats = insights['data']
            print(f"   Total Patterns: {learning_stats['total_patterns']}")
            print(f"   Average Confidence: {learning_stats['average_confidence_score']:.2f}")
            print(f"   Applied to Generation: {learning_stats['patterns_applied_to_generation']}")

            for insight in learning_stats['insights'][:3]:
                print(f"\n   Pattern Type: {insight['pattern_type']}")
                print(f"   Confidence: {insight['confidence_score']:.2f}")
                print(f"   Applied: {insight['applied_to_generation']}")
                print(f"   Created: {insight['created_at']}")

        except APIError as e:
            print(f"❌ Failed to get learning insights: {e}")

        print_section("10. Summary")
        print("🎉 Basic usage example completed successfully!")
        print("\nKey accomplishments:")
        print("✅ User authentication")
        print("✅ Contract generation from natural language")
        print("✅ Contract deployment initiation")
        print("✅ Contract history retrieval")
        print("✅ Documentation search")
        print("✅ System statistics access")
        print("✅ Learning insights retrieval")

        print(f"\nYour contracts are available for deployment and management.")
        print(f"Use the web interface at http://localhost:8000 for detailed contract management.")

    except KeyboardInterrupt:
        print("\n\n⚠️  Example interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Import here to avoid dependency issues
    import json

    # Check for environment variables
    if not os.getenv('SMART_CONTRACT_EMAIL'):
        print("⚠️  SMART_CONTRACT_EMAIL environment variable not set")
        print("Using default: user@example.com")

    if not os.getenv('SMART_CONTRACT_PASSWORD'):
        print("⚠️  SMART_CONTRACT_PASSWORD environment variable not set")
        print("Using default: password")

    # Run the example
    main()