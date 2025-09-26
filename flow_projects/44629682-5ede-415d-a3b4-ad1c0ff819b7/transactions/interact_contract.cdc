import Contract from 0x01

transaction() {
    prepare(signer: auth(BorrowValue) &Account) {
        log("Interacting with contract Contract")
    }

    execute {
        log("Contract interaction completed")
    }
}