# POSIX terminal colors / byte chaining; you may need something different
# on an NT / Windows system
GREEN = '\033[92m'
YELLOW = '\033[33m'
END_COLOR = '\033[0m'

CORRECT_WORD = 'YESSIR'
CORRECT_LENGTH = len(CORRECT_WORD)

guesses_allowed = 5
guess_count = 0

while True:
    count_correct = 0
    guess = input("Guess the word: ").lower()

    if len(guess) > CORRECT_LENGTH:
        print(f"Guess is too long! Try again. The correct word is {CORRECT_LENGTH} long. ( This did not count against you. )")
        continue
    if len(guess) < CORRECT_LENGTH:
        print(f"Guess not long enough! Try again. The correct word is {CORRECT_LENGTH} long. ( This did not count against you. )")
        continue
    # This checks if all of the letters in the guess are in the alphabet.
    # If not, then we'll yell at our player.
    if guess.isalpha():
        # We enumerate so we can do some checking.
        index: int
        letter: str
        for index, letter in enumerate(guess):
            # If the letter in our guess is in the correct word,
            # We should _at least_ print it in yellow.
            if letter in CORRECT_WORD.lower():
                # Additionally:
                # If the letter in our guess matches the letter in
                # the same position in the correct word, we should print
                # the letter in green.
                if letter == CORRECT_WORD.lower()[index]:
                    count_correct += 1
                    # Printing with the keyword argument 'end' allows us to
                    # control what happens at the end of the print statement.
                    # In this instance, we prevent adding a newline to the end
                    # of the character, because we are trying to print all of the
                    # characters on one line.
                    print(f'{GREEN}{letter.upper()}{END_COLOR}', end='')
                else:
                    print(f'{YELLOW}{letter.upper()}{END_COLOR}', end='')
            # If the letter isn't in the correct word at all, just print it
            # normally without any color modifiers.
            else:
                print(letter, end='')
        print()
        # If we've guessed correctly the exact number of letters
        # that are in the correct string, it follows that we've
        # guessed the correct letters all the way through.
        # Then, the game is done, and we can exit.
        if count_correct == CORRECT_LENGTH:
            print("YOU DID IT")
            break
        # Here, we haven't guessed all correct letters. Compute
        # how many guesses we've made...
        guess_count += 1
        # ... and if we're out of guesses, yell at the player, and
        # then leave.
        if guess_count == guesses_allowed:
            print("YOU FAILED")
            break
    else:
        print("Only letters allowed. ( This did not count against you. )")
        continue

