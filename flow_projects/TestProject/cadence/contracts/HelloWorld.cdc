// HelloWorld.cdc
// A simple Hello World contract for Flow blockchain

pub contract HelloWorld {
    pub var greeting: String

    init() {
        self.greeting = "Hello, World!"
    }

    pub fun hello(): String {
        return self.greeting
    }

    pub fun changeGreeting(newGreeting: String) {
        self.greeting = newGreeting
    }
}