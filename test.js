/**
 * 这是一个测试文件
 */
function greet(name) {
    console.log("Hello, " + name + "!");
    return "Greeting completed";
}

// 计算两个数的和
function add(a, b) {
    return a + b;
}

// 一个简单的类
class Person {
    constructor(name, age) {
        this.name = name;
        this.age = age;
    }
    
    sayHello() {
        console.log(`My name is ${this.name} and I am ${this.age} years old.`);
    }
    
    getDetails() {
        return {
            name: this.name,
            age: this.age,
            adult: this.age >= 18
        };
    }
}

// 导出模块
module.exports = {
    greet,
    add,
    Person
}; 