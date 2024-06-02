#include <stdio.h>

// Nested function declarations
void funcC(int c);
void funcB(int b);
void funcA(int a);

void funcC(int c) {
    int z = c * 3;
    printf("Inside funcC: z = %d\n", z);
}

void funcB(int b) {
    int y = b + 2;
    printf("Inside funcB: y = %d\n", y);
    funcC(y);
}

void funcA(int a) {
    int x = a - 1;
    printf("Inside funcA: x = %d\n", x);
    funcB(x);
}

int main() {
    int w = 5;
    printf("Inside main: w = %d\n", w);
    funcA(w);
    return 0;
}
