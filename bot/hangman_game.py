from random_word import RandomWords


def get_hangman_word():
    words = RandomWords()
    word = words.get_random_word()
    return word


def check_guess(word, guess):
    indices = [i for i, x in enumerate(word) if x == guess]
    if len(indices) == 0:
        return False
    else:
        return indices


def modify_places(places, indices, word):
    for i in indices:
        places = f'{places[:i]}{word[i]}{places[i+1:]}'
    return places
