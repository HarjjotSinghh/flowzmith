import Test
import SoftwareTest from "../contracts/SoftwareTest.cdc"

access(all) fun testContractDeployment() {
    let account = Test.createAccount()
    let err = Test.deployContract(
        name: "SoftwareTest",
        path: "../contracts/SoftwareTest.cdc",
        arguments: []
    )
    Test.expect(err, Test.beNil())
}