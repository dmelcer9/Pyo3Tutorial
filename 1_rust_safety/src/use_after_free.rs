struct S {
    a: i32,
    b: f32,
}

struct ContainerBorrowed<'a> {
    s: &'a S,
}

struct ContainerOwned {
    s: Box<S>,
}

fn foo(s: &S) {
    println!("{}", s.a);
}

fn foo_owned(s: Box<S>) {
    println!("{}", s.a);
}

fn also_okay() -> Box<S> {
    Box::new(S { a: 1, b: 3.0 })
}

pub fn main1() {
    let s = also_okay();

    foo_owned(s); // Okay in isolation

    let co = ContainerOwned { s }; // Error: s already moved
}

pub fn main2(){
    let s = also_okay();
    let co = ContainerOwned { s };
    foo(&co.s); // Okay
    foo_owned(co.s); // Also oaky

    foo(&co.s); // Error: co moved
}

pub fn main3(){
    let s = also_okay();
    let co = ContainerOwned {s};

    let cb = ContainerBorrowed {s: &co.s};
    foo(&cb.s);

    let s = co.s;
    foo(&s);
    foo(&cb.s); // Error: s moved
}