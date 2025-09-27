// WalletManager.cdc

contract WalletManager {

    // Events
    event WalletCreated(address: Address, walletID: UInt64)
    event WalletUpdated(address: Address, walletID: UInt64, newBalance: UFix64)
    event WalletDeleted(address: Address, walletID: UInt64)

    // Resource Interface
    resource interface IWallet {
        fun deposit(withdraw: @Token)
        fun withdraw(amount: UFix64): @Token
        fun getBalance(): UFix64
        fun getID(): UInt64
    }

    // Resource
    resource Wallet: IWallet {
        let id: UInt64
        var balance: UFix64
        let owner: Address

        init(id: UInt64, owner: Address) {
            pre {
                id > 0: "ID must be greater than 0"
            }
            self.id = id
            self.balance = 0.0
            self.owner = owner
        }

        fun deposit(withdraw: @Token) {
            pre {
                withdraw.balance > 0.0: "Withdrawal balance must be positive"
            }
            self.balance = self.balance + withdraw.balance
            destroy withdraw
        }

        fun withdraw(amount: UFix64): @Token {
            pre {
                amount > 0.0: "Withdrawal amount must be positive"
                amount <= self.balance: "Insufficient balance"
            }
            self.balance = self.balance - amount
            return <-create Token(balance: amount)
        }

        fun getBalance(): UFix64 {
            return self.balance
        }

        fun getID(): UInt64 {
            return self.id
        }
    }

    // Mapping of wallet IDs to their respective resources
    var wallets: @{UInt64: Wallet}

    init() {
        self.wallets <- {}
    }

    // Function to create a new wallet
    fun createWallet(): UInt64 {
        let newID = UInt64(self.wallets.length + 1)
        let newWallet <- create Wallet(id: newID, owner: self.account.address)
        self.wallets[newID] <-! newWallet
        emit WalletCreated(address: self.account.address, walletID: newID)
        return newID
    }

    // Function to get a wallet capability
    fun getWalletCapability(walletID: UInt64): Capability<&Wallet> {
        pre {
            self.wallets[walletID] != nil: "Wallet does not exist"
        }
        return self.account.capabilities.storage.issue<&Wallet>(self.wallets[walletID]!)
    }

    // Function to update a wallet balance
    fun updateWalletBalance(walletID: UInt64, newBalance: UFix64) {
        pre {
            self.wallets[walletID] != nil: "Wallet does not exist"
        }
        let wallet = self.wallets[walletID]!
        wallet.balance = newBalance
        emit WalletUpdated(address: self.account.address, walletID: walletID, newBalance: newBalance)
    }

    // Function to delete a wallet
    fun deleteWallet(walletID: UInt64) {
        pre {
            self.wallets[walletID] != nil: "Wallet does not exist"
        }
        let wallet <- self.wallets.remove(key: walletID)!
        destroy wallet
        emit WalletDeleted(address: self.account.address, walletID: walletID)
    }

    // Token Resource (example, might need to be adjusted based on actual token contract)
    resource Token {
        var balance: UFix64

        init(balance: UFix64) {
            self.balance = balance
        }
    }
}

// Example transaction to create a new wallet
transaction {
    prepare(acct: &Account) {
        let walletManager = acct.contracts.get("WalletManager")?.borrow<&WalletManager>()!
        let newWalletID = walletManager.createWallet()
        log("New wallet ID: ".concat(newWalletID.toString()))
    }
}

// Example script to get a wallet balance
fun main(account: Address, walletID: UInt64): UFix64 {
    let walletManager = getAccount(account).contracts.get("WalletManager")?.borrow<&WalletManager>()!
    let walletCap = walletManager.getWalletCapability(walletID: walletID)
    let wallet = walletCap.borrow()!
    return wallet.getBalance()
}