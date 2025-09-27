import FungibleToken from 0xFungibleToken
import AutoToken from 0x01

access(all) fun main(account: Address): UFix64 {
    let vaultRef = getAccount(account)
        .capabilities.borrow<&{FungibleToken.Balance}>(AutoToken.BalancePublicPath)
        ?? panic("Could not borrow Balance reference to the Vault")

    return vaultRef.balance
}