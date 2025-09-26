"""
Example usage of the Flow MCP Server
"""

import asyncio
import json
from mcp.mcp_client import MCPFlowClient


async def example_contract_interaction():
    """Example of interacting with contracts."""
    client = MCPFlowClient()
    await client.connect()

    try:
        # List available accounts
        print("=== Available Accounts ===")
        accounts = await client.list_accounts()
        print(json.dumps(accounts, indent=2))

        # View a specific account
        print("\n=== Account Details ===")
        account_address = "0x1654653399040a61"  # Example emulator address
        account = await client.view_account(account_address)
        print(json.dumps(account, indent=2))

        # Get account balance
        print("\n=== Account Balance ===")
        balance = await client.get_account_balance(account_address)
        print(json.dumps(balance, indent=2))

        # View a contract
        print("\n=== Contract Details ===")
        contract_address = "0x1654653399040a61"
        contract_name = "FungibleToken"
        contract = await client.view_contract(contract_address, contract_name)
        print(json.dumps(contract, indent=2))

        # List recent transactions
        print("\n=== Recent Transactions ===")
        transactions = await client.list_transactions(limit=5)
        print(json.dumps(transactions, indent=2))

    finally:
        await client.disconnect()


async def example_contract_deployment():
    """Example of deploying a contract."""
    client = MCPFlowClient()
    await client.connect()

    try:
        # Deploy a contract
        print("=== Deploying Contract ===")
        result = await client.deploy_contract(
            contract_path="./contracts/MyContract.cdc",
            account="emulator-account",
            network="emulator"
        )
        print(json.dumps(result, indent=2))

    finally:
        await client.disconnect()


async def example_contract_call():
    """Example of calling a contract function."""
    client = MCPFlowClient()
    await client.connect()

    try:
        # Call a contract function
        print("=== Calling Contract Function ===")
        result = await client.call_contract({
            "network": "emulator",
            "account": "emulator-account",
            "contract_name": "MyContract",
            "function_name": "myFunction",
            "arguments": ["arg1", "42"]
        })
        print(json.dumps(result, indent=2))

    finally:
        await client.disconnect()


async def main():
    """Run all examples."""
    print("Flow MCP Server Examples")
    print("=" * 50)

    try:
        await example_contract_interaction()
        # Uncomment these if you have contracts deployed
        # await example_contract_deployment()
        # await example_contract_call()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())