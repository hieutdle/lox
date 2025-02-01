# Plox

A tree-walk interpreter written in Python for the Lox programming language, a language created for the book [Crafting Interpreters](http://craftinginterpreters.com/).

## Features:

### ✅ Lexer

### ✅ Parser

### ✅ Block/Scope

```lox
var x = "global x";
var y = "global y";
var z = "global z";
{
  var x = "outer x";
  var y = "outer y";
  {
    var x = "inner x";
    print x; // expect: inner x
    print y; // expect: outer y
    print z; // expect: global z
  }
  print x; // expect: outer x
  print y; // expect: outer y
  print z; // expect: global z
}
print x; // expect: global x
print y; // expect: global y
print z; // expect: global z
```

### ✅ Closure

```lox
var x = "global";
{
  fun showX() {
    print x;
  }
  showX();
  var x = "block";
  showX();
}
// expect: global
// expect: global
```

### ✅ Loop

```lox
var i = 2;
while (i < 12) {
  i = i + 2;
  if (i == 8) {
    break;
  }
}
print i; // expect: 8

var a = 1;
var temp;
for (var b = 2; a < 15000; b = temp + b) {
  temp = a;
  a = b;
  while (true) {
    break;
  }
}
print a; // expect: 10946
```

### ✅ Function

```lox
fun greet(first, last) {
  print "Hello, " + first + " " + last + "!";
}
greet("John", "Doe");
// expect: Hello, John Doe!

fun factorial(n) {
  if (n <= 1) return 1;
  return n * factorial(n - 1);
}
print factorial(5); // expect: 120

fun createCounter() {
  var count = 0;
  fun increment() {
    count = count + 1;
    print count;
  }
  return increment;
}

var counter = createCounter();
counter(); // expect: 1
counter(); // expect: 2
```

### ✅ Class

```lox
class Animal {
  speak() {
    print this.sound;
  }
}

var dog = Animal();
dog.sound = "Woof";

var cat = Animal();
cat.sound = "Meow";

cat.speak = dog.speak;
cat.speak();
```

### ✅ Inheritance

```lox
class Pastry {
  bake() {
    print "Bake until golden brown.";
  }
}

class Croissant < Pastry {
  bake() {
    super.bake();
    print "Add layers of butter and fold carefully.";
  }
}

Croissant().bake();
// expect: Bake until golden brown.
// expect: Add layers of butter and fold carefully.
```

---

[Crafting Interpreters](http://craftinginterpreters.com/)
