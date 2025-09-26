import Test2 from 0x01

transaction() {
    prepare(signer: auth(BorrowValue) &Account) {
        log("Interacting with contract Test2")
    }

    execute {
        log("Contract interaction completed")
    }
}