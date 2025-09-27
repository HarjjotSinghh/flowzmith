import Test
import Property from "../contracts/Property.cdc"

access(all) fun testContractDeployment() {
    let account = Test.createAccount()
    let err = Test.deployContract(
        name: "Property",
        path: "../contracts/Property.cdc",
        arguments: []
    )
    Test.expect(err, Test.beNil())
}

access(all) fun testInitialSupply() {
    let supply = Property.totalSupply
    Test.expect(supply, Test.equal(0.0))
}