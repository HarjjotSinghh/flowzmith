access(all) contract APITestToken {
    access(all) var totalSupply: UFix64
    
    init() {
        self.totalSupply = 1000000.0
    }
    
    access(all) fun getTotalSupply(): UFix64 {
        return self.totalSupply
    }
}