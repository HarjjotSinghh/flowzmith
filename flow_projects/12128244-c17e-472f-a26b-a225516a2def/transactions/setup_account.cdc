import FungibleToken from 0xFungibleToken
import Property from 0x01

transaction {
    prepare(signer: auth(BorrowValue, IssueStorageCapabilityController, PublishCapability, SaveValue) &Account) {
        if signer.storage.borrow<&Property.Vault>(from: Property.VaultStoragePath) == nil {
            signer.storage.save(<-Property.createEmptyVault(vaultType: Type<@Property.Vault>()), to: Property.VaultStoragePath)

            let receiverCap = signer.capabilities.storage.issue<&{FungibleToken.Receiver}>(Property.VaultStoragePath)
            signer.capabilities.publish(receiverCap, at: Property.ReceiverPublicPath)

            let balanceCap = signer.capabilities.storage.issue<&{FungibleToken.Balance}>(Property.VaultStoragePath)
            signer.capabilities.publish(balanceCap, at: Property.BalancePublicPath)
        }
    }
}