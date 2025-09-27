import Test
import WalletManager from "../contracts/WalletManager.cdc"

access(all) fun testContractDeployment() {
    let account = Test.createAccount()
    let err = Test.deployContract(
        name: "WalletManager",
        path: "../contracts/WalletManager.cdc",
        arguments: []
    )
    Test.expect(err, Test.beNil())
}