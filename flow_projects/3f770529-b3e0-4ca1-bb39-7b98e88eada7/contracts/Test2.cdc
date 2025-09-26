```cadence
// Test2.cdc

// A simple DAO contract example on Cadence

pub contract Test2 {

    // Events
    pub event ProposalCreated(proposalID: UInt64)
    pub event VoteCast(proposalID: UInt64, voter: Address, vote: Bool)
    pub event ProposalExecuted(proposalID: UInt64)

    // Resource interface for Proposal
    pub resource interface IProposal {
        pub let id: UInt64
        pub let proposer: Address
        pub let description: String
        pub var votes: {Address: Bool}
        pub var executed: Bool

        pub fun castVote(voter: Address, vote: Bool)
        pub fun execute()
    }

    // Proposal resource
    pub resource Proposal: IProposal {
        pub let id: UInt64
        pub let proposer: Address
        pub let description: String
        pub var votes: {Address: Bool}
        pub var executed: Bool

        init(proposer: Address, description: String, id: UInt64) {
            self.id = id
            self.proposer = proposer
            self.description = description
            self.votes = {}
            self.executed = false
        }

        pub fun castVote(voter: Address, vote: Bool) {
            pre {
                !self.executed: "Proposal has already been executed"
                !self.votes.containsKey(voter): "Voter has already voted"
            }
            self.votes[voter] = vote
            emit VoteCast(self.id, voter, vote)
        }

        pub fun execute() {
            pre {
                !self.executed: "Proposal has already been executed"
            }
            let yesVotes = self.votes.values.filter { $0 }.length
            let noVotes = self.votes.values.filter { !$0 }.length
            if yesVotes > noVotes {
                self.executed = true
                emit ProposalExecuted(self.id)
            } else {
                panic("Not enough yes votes to execute proposal")
            }
        }
    }

    // DAO state
    pub var proposals: @{UInt64: Proposal}
    pub var nextProposalID: UInt64

    init() {
        self.proposals <- {}
        self.nextProposalID = 0
    }

    // Function to create a new proposal
    pub fun createProposal(proposer: Address, description: String) {
        let proposal <- create Proposal(proposer: proposer, description: description, id: self.nextProposalID)
        self.proposals[self.nextProposalID] <-! proposal
        self.nextProposalID = self.nextProposalID + 1
        emit ProposalCreated(self.nextProposalID - 1)
    }

    // Function to get a proposal
    pub fun getProposal(id: UInt64): &Proposal? {
        return &self.proposals[id] as &Proposal?
    }

    // Destroy unused proposals
    destroy() {
        destroy self.proposals
    }
}

// Example transaction to create a proposal
transaction(description: String) {
    prepare(signer: AuthAccount) {
        Test2.createProposal(proposer: signer.address, description: description)
    }
}

// Example transaction to cast a vote
transaction(proposalID: UInt64, vote: Bool) {
    prepare(signer: AuthAccount) {
        let proposal = Test2.getProposal(id: proposalID)
        if let proposal = proposal {
            proposal.castVote(voter: signer.address, vote: vote)
        } else {
            panic("Proposal not found")
        }
    }
}

// Example transaction to execute a proposal
transaction(proposalID: UInt64) {
    prepare(signer: AuthAccount) {
        let proposal = Test2.getProposal(id: proposalID)
        if let proposal = proposal {
            proposal.execute()
        } else {
            panic("Proposal not found")
        }
    }
}

// Example script to get a proposal
pub fun main(proposalID: UInt64): &Test2.Proposal? {
    return Test2.getProposal(id: proposalID)
}
```