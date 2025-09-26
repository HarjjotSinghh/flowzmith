// Sample Flow smart contract for testing

pub contract SampleContract {

    // Events
    pub event ContractInitialized()
    pub event ValueUpdated(newValue: UInt64, updater: Address)

    // State
    access(self) var storedValue: UInt64
    access(self) var owner: Address

    // Initialize
    init() {
        self.storedValue = 0
        self.owner = self.account.address
        emit ContractInitialized()
    }

    // Public functions
    pub fun getValue(): UInt64 {
        return self.storedValue
    }

    pub fun getOwner(): Address {
        return self.owner
    }

    // Transaction functions
    pub fun updateValue(newValue: UInt64) {
        pre {
            self.account.address == self.owner: "Only owner can update value"
        }
        self.storedValue = newValue
        emit ValueUpdated(newValue: newValue, updater: self.account.address)
    }

    // Resource definitions
    pub resource NFT {
        pub let id: UInt64
        pub let metadata: {String: String}

        init(id: UInt64, metadata: {String: String}) {
            self.id = id
            self.metadata = metadata
        }
    }

    // Collection management
    pub resource interface NFTReceiver {
        pub fun deposit(token: @NFT)
        pub fun getIDs(): [UInt64]
        pub fun borrowNFT(id: UInt64): &NFT
    }

    pub resource Collection: NFTReceiver {
        pub var ownedNFTs: @{UInt64: NFT}

        init() {
            self.ownedNFTs <- {}
        }

        destroy() {
            destroy self.ownedNFTs
        }

        pub fun deposit(token: @NFT) {
            let id = token.id
            let oldToken <- self.ownedNFTs[id] <- token
            destroy oldToken
        }

        pub fun getIDs(): [UInt64] {
            return self.ownedNFTs.keys
        }

        pub fun borrowNFT(id: UInt64): &NFT {
            return &self.ownedNFTs[id] as &NFT
        }

        pub fun withdraw(id: UInt64): @NFT {
            let token <- self.ownedNFTs.remove(key: id)
                ?? panic("NFT not found in collection")
            return <-token
        }
    }

    // Public functions for collection management
    pub fun createCollection(): @Collection {
        return <- create Collection()
    }

    pub fun mintNFT(metadata: {String: String}): @NFT {
        return <- create NFT(id: self.storedValue, metadata: metadata)
    }
}