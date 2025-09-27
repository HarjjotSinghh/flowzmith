import FungibleToken from 0xFungibleToken
import Property from 0x01

access(all) fun main(account: Address): Bool {
    let receiverRef = getAccount(account)
        .capabilities.get<&{FungibleToken.Receiver}>(Property.ReceiverPublicPath)
        .check()
    
    let balanceRef = getAccount(account)
        .capabilities.get<&{FungibleToken.Balance}>(Property.BalancePublicPath)
        .check()
    
    return receiverRef && balanceRef
}