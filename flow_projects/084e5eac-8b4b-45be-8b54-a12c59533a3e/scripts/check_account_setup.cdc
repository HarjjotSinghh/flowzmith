import FungibleToken from 0xFungibleToken
import APITestToken from 0x01

access(all) fun main(account: Address): Bool {
    let receiverRef = getAccount(account)
        .capabilities.get<&{FungibleToken.Receiver}>(APITestToken.ReceiverPublicPath)
        .check()
    
    let balanceRef = getAccount(account)
        .capabilities.get<&{FungibleToken.Balance}>(APITestToken.BalancePublicPath)
        .check()
    
    return receiverRef && balanceRef
}