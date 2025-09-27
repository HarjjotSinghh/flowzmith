```cadence
// NewTest.cdc

// Import required contracts if needed
// import "FlowContract" from 0x...

pub contract NewTest {
    // Events
    pub event TestCreated(testId: UInt64)
    pub event TestUpdated(testId: UInt64, newStatus: String)
    pub event TestDeleted(testId: UInt64)

    // Resource interface for Test
    pub resource interface ITest {
        pub let id: UInt64
        pub var status: String
        pub var description: String

        pub fun updateStatus(newStatus: String)
        pub fun updateDescription(newDescription: String)
    }

    // Test resource
    pub resource Test: ITest {
        pub let id: UInt64
        pub var status: String
        pub var description: String

        init(id: UInt64, description: String) {
            self.id = id
            self.status = "Not Started"
            self.description = description
        }

        pub fun updateStatus(newStatus: String) {
            pre {
                newStatus != "": "New status cannot be empty"
            }
            self.status = newStatus
            emit TestUpdated(testId: self.id, newStatus: newStatus)
        }

        pub fun updateDescription(newDescription: String) {
            pre {
                newDescription != "": "New description cannot be empty"
            }
            self.description = newDescription
        }
    }

    // Collection resource interface
    pub resource interface ITestCollection {
        pub fun createTest(description: String)
        pub fun getTest(id: UInt64): Test?
        pub fun updateTestStatus(id: UInt64, newStatus: String)
        pub fun deleteTest(id: UInt64)
    }

    // TestCollection resource
    pub resource TestCollection: ITestCollection {
        pub var tests: @{UInt64: Test}

        init() {
            self.tests <- {}
        }

        pub fun createTest(description: String) {
            let newId = UInt64(self.tests.length)
            let newTest <- create Test(id: newId, description: description)
            self.tests[newId] <-! newTest
            emit TestCreated(testId: newId)
        }

        pub fun getTest(id: UInt64): Test? {
            return self.tests[id]
        }

        pub fun updateTestStatus(id: UInt64, newStatus: String) {
            if let test = self.tests[id] {
                test.updateStatus(newStatus: newStatus)
            } else {
                panic("Test not found")
            }
        }

        pub fun deleteTest(id: UInt64) {
            if let test <- self.tests.remove(key: id) {
                destroy test
                emit TestDeleted(testId: id)
            } else {
                panic("Test not found")
            }
        }

        destroy() {
            destroy self.tests
        }
    }

    // Public functions
    pub fun createTestCollection(): @TestCollection {
        return <- create TestCollection()
    }

    // Example transaction to create a new TestCollection
    //
    // transaction {
    //     prepare(signer: auth(Storage) &Account) {
    //         let collection <- NewTest.createTestCollection()
    //         signer.save(<-collection, to: /storage/TestCollection)
    //     }
    // }

    // Example transaction to create a new Test
    //
    // transaction {
    //     prepare(signer: auth(Storage) &Account) {
    //         let collection = signer.borrow<&NewTest.TestCollection>(from: /storage/TestCollection)
    //             ?? panic("Could not borrow reference to TestCollection")
    //         collection.createTest(description: "New Test Description")
    //     }
    // }

    // Example script to read a Test
    //
    // pub fun main(account: Address): String? {
    //     let collection = getAccount(account)
    //         .getCapability(/public/TestCollection)
    //         .borrow<&NewTest.TestCollection>()
    //         ?? panic("Could not borrow reference to TestCollection")
    //     let test = collection.getTest(id: 0)
    //     return test?.description
    // }
}
```