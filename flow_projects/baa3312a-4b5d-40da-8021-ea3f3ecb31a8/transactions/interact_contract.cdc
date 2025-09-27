import NewTest from 0x01

transaction() {
    prepare(signer: auth(BorrowValue) &Account) {
        log("Interacting with contract NewTest")
    }

    execute {
        log("Contract interaction completed")
    }
}