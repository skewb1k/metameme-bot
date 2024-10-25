import os
from random import randint, random, choice
from string import digits


class PhraseGenerator:
    alphabet = "абвгдежзийклмнопрстуфхцчшщъыьэюя"

    def __init__(
        self,
        words_file: str,
        random_letters_chance: float,
        random_digits_chance: float,
        single_word_chance: float,
        caps_chance: float,
        min_random_letters_len: int,
        max_random_letters_len: int,
        min_words_count: int,
        max_words_count: int,
    ):
        self.words_file = words_file
        self.random_letters_chance = random_letters_chance
        self.random_digits_chance = random_digits_chance
        self.single_word_chance = single_word_chance
        self.caps_chance = caps_chance
        self.min_random_letters_len = min_random_letters_len
        self.max_random_letters_len = max_random_letters_len
        self.min_words_count = min_words_count
        self.max_words_count = max_words_count

    # tricky way to get random string from line w/o loading full file
    def _get_random_line(self) -> str:
        file_size = os.path.getsize(self.words_file)
        with open(self.words_file, "rb") as f:
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
        self, size=0, allow_random_letters=True, allow_digits=True, allow_caps=True
    ) -> str:
        if size == 0:
            if random() <= self.single_word_chance:
                word_count = 1
            else:
                word_count = randint(self.min_words_count, self.max_words_count)
        else:
            word_count = size

        words = []
        for _ in range(word_count):
            if allow_random_letters and random() <= self.random_letters_chance:
                word = "".join(
                    choice(self.alphabet)
                    for _ in range(
                        randint(
                            self.min_random_letters_len, self.max_random_letters_len
                        )
                    )
                )
            else:
                word = self._get_random_line()

            if allow_caps and random() <= self.caps_chance:
                words.append(word.upper())
            else:
                words.append(word.lower())

        result = " ".join(words)
        if allow_digits and random() <= self.random_digits_chance:
            result += " " + choice(digits)

        return result
