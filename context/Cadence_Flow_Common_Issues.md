(env) ~/smart-contract-llm [0] $ python cli.py flow-generate-deploy --requirements "Create a simple NFT contract with minting functionality" --network testnet
╭───────────────────────────────────────────────────────────────────────────────────────╮
│  ███████╗ ██╗       ██████╗  ██╗    ██╗ ███████╗ ███╗   ███╗ ██╗ ████████╗ ██╗  ██╗   │
│  ██╔════╝ ██║      ██╔═══██╗ ██║    ██║ ╚══███╔╝ ████╗ ████║ ██║ ╚══██╔══╝ ██║  ██║   │
│  █████╗   ██║      ██║   ██║ ██║ █╗ ██║   ███╔╝  ██╔████╔██║ ██║    ██║    ███████║   │
│  ██╔══╝   ██║      ██║   ██║ ██║███╗██║  ███╔╝   ██║╚██╔╝██║ ██║    ██║    ██╔══██║   │
│  ██║      ███████╗ ╚██████╔╝ ╚███╔███╔╝ ███████╗ ██║ ╚═╝ ██║ ██║    ██║    ██║  ██║   │
│  ╚═╝      ╚══════╝  ╚═════╝   ╚══╝╚══╝  ╚══════╝ ╚═╝     ╚═╝ ╚═╝    ╚═╝    ╚═╝  ╚═╝   │
╰───────────────────────────────────────────────────────────────────────────────────────╯
╭─────────────────────────────────────── Welcome ───────────────────────────────────────╮
│ ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓ │
│ ┃                                 🚀 Flowzmith CLI                                  ┃ │
│ ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛ │
│                                                                                       │
│ Welcome to the Flowzmith command-line interface!                                      │
│                                                                                       │
│ This tool provides step-by-step guided workflows for:                                 │
│                                                                                       │
│ • Smart contract submission and generation                                            │
│                                                                                       │
│ • Contract deployment to Flow blockchain                                              │
│                                                                                       │
│ • Documentation search and management                                                 │
│                                                                                       │
│ • Real-time progress monitoring                                                       │
│                                                                                       │
│ Let's get started building your next smart contract!                                  │
╰───────────────────────────────────────────────────────────────────────────────────────╯
[2025-09-28 00:26:27,327] INFO src.cli.api_client: APIClient session created (base_url=http://localhost:8000, ws_url=ws://localhost:8000/ws)
[2025-09-28 00:26:27,327] INFO src.cli.flow_manager: FlowProjectManager initialized with base_dir=/Users/harjjotsinghh/Desktop/Main/D Drive/Projects/smart-contract-llm/flow_projects
[2025-09-28 00:26:27,327] INFO src.cli.deployment_service: ContractDeploymentService initialized
Generating and deploying contract: Contract_20250928_002627
Requirements: Create a simple NFT contract with minting functionality
[2025-09-28 00:26:27,328] INFO src.cli.api_client: Generating contract with context: requirements_preview=Create a simple NFT contract with minting functionality, has_context=False
[2025-09-28 00:26:27,335] INFO src.cli.api_client: HTTP POST http://localhost:8000/api/v1/contracts/generate-with-context json_keys=['requirements', 'context_dir', 'network'] has_data=False headers=None
✅ Contract generated successfully!
Submission ID: ec1eec79-3b8e-4999-970e-7b823c3bc795
Validation Status: VALID
[2025-09-28 00:27:14,706] INFO src.cli.deployment_service: Starting automatic deployment: contract=Contract_20250928_002627, project_id=contract_20250928_002714_f0e5bb03, network=testnet
[2025-09-28 00:27:14,925] INFO src.cli.flow_manager: Flow CLI version check: Version: v2.7.3
[2025-09-28 00:27:14,926] INFO src.cli.flow_manager: Creating Flow project: project_id=contract_20250928_002714_f0e5bb03, contract=Contract_20250928_002627, network=testnet
[2025-09-28 00:27:20,753] INFO src.cli.flow_manager: Flow init completed for project contract_20250928_002714_f0e5bb03
[2025-09-28 00:27:26,316] INFO src.cli.flow_manager: Generated keys for project, private_key length: 142
[2025-09-28 00:27:26,317] INFO src.cli.flow_manager: Updated flow.json with proper keys for network: testnet
[2025-09-28 00:27:26,318] INFO src.cli.flow_manager: Contract file written: /Users/harjjotsinghh/Desktop/Main/D Drive/Projects/smart-contract-llm/flow_projects/contract_20250928_002714_f0e5bb03/contracts/Contract_20250928_002627.cdc
[2025-09-28 00:27:26,318] INFO src.cli.flow_manager: Updated flow.json for contract Contract_20250928_002627 on network testnet using account testnet-account
[2025-09-28 00:27:26,318] INFO src.cli.flow_manager: Created README for project contract_20250928_002714_f0e5bb03
[2025-09-28 00:27:26,318] INFO src.cli.flow_manager: Flow project created successfully: contract_20250928_002714_f0e5bb03
[2025-09-28 00:27:26,318] INFO src.cli.flow_manager: Deploying contract: project_id=contract_20250928_002714_f0e5bb03, network=testnet, account=emulator-account
[2025-09-28 00:27:36,765] ERROR src.cli.flow_manager: Deployment failed for contract_20250928_002714_f0e5bb03: ❌ Command Error: failed deploying all contracts

[2025-09-28 00:27:36,765] ERROR src.cli.deployment_service: Deployment failed for contract_20250928_002714_f0e5bb03: ❌ Command Error: failed deploying all contracts

❌ Deployment failed: None
Status: deployment_failed
[2025-09-28 00:27:36,766] INFO src.cli.api_client: APIClient shutting down; closing websocket=False, session=True

(TraeAI-9) ~/Desktop/Main/D Drive/Projects/smart-contract-llm [0] $ ls -lt flow_projects/ | head -3
total 0
drwxr-xr-x@ 10 harjjotsinghh  staff  320 Sep 28 00:27 contract_20250928_002714_f0e5bb03
drwxr-xr-x@  6 harjjotsinghh  staff  192 Sep 28 00:27 ec1eec79-3b8e-4999-970e-7b823c3bc795

(TraeAI-9) ~/Desktop/Main/D Drive/Projects/smart-contract-llm [0] $ cat "flow_projects/contract_20250928_002714_f0e5bb03/contracts/Contract_20250928_002627.cdc"
access(all) contract SimpleNFT: NonFungibleToken {

    access(all) event ContractInitialized()
    access(all) event NFTMinted(id: UInt64, metadata: {String: String})

    access(all) resource interface CollectionPublic {
        access(NonFungibleToken.Withdraw)
        fun deposit(token: @NonFungibleToken.NFT)
        access(NonFungibleToken.CollectionPublic)
        fun getIDs(): [UInt64]
        access(NonFungibleToken.CollectionPublic)
        fun borrowNFT(id: UInt64): &NonFungibleToken.NFT
    }

    access(all) resource Collection: CollectionPublic, NonFungibleToken.Provider {
        access(NonFungibleToken.Withdraw)
        fun withdraw(withdrawID: UInt64): @NonFungibleToken.NFT {
            pre {
                ownedNFTs[withdrawID] != nil: "NFT not found in collection"
            }
            let token <- ownedNFTs.remove(key: withdrawID)!
            emit Withdraw(id: token.id, withdrawer: <-getAccount(self.owner?.address))
            return <-token
        }

        access(all) fun deposit(token: @NonFungibleToken.NFT) {
            let tokenID = token.id
            let oldToken <- ownedNFTs[tokenID] <- token
            destroy oldToken
            emit Deposit(id: tokenID, to: <-getAccount(self.owner?.address))
        }

        access(NonFungibleToken.CollectionPublic)
        fun getIDs(): [UInt64] {
            return ownedNFTs.keys
        }

        access(NonFungibleToken.CollectionPublic)
        fun borrowNFT(id: UInt64): &NonFungibleToken.NFT {
            pre {
                ownedNFTs[id] != nil: "NFT not found in collection"
            }
            return (&ownedNFTs[id] as &NonFungibleToken.NFT?)!
        }

        access(self) let ownedNFTs: @{UInt64: NonFungibleToken.NFT}

        init() {
            self.ownedNFTs <- {}
        }
    }

    access(all) resource NFT: NonFungibleToken.NFT, MetadataViews.Resolver {
        access(all) let id: UInt64
        access(all) let metadata: {String: String}

        init(id: UInt64, metadata: {String: String}) {
            self.id = id
            self.metadata = metadata
        }

        access(all) fun getViews(): [Type] {
            return [
                Type<MetadataViews.Display>()
            ]
        }

        access(all) fun resolveView(_ view: Type): AnyStruct? {
            switch view {
                case Type<MetadataViews.Display>():
                    return MetadataViews.Display(
                        name: self.metadata["name"] ?? "",
                        description: self.metadata["description"] ?? "",
                        thumbnail: MetadataViews.HTTPFile(
                            url: self.metadata["thumbnail"] ?? ""
                        )
                    )
            }
            return nil
        }
    }

    access(all) resource NFTMinter {
        access(all) fun mintNFT(
            recipient: &{CollectionPublic},
            metadata: {String: String}
        ): UInt64 {
            let newNFT <- create NFT(
                id: SimpleNFT.totalSupply,
                metadata: metadata
            )
            let mintedID = newNFT.id
            recipient.deposit(token: <-newNFT)
            SimpleNFT.totalSupply = SimpleNFT.totalSupply + 1
            emit NFTMinted(id: mintedID, metadata: metadata)
            return mintedID
        }
    }

    access(all) let totalSupply: UInt64

    init() {
        self.totalSupply = 0
        emit ContractInitialized()
        let minter <- create NFTMinter()
        let collection <- create Collection()
        self.account.storage.save(<-minter, to: /storage/NFTMinter)
        self.account.storage.save(<-collection, to: /storage/NFTCollection)
        self.account.capabilities.publish(
            self.account.capabilities.storage.issue<&{CollectionPublic}>(/storage/NFTCollection),
            at: /public/NFTCollection
        )
    }
}

// Example transaction to mint an NFT
// transaction {
//     let recipient: &{SimpleNFT.CollectionPublic}
//     let minter: &SimpleNFT.NFTMinter

//     prepare(signer: AuthAccount) {
//         self.recipient = signer.capabilities.borrow<&{SimpleNFT.CollectionPublic}>(/public/NFTCollection)
//             ?? panic("Could not borrow reference to recipient's collection")
//         self.minter = signer.borrow<&SimpleNFT.NFTMinter>(from: /storage/NFTMinter)
//             ?? panic("Could not borrow reference to minter")
//     }

//     execute {
//         let metadata: {String: String} = {
//             "name": "Example NFT",
//             "description": "This is an example NFT",
//             "thumbnail": "https://example.com/thumbnail.jpg"
//         }
//         let newNFTID = self.minter.mintNFT(recipient: self.recipient, metadata: metadata)
//         log("Minted NFT with ID: ".concat(newNFTID.toString()))
//     }
// }

// Example script to get NFT IDs
// pub fun main(address: Address): [UInt64] {
//     let collection = getAccount(address)
//         .capabilities.borrow<&{SimpleNFT.CollectionPublic}>(/public/NFTCollection)
//         ?? panic("Could not borrow reference to collection")
//     return collection.getIDs()
// }%                                                                                    

(TraeAI-9) ~/Desktop/Main/D Drive/Projects/smart-contract-llm [0] $ grep -A 20 "resource NFTMinter" "flow_projects/contract_20250928_002714_f0e5bb03/contracts/Contract_20250928_002627.cdc"
    access(all) resource NFTMinter {
        access(all) fun mintNFT(
            recipient: &{CollectionPublic},
            metadata: {String: String}
        ): UInt64 {
            let newNFT <- create NFT(
                id: SimpleNFT.totalSupply,
                metadata: metadata
            )
            let mintedID = newNFT.id
            recipient.deposit(token: <-newNFT)
            SimpleNFT.totalSupply = SimpleNFT.totalSupply + 1
            emit NFTMinted(id: mintedID, metadata: metadata)
            return mintedID
        }
    }

    access(all) let totalSupply: UInt64

    init() {
        self.totalSupply = 0

(TraeAI-9) ~/Desktop/Main/D Drive/Projects/smart-contract-llm [0] $ cd "flow_projects/contract_20250928_002714_f0e5bb03" && flow project deploy --network testnet

Deploying 1 contracts for accounts: testnet-account

❌ Failed to deploy contract Contract_20250928_002627: failed to deploy contract Contract_20250928_002627: [Error Code: 1101] error caused by: 1 error occurred:
        * transaction execute failed: [Error Code: 1101] cadence runtime error: Execution failed:
error: cannot deploy invalid contract
 --> d6b6b8dc5711fcf44579f70e666ec1b2f17717cf338b30644f84adfb367cdc22:4:3
  |
4 |                     signer.contracts.add(name: name, code: code.utf8 )
  |                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

error: cannot find type in this scope: `NonFungibleToken`
 --> ea0b8be271e5a26b.SimpleNFT:1:32
  |
1 | access(all) contract SimpleNFT: NonFungibleToken {
  |                                 ^^^^^^^^^^^^^^^^ not found in this scope; check for typos or declare it

  See documentation at: https://cadence-lang.org/docs/language/constants-and-variables

error: cannot find type in this scope: `NonFungibleToken`
  --> ea0b8be271e5a26b.SimpleNFT:15:55
   |
15 |     access(all) resource Collection: CollectionPublic, NonFungibleToken.Provider {
   |                                                        ^^^^^^^^^^^^^^^^ not found in this scope; check for typos or declare it

  See documentation at: https://cadence-lang.org/docs/language/constants-and-variables

error: cannot find type in this scope: `NonFungibleToken`
  --> ea0b8be271e5a26b.SimpleNFT:53:30
   |
53 |     access(all) resource NFT: NonFungibleToken.NFT, MetadataViews.Resolver {
   |                               ^^^^^^^^^^^^^^^^ not found in this scope; check for typos or declare it

  See documentation at: https://cadence-lang.org/docs/language/constants-and-variables

error: cannot find type in this scope: `MetadataViews`
  --> ea0b8be271e5a26b.SimpleNFT:53:52
   |
53 |     access(all) resource NFT: NonFungibleToken.NFT, MetadataViews.Resolver {
   |                                                     ^^^^^^^^^^^^^ not found in this scope; check for typos or declare it

  See documentation at: https://cadence-lang.org/docs/language/constants-and-variables

error: cannot find type in this scope: `NonFungibleToken`
 --> ea0b8be271e5a26b.SimpleNFT:7:15
  |
7 |         access(NonFungibleToken.Withdraw)
  |                ^^^^^^^^^^^^^^^^ not found in this scope; check for typos or declare it

  See documentation at: https://cadence-lang.org/docs/language/constants-and-variables

error: cannot find type in this scope: `NonFungibleToken`
 --> ea0b8be271e5a26b.SimpleNFT:8:28
  |
8 |         fun deposit(token: @NonFungibleToken.NFT)
  |                             ^^^^^^^^^^^^^^^^ not found in this scope; check for typos or declare it

  See documentation at: https://cadence-lang.org/docs/language/constants-and-variables

error: cannot find type in this scope: `NonFungibleToken`
 --> ea0b8be271e5a26b.SimpleNFT:9:15
  |
9 |         access(NonFungibleToken.CollectionPublic)
  |                ^^^^^^^^^^^^^^^^ not found in this scope; check for typos or declare it

  See documentation at: https://cadence-lang.org/docs/language/constants-and-variables

error: cannot find type in this scope: `NonFungibleToken`
  --> ea0b8be271e5a26b.SimpleNFT:11:15
   |
11 |         access(NonFungibleToken.CollectionPublic)
   |                ^^^^^^^^^^^^^^^^ not found in this scope; check for typos or declare it

  See documentation at: https://cadence-lang.org/docs/language/constants-and-variables

error: cannot find type in this scope: `NonFungibleToken`
  --> ea0b8be271e5a26b.SimpleNFT:12:36
   |
12 |         fun borrowNFT(id: UInt64): &NonFungibleToken.NFT
   |                                     ^^^^^^^^^^^^^^^^ not found in this scope; check for typos or declare it

  See documentation at: https://cadence-lang.org/docs/language/constants-and-variables

error: cannot find type in this scope: `NonFungibleToken`
  --> ea0b8be271e5a26b.SimpleNFT:46:46
   |
46 |         access(self) let ownedNFTs: @{UInt64: NonFungibleToken.NFT}
   |                                               ^^^^^^^^^^^^^^^^ not found in this scope; check for typos or declare it

  See documentation at: https://cadence-lang.org/docs/language/constants-and-variables

error: cannot find type in this scope: `NonFungibleToken`
  --> ea0b8be271e5a26b.SimpleNFT:16:15
   |
16 |         access(NonFungibleToken.Withdraw)
   |                ^^^^^^^^^^^^^^^^ not found in this scope; check for typos or declare it

  See documentation at: https://cadence-lang.org/docs/language/constants-and-variables

error: cannot find type in this scope: `NonFungibleToken`
  --> ea0b8be271e5a26b.SimpleNFT:17:43
   |
17 |         fun withdraw(withdrawID: UInt64): @NonFungibleToken.NFT {
   |                                            ^^^^^^^^^^^^^^^^ not found in this scope; check for typos or declare it

  See documentation at: https://cadence-lang.org/docs/language/constants-and-variables

error: cannot find type in this scope: `NonFungibleToken`
  --> ea0b8be271e5a26b.SimpleNFT:26:40
   |
26 |         access(all) fun deposit(token: @NonFungibleToken.NFT) {
   |                                         ^^^^^^^^^^^^^^^^ not found in this scope; check for typos or declare it

  See documentation at: https://cadence-lang.org/docs/language/constants-and-variables

error: cannot find type in this scope: `NonFungibleToken`
  --> ea0b8be271e5a26b.SimpleNFT:33:15
   |
33 |         access(NonFungibleToken.CollectionPublic)
   |                ^^^^^^^^^^^^^^^^ not found in this scope; check for typos or declare it

  See documentation at: https://cadence-lang.org/docs/language/constants-and-variables

error: cannot find type in this scope: `NonFungibleToken`
  --> ea0b8be271e5a26b.SimpleNFT:38:15
   |
38 |         access(NonFungibleToken.CollectionPublic)
   |                ^^^^^^^^^^^^^^^^ not found in this scope; check for typos or declare it

  See documentation at: https://cadence-lang.org/docs/language/constants-and-variables

error: cannot find type in this scope: `NonFungibleToken`
  --> ea0b8be271e5a26b.SimpleNFT:39:36
   |
39 |         fun borrowNFT(id: UInt64): &NonFungibleToken.NFT {
   |                                     ^^^^^^^^^^^^^^^^ not found in this scope; check for typos or declare it

  See documentation at: https://cadence-lang.org/docs/language/constants-and-variables

error: cannot find variable in this scope: `ownedNFTs`
  --> ea0b8be271e5a26b.SimpleNFT:19:16
   |
19 |                 ownedNFTs[withdrawID] != nil: "NFT not found in collection"
   |                 ^^^^^^^^^ not found in this scope; check for typos or declare it

  See documentation at: https://cadence-lang.org/docs/language/constants-and-variables

error: cannot find variable in this scope: `ownedNFTs`
  --> ea0b8be271e5a26b.SimpleNFT:21:25
   |
21 |             let token <- ownedNFTs.remove(key: withdrawID)!
   |                          ^^^^^^^^^ not found in this scope; check for typos or declare it

  See documentation at: https://cadence-lang.org/docs/language/constants-and-variables

error: cannot find variable in this scope: `Withdraw`
  --> ea0b8be271e5a26b.SimpleNFT:22:17
   |
22 |             emit Withdraw(id: token.id, withdrawer: <-getAccount(self.owner?.address))
   |                  ^^^^^^^^ not found in this scope; check for typos or declare it

  See documentation at: https://cadence-lang.org/docs/language/constants-and-variables

error: mismatched types
  --> ea0b8be271e5a26b.SimpleNFT:22:65
   |
22 |             emit Withdraw(id: token.id, withdrawer: <-getAccount(self.owner?.address))
   |                                                                  ^^^^^^^^^^^^^^^^^^^ expected `Address`, got `Address?`; check the expression's type or convert it to the expected type

  See documentation at: https://cadence-lang.org/docs/language/values-and-types

error: invalid move operation (`<-`) for non-resource
  --> ea0b8be271e5a26b.SimpleNFT:22:52
   |
22 |             emit Withdraw(id: token.id, withdrawer: <-getAccount(self.owner?.address))
   |                                                     ^^ the move operator (`<-`) can only be used on resources; remove the `<-` operator for the non-resource

  See documentation at: https://cadence-lang.org/docs/language/operators/assign-move-force-swap

error: cannot find variable in this scope: `ownedNFTs`
  --> ea0b8be271e5a26b.SimpleNFT:28:28
   |
28 |             let oldToken <- ownedNFTs[tokenID] <- token
   |                             ^^^^^^^^^ not found in this scope; check for typos or declare it

  See documentation at: https://cadence-lang.org/docs/language/constants-and-variables

error: cannot find variable in this scope: `ownedNFTs`
  --> ea0b8be271e5a26b.SimpleNFT:28:28
   |
28 |             let oldToken <- ownedNFTs[tokenID] <- token
   |                             ^^^^^^^^^ not found in this scope; check for typos or declare it

  See documentation at: https://cadence-lang.org/docs/language/constants-and-variables

error: cannot find variable in this scope: `ownedNFTs`
  --> ea0b8be271e5a26b.SimpleNFT:28:28
   |
28 |             let oldToken <- ownedNFTs[tokenID] <- token
   |                             ^^^^^^^^^ not found in this scope; check for typos or declare it

  See documentation at: https://cadence-lang.org/docs/language/constants-and-variables

error: cannot find variable in this scope: `Deposit`
  --> ea0b8be271e5a26b.SimpleNFT:30:17
   |
30 |             emit Deposit(id: tokenID, to: <-getAccount(self.owner?.address))
   |                  ^^^^^^^ not found in this scope; check for typos or declare it

  See documentation at: https://cadence-lang.org/docs/language/constants-and-variables

error: mismatched types
  --> ea0b8be271e5a26b.SimpleNFT:30:55
   |
30 |             emit Deposit(id: tokenID, to: <-getAccount(self.owner?.address))
   |                                                        ^^^^^^^^^^^^^^^^^^^ expected `Address`, got `Address?`; check the expression's type or convert it to the expected type

  See documentation at: https://cadence-lang.org/docs/language/values-and-types

error: invalid move operation (`<-`) for non-resource
  --> ea0b8be271e5a26b.SimpleNFT:30:42
   |
30 |             emit Deposit(id: tokenID, to: <-getAccount(self.owner?.address))
   |                                           ^^ the move operator (`<-`) can only be used on resources; remove the `<-` operator for the non-resource

  See documentation at: https://cadence-lang.org/docs/language/operators/assign-move-force-swap

error: cannot find variable in this scope: `ownedNFTs`
  --> ea0b8be271e5a26b.SimpleNFT:35:19
   |
35 |             return ownedNFTs.keys
   |                    ^^^^^^^^^ not found in this scope; check for typos or declare it

  See documentation at: https://cadence-lang.org/docs/language/constants-and-variables

error: cannot find variable in this scope: `ownedNFTs`
  --> ea0b8be271e5a26b.SimpleNFT:41:16
   |
41 |                 ownedNFTs[id] != nil: "NFT not found in collection"
   |                 ^^^^^^^^^ not found in this scope; check for typos or declare it

  See documentation at: https://cadence-lang.org/docs/language/constants-and-variables

error: cannot find type in this scope: `NonFungibleToken`
  --> ea0b8be271e5a26b.SimpleNFT:43:39
   |
43 |             return (&ownedNFTs[id] as &NonFungibleToken.NFT?)!
   |                                        ^^^^^^^^^^^^^^^^ not found in this scope; check for typos or declare it

  See documentation at: https://cadence-lang.org/docs/language/constants-and-variables

error: cannot find variable in this scope: `ownedNFTs`
  --> ea0b8be271e5a26b.SimpleNFT:43:21
   |
43 |             return (&ownedNFTs[id] as &NonFungibleToken.NFT?)!
   |                      ^^^^^^^^^ not found in this scope; check for typos or declare it

  See documentation at: https://cadence-lang.org/docs/language/constants-and-variables

error: resource `SimpleNFT.Collection` does not conform to resource interface `SimpleNFT.CollectionPublic`
  --> ea0b8be271e5a26b.SimpleNFT:15:25
   |
15 |     access(all) resource Collection: CollectionPublic, NonFungibleToken.Provider {
   |                          ^
  ... 
   |
26 |         access(all) fun deposit(token: @NonFungibleToken.NFT) {
   |                         ------- conformance mismatch here
  ... 
   |
34 |         fun getIDs(): [UInt64] {
   |             ------ conformance mismatch here
  ... 
   |
39 |         fun borrowNFT(id: UInt64): &NonFungibleToken.NFT {
   |             --------- conformance mismatch here

  See documentation at: https://cadence-lang.org/docs/language/interfaces

error: cannot find type in this scope: `MetadataViews`
  --> ea0b8be271e5a26b.SimpleNFT:64:21
   |
64 |                 Type<MetadataViews.Display>()
   |                      ^^^^^^^^^^^^^ not found in this scope; check for typos or declare it

  See documentation at: https://cadence-lang.org/docs/language/constants-and-variables

error: cannot infer type argument for type parameter `T`
  --> ea0b8be271e5a26b.SimpleNFT:64:16
   |
64 |                 Type<MetadataViews.Display>()
   |                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ provide an explicit type argument for type parameter `T` to resolve the ambiguity

  See documentation at: https://cadence-lang.org/docs/language/values-and-types

error: cannot find type in this scope: `MetadataViews`
  --> ea0b8be271e5a26b.SimpleNFT:70:26
   |
70 |                 case Type<MetadataViews.Display>():
   |                           ^^^^^^^^^^^^^ not found in this scope; check for typos or declare it

  See documentation at: https://cadence-lang.org/docs/language/constants-and-variables

error: cannot infer type argument for type parameter `T`
  --> ea0b8be271e5a26b.SimpleNFT:70:21
   |
70 |                 case Type<MetadataViews.Display>():
   |                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ provide an explicit type argument for type parameter `T` to resolve the ambiguity

  See documentation at: https://cadence-lang.org/docs/language/values-and-types

error: cannot find variable in this scope: `MetadataViews`
  --> ea0b8be271e5a26b.SimpleNFT:71:27
   |
71 |                     return MetadataViews.Display(
   |                            ^^^^^^^^^^^^^ not found in this scope; check for typos or declare it

  See documentation at: https://cadence-lang.org/docs/language/constants-and-variables

error: cannot find variable in this scope: `MetadataViews`
  --> ea0b8be271e5a26b.SimpleNFT:74:35
   |
74 |                         thumbnail: MetadataViews.HTTPFile(
   |                                    ^^^^^^^^^^^^^ not found in this scope; check for typos or declare it

  See documentation at: https://cadence-lang.org/docs/language/constants-and-variables

error: access denied: cannot access `deposit` because function requires `NonFungibleToken` authorization, but reference is unauthorized
  --> ea0b8be271e5a26b.SimpleNFT:93:12
   |
93 |             recipient.deposit(token: <-newNFT)
   |             ^^^^^^^^^^^^^^^^^ ensure your reference has the required authorization by using the appropriate access modifier or entitlement

  See documentation at: https://cadence-lang.org/docs/language/access-control

error: cannot assign to constant member: `totalSupply`
  --> ea0b8be271e5a26b.SimpleNFT:94:22
   |
94 |             SimpleNFT.totalSupply = SimpleNFT.totalSupply + 1
   |                       ^^^^^^^^^^^ constant members cannot be reassigned after initialization; consider using a variable field (`var`) instead

  See documentation at: https://cadence-lang.org/docs/language/constants-and-variables

Was this error unhelpful?
Consider suggesting an improvement here: https://github.com/onflow/cadence/issues.



❌ Command Error: failed deploying all contracts
