import SoftwareTest from 0x01

transaction() {
    prepare(signer: auth(BorrowValue) &Account) {
        log("Contract SoftwareTest deployed successfully")
    }

    execute {
        log("Executing deployment transaction")
    }
}