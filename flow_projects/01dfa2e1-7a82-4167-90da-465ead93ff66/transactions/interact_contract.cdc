import Organization from 0x01

transaction() {
    prepare(signer: auth(BorrowValue) &Account) {
        log("Interacting with contract Organization")
    }

    execute {
        log("Contract interaction completed")
    }
}