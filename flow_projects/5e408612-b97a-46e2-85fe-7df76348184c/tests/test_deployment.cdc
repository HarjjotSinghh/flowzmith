import Test
import DocumentRWA from "../contracts/DocumentRWA.cdc"

access(all) fun testContractDeployment() {
    let account = Test.createAccount()
    let err = Test.deployContract(
        name: "DocumentRWA",
        path: "../contracts/DocumentRWA.cdc",
        arguments: []
    )
    Test.expect(err, Test.beNil())
}