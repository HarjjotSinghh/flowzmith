import SoftwareTest from 0x01

transaction() {
    prepare(signer: auth(BorrowValue) &Account) {
        log("Interacting with contract SoftwareTest")
    }

    execute {
        log("Contract interaction completed")
    }
}