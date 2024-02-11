#include <stdio.h>

int main() {
    int x;
    char character;

    // Read the integer x from stdin
    printf("Enter an integer x: ");
    scanf("%d", &x);

    // Read the character from stdin
    printf("Enter a character: ");
    scanf(" %c", &character);

    // Print the character x amount of times to stdout
    printf("Printing the character '%c' %d times:\n", character, x);
    for (int i = 0; i < x; i++) {
        printf("%c", character);
    }
    printf("\n");

    return 0;
}
