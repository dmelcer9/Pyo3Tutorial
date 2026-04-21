#include <stdlib.h>
#include <stdio.h>

struct S {
    int a;
    float b;
};


void foo(struct S* s){
  printf("%d\n",s -> a);
}

struct S okay() {
   struct S bar = (struct S){1, 3.0};
   foo(&bar);
   return bar;
}

struct S* also_okay() {
    struct S* s = malloc(sizeof(struct S));
    s->a = 1;
    s->b = 3.0;
    return s;
}

struct S* bad () {
   struct S foo = (struct S){1, 3.0};
   return &foo;
}

int main() {
}