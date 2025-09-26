// SimpleERC20Token.cdc

import FungibleToken from 0xFungibleToken

pub contract SimpleERC20Token: FungibleToken.Provider, FungibleToken.Receiver, FungibleToken.Balance {

    // Total supply of tokens
    pub var totalSupply: UFix64

    // Event emitted when tokens are withdrawn from a vault
    pub event TokensWithdrawn(amount: UFix64, from: Address?)

    // Event emitted when tokens are deposited into a vault
    pub event TokensDeposited(amount: UFix64, to: Address?)

    // Event emitted when a new minter is created
    pub event MinterCreated(minter: Capability<&Minter>)

    // Vault resource definition
    pub resource Vault: FungibleToken.Provider, FungibleToken.Receiver, FungibleToken.Balance {
        pub var balance: UFix64

        init(balance: UFix64) {
            self.balance = balance
        }

        // Withdraw tokens from the vault
        pub fun withdraw(amount: UFix64): @FungibleToken.Vault {
            pre {
                amount > 0.0: "Withdrawal amount must be positive"
                self.balance >= amount: "Insufficient balance"
            }
            self.balance = self.balance - amount
            emit TokensWithdrawn(amount: amount, from: self.owner?.address)
            return <-create Vault(balance: amount)
        }

        // Deposit tokens into the vault
        pub fun deposit(from: @FungibleToken.Vault) {
            pre {
                from.balance > 0.0: "Deposit amount must be positive"
            }
            let vault <- from as! @SimpleERC20Token.Vault
            self.balance = self.balance + vault.balance
            emit TokensDeposited(amount: vault.balance, to: self.owner?.address)
            destroy vault
        }

        // Get the balance of the vault
        pub fun getBalance(): UFix64 {
            return self.balance
        }

        destroy() {
            SimpleERC20Token.totalSupply = SimpleERC20Token.totalSupply - self.balance
        }
    }

    // Minter resource definition
    pub resource Minter {
        // Mint new tokens
        pub fun mint(amount: UFix64): @SimpleERC20Token.Vault {
            pre {
                amount > 0.0: "Mint amount must be positive"
            }
            SimpleERC20Token.totalSupply = SimpleERC20Token.totalSupply + amount
            return <-create Vault(balance: amount)
        }
    }

    // Create a new vault with the given balance
    pub fun createEmptyVault(): @Vault {
        return <-create Vault(balance: 0.0)
    }

    // Create a new minter
    pub fun createMinter(): Capability<&Minter> {
        let minter <- create Minter()
        let minterCap = self.account.capabilities.storage.save(<- minter, name: "minter")
        let minterLink = self.account.capabilities.storage.link<&Minter>(name: "minter", getTarget: minterCap)
        emit MinterCreated(minter: minterLink)
        return minterLink
    }

    init() {
        // Initialize total supply
        self.totalSupply = 0.0

        // Create a vault for the contract
        let vault <- create Vault(balance: 0.0)
        self.account.save(<- vault, to: /storage/simpleERC20TokenVault)

        // Link the vault
        self.account.link<&{FungibleToken.Receiver}>(/public/simpleERC20TokenReceiver, target: /storage/simpleERC20TokenVault)
        self.account.link<&{FungibleToken.Balance}>(/public/simpleERC20TokenBalance, target: /storage/simpleERC20TokenVault)

        // Create a minter
        self.createMinter()
    }
}

// Example transaction to mint tokens
// transaction {
//     let minter: &SimpleERC20Token.Minter
//     let recipient: Capability<&{FungibleToken.Receiver}>
//     prepare(acct: AuthAccount) {
//         self.minter = acct.capabilities.storage.borrow<&SimpleERC20Token.Minter>(name: "minter")!
//         self.recipient = getAccount(0xRecipient).capabilities.get<&{FungibleToken.Receiver}>(/public/simpleERC20TokenReceiver)!
//     }
//     execute {
//         let tokens <- self.minter.mint(amount: 100.0)
//         self.recipient.borrow()!.deposit(from: <- tokens)
//     }
// }

// Example script to get the balance of an account
// pub fun main(address: Address): UFix64 {
//     let account = getAccount(address)
//     let balanceRef = account.capabilities.get<&{FungibleToken.Balance}>(/public/simpleERC20TokenBalance)?.borrow()
//     return balanceRef?.getBalance() ?? 0.0
// }
