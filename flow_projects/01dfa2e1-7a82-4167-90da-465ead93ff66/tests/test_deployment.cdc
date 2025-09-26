import Test
import Organization from "../contracts/Organization.cdc"

access(all) fun testContractDeployment() {
    let account = Test.createAccount()
    let err = Test.deployContract(
        name: "Organization",
        path: "../contracts/Organization.cdc",
        arguments: []
    )
    Test.expect(err, Test.beNil())
}