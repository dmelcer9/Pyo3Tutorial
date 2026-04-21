#include <stdlib.h>
#include <stdio.h>

struct S {
    int a;
    float b;
};

struct Container {
    struct S* s;
};

struct S* also_okay() {
    struct S* s = malloc(sizeof(struct S));
    s->a = 1;
    s->b = 3.0;
    return s;
}

void foo(struct S* s){
  printf("%d\n",s -> a);
  free(s);
}

int main() {
    struct Container c;
    struct S* s = also_okay();
    c.s = s;
    foo(s);
    foo(c.s);
}