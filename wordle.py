#!/usr/bin/python3

from curses.ascii import isupper
import string
import random


def get_words(length: int) -> set:
    result =set()
    
    with open('/usr/share/dict/words', 'r') as f:
        for line in f:
            strip_line = line.strip()
            if len(strip_line) != length:
                continue

            if "'" in strip_line:
                continue

            if isupper(strip_line[0]):
                continue

            result.add(strip_line)
    return result

def filter_include_letters(word: string, include: set):
    if not len(include):
        return True
    if len(set(word).intersection(include)) > 0:
        return True
    return False


def filter_exclude_letters(word: string, exclude: set):
    if len(exclude) == 0:
        return True

    if len(set(word).intersection(exclude)) == 0:
        return True
    return False


def filter_known_letter_positions(word: string, letters: list):
    result = True
    for i in range(len(word)):
        if letters[i] != '' and letters[i] != word[i]:
            result = False
    return result


def filter_excluded_letter_positions(word: string, letters: list):
    result = True
    for i in range(len(word)):
        if word[i] in letters[i]:
            result = False
    return result

def get_letter_distribution(words: set):
    distribution = {}

    for word in words:
        sorted_word = ''.join(sorted(word))

        for letter in sorted_word:
            if letter in distribution:
                distribution[letter] = distribution[letter] + 1
            else:
                distribution[letter] = 1

    return distribution

def find_matching_words(words: set, include: set):
    result = set()
   
    if len(include):
        for word in words:
            if len(set(word).intersection(include)) == len(include):
                result.add(word)

    return result

def word_probability_weight(word: string, distribution: map):
    weight = 0
    for w in word:
        weight = weight + distribution[w]
    
    # Hack to favour words without repeat characters, so our initial guess
    # isn't a work like mummy for example, which would be useless.
    if len(set(word)) < len(word):
        weight = weight / 2

    return weight

def main():
    # This is the letters that are known to be in the right position.
    known_letters = ['', '', '', '', '']

    # This is the letters that are right, but in the incorrect position.
    excluded_letters = [
        set(), 
        set(), 
        set(), 
        set(), 
        set()
    ]

    # This is the letters that are known to not be in the word.
    bad_letters = set()

    # Read the words in from the dictionary
    words = get_words(len(known_letters))

    print('Use the following for each position in the word:')
    print('x = letter not in word')
    print('g = letter in right position')
    print('o = letter in wrong position')

    while(True):
        good_letters = set().union(*excluded_letters, [x for x in known_letters if x != ''])
        
        words = [word for word in words if filter_include_letters(word, good_letters) and
            filter_exclude_letters(word, bad_letters) and
            filter_known_letter_positions(word, known_letters) and
            filter_excluded_letter_positions(word, excluded_letters)]

        if len(words) == 0:
            print('No words left.')
            exit(-1)
        elif len(words) == 1:
            print('Only word left: ', words.pop())
            exit(0)

        print('Possible words left: ', len(words))

        dist = get_letter_distribution(words)
        sorted_dist = dict(sorted(dist.items(), key=lambda item: item[1], reverse=True))

        include = set(good_letters)
        exclude = set(bad_letters)

        possibles = set()
        for k,v in sorted_dist.items():
            include.add(k)
            possibles = possibles.union(find_matching_words(words, include))
            exclude = exclude.union(include.difference(good_letters))
            include = set(good_letters)

        weighted = [(w, word_probability_weight(w, dist)) for w in possibles]

        weighted = sorted(weighted, key=lambda word: word[1], reverse=True)

        weighted = weighted[:10]

        guess, _ = (weighted[0] if len(weighted) < 5 else random.choice(weighted))

        print('My guess: ' + guess)

        result = input('Result (x,g,o) ->')

        if len(result) != len(guess):
            error('Not enough letters.');

        for i, r in enumerate(result):
            if r == 'x':
                bad_letters.add(guess[i])
            elif r == 'g':
                known_letters[i] = guess[i]
            elif r == 'o':
                excluded_letters[i].add(guess[i])

   

if __name__ == "__main__":
    main()
