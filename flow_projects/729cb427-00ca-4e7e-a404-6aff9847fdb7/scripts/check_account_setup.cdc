import FungibleToken from 0xFungibleToken
import AutoToken from 0x01

access(all) fun main(account: Address): Bool {
    let receiverRef = getAccount(account)
        .capabilities.get<&{FungibleToken.Receiver}>(AutoToken.ReceiverPublicPath)
        .check()
    
    let balanceRef = getAccount(account)
        .capabilities.get<&{FungibleToken.Balance}>(AutoToken.BalancePublicPath)
        .check()
    
    return receiverRef && balanceRef
}