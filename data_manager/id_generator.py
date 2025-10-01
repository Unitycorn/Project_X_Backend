import random

smallLetters = 'abcdefghijklmnopqrstuvwxyz'
bigLetters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
numerals = '0123456789'

charList = list(smallLetters) + list(bigLetters) + list(numerals)


def idGenerator(idLength):
    idResult = ""
    for i in range(idLength):
        idResult += random.choice(charList)
    return idResult
