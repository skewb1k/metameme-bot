import os
from random import randint, random, choice
from string import digits


path_to_file = 'data/words.txt'
RANDOM_LETTERS_CHANCE = 0.1
RANDOM_DIGITS_CHANCE = 0.1
ONE_WORD_CHANCE = 0.5
CAPS_CHANCE = 0.5
MIN_RANDOM_LETTERS_LEN = 4
MAX_RANDOM_LETTERS_LEN = 7
MIN_WORDS_COUHT = 1
MAX_WORDS_COUNT = 3
alphabet = 'абвгдежзийклмнопрстуфхцчшщъыьэюя'


# tricky way to get random string from line w/o loading full file
def get_random_line() -> str:
    file_size = os.path.getsize(path_to_file)
    with open(path_to_file, 'rb') as f:
        while True:
            pos = randint(0, file_size)
            if not pos:  # the first line is chosen
                return f.readline().decode()  # return str
            f.seek(pos)  # seek to random position
            f.readline()  # skip possibly incomplete line
            line = f.readline()  # read next (full) line
            if line:
                return line.decode().rstrip()


def get_random_phrase(
    size=0, allow_random_letters=True, allow_digits=True, allow_caps=True
) -> str:
    if size == 0:
        if random() <= ONE_WORD_CHANCE:
            word_count = 1
        else:
            word_count = randint(MIN_WORDS_COUHT, MAX_WORDS_COUNT)
    else:
        word_count = size

    words = []
    for _ in range(word_count):
        if allow_random_letters and random() <= RANDOM_LETTERS_CHANCE:
            word = ''.join(
                choice(alphabet)
                for _ in range(randint(MIN_RANDOM_LETTERS_LEN, MAX_RANDOM_LETTERS_LEN))
            )
        else:
            word = get_random_line()

        if allow_caps and random() <= CAPS_CHANCE:
            words.append(word.upper())
        else:
            words.append(word.lower())
    result = ' '.join(words)
    if allow_digits and random() <= RANDOM_DIGITS_CHANCE:
        result += ' ' + choice(digits)
    return result
