import Test
import AutoToken from "../contracts/AutoToken.cdc"

access(all) fun testContractDeployment() {
    let account = Test.createAccount()
    let err = Test.deployContract(
        name: "AutoToken",
        path: "../contracts/AutoToken.cdc",
        arguments: []
    )
    Test.expect(err, Test.beNil())
}

access(all) fun testInitialSupply() {
    let supply = AutoToken.totalSupply
    Test.expect(supply, Test.equal(0.0))
}