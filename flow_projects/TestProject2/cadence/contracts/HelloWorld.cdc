// HelloWorld.cdc
// A simple Hello World contract for Flow blockchain

access(all) contract HelloWorld {
    access(all) var greeting: String

    init() {
        self.greeting = "Hello, World!"
    }

    access(all) fun hello(): String {
        return self.greeting
    }

    access(all) fun changeGreeting(newGreeting: String) {
        self.greeting = newGreeting
    }
}