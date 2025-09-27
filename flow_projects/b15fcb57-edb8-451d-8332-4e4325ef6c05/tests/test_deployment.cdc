import Test
import WalletManager2 from "../contracts/WalletManager2.cdc"

access(all) fun testContractDeployment() {
    let account = Test.createAccount()
    let err = Test.deployContract(
        name: "WalletManager2",
        path: "../contracts/WalletManager2.cdc",
        arguments: []
    )
    Test.expect(err, Test.beNil())
}