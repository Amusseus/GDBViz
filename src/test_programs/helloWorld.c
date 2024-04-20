#include <stdio.h>

// Function to print Hello World and the number of times it has been printed
void printHello(int count) {
    printf("Hello World num: %dn", count);
}

int main() {
    static int count = 1; // Static variable to keep track of the count

    // Print Hello World and the count 10 times
    printHello(count++);
    printHello(count++);
    printHello(count++);
    printHello(count++);
    printHello(count++);
    printHello(count++);
    printHello(count++);
    printHello(count++);
    printHello(count++);
    printHello(count++);

    return 0;
}

