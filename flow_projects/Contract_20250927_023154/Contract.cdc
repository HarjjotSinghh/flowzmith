
access(all) contract TestToken {
    access(all) var totalSupply: UFix64
    
    init() {
        self.totalSupply = 1000.0
    }
    
    access(all) fun getTotalSupply(): UFix64 {
        return self.totalSupply
    }
}
