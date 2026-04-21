struct S {
    a: i32,
    b: f32,
}

fn foo(s: &S) {
    println!("{}", s.a);
}

fn okay() -> S {
    S { a: 1, b: 3.0 }
}

fn also_okay() -> Box<S> {
    Box::new(S { a: 1, b: 3.0 })
}

fn bad() -> &S {
    &S { a: 1, b: 3.0 }
}