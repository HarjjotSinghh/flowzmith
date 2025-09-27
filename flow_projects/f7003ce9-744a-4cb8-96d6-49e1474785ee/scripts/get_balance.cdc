import FungibleToken from 0xFungibleToken
import Property from 0x01

access(all) fun main(account: Address): UFix64 {
    let vaultRef = getAccount(account)
        .capabilities.borrow<&{FungibleToken.Balance}>(Property.BalancePublicPath)
        ?? panic("Could not borrow Balance reference to the Vault")

    return vaultRef.balance
}