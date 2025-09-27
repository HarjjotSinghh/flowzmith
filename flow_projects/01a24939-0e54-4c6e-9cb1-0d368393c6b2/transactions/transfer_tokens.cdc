import FungibleToken from 0xFungibleToken
import AutoToken from 0x01

transaction(amount: UFix64, to: Address) {
    let vault: auth(FungibleToken.Withdraw) &AutoToken.Vault

    prepare(signer: auth(BorrowValue) &Account) {
        self.vault = signer.storage.borrow<auth(FungibleToken.Withdraw) &AutoToken.Vault>(
            from: AutoToken.VaultStoragePath
        ) ?? panic("Could not borrow reference to the owner's Vault!")
    }

    execute {
        let receiver = getAccount(to)
            .capabilities.borrow<&{FungibleToken.Receiver}>(AutoToken.ReceiverPublicPath)
            ?? panic("Could not borrow receiver reference to the recipient's Vault")

        let sentVault <- self.vault.withdraw(amount: amount)
        receiver.deposit(from: <-sentVault)
    }
}