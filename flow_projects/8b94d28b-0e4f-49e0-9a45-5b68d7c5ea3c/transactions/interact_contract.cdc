import TestNew from 0x01

transaction() {
    prepare(signer: auth(BorrowValue) &Account) {
        log("Interacting with contract TestNew")
    }

    execute {
        log("Contract interaction completed")
    }
}