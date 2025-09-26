import UserProfile from 0x01

transaction() {
    prepare(signer: auth(BorrowValue) &Account) {
        log("Interacting with contract UserProfile")
    }

    execute {
        log("Contract interaction completed")
    }
}