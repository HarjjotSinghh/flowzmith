import FungibleToken from 0xFungibleToken
import Property from 0x01

transaction(recipient: Address, amount: UFix64) {
    let tokenAdmin: &Property.Administrator
    let tokenReceiver: &{FungibleToken.Receiver}

    prepare(signer: auth(BorrowValue) &Account) {
        self.tokenAdmin = signer.storage.borrow<&Property.Administrator>(
            from: Property.AdminStoragePath
        ) ?? panic("Signer is not the token admin")

        self.tokenReceiver = getAccount(recipient)
            .capabilities.borrow<&{FungibleToken.Receiver}>(Property.ReceiverPublicPath)
            ?? panic("Unable to borrow receiver reference")
    }

    execute {
        let minter <- self.tokenAdmin.createNewMinter(allowedAmount: amount)
        let mintedVault <- minter.mintTokens(amount: amount)
        
        self.tokenReceiver.deposit(from: <-mintedVault)
        destroy minter
    }
}