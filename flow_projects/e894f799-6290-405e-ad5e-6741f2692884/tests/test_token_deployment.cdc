import Test
import APITestToken from "../contracts/APITestToken.cdc"

access(all) fun testContractDeployment() {
    let account = Test.createAccount()
    let err = Test.deployContract(
        name: "APITestToken",
        path: "../contracts/APITestToken.cdc",
        arguments: []
    )
    Test.expect(err, Test.beNil())
}

access(all) fun testInitialSupply() {
    let supply = APITestToken.totalSupply
    Test.expect(supply, Test.equal(0.0))
}