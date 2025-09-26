import FungibleToken from 0xFungibleToken
import APITestToken from 0x01

transaction(recipient: Address, amount: UFix64) {
    let tokenAdmin: &APITestToken.Administrator
    let tokenReceiver: &{FungibleToken.Receiver}

    prepare(signer: auth(BorrowValue) &Account) {
        self.tokenAdmin = signer.storage.borrow<&APITestToken.Administrator>(
            from: APITestToken.AdminStoragePath
        ) ?? panic("Signer is not the token admin")

        self.tokenReceiver = getAccount(recipient)
            .capabilities.borrow<&{FungibleToken.Receiver}>(APITestToken.ReceiverPublicPath)
            ?? panic("Unable to borrow receiver reference")
    }

    execute {
        let minter <- self.tokenAdmin.createNewMinter(allowedAmount: amount)
        let mintedVault <- minter.mintTokens(amount: amount)
        
        self.tokenReceiver.deposit(from: <-mintedVault)
        destroy minter
    }
}