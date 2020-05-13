def translate_card(card):

    number_mapper = {
        11: 'Jack',
        12: 'Queen',
        13: 'King',
        14: 'Ace'
    }

    number = card if int(card) not in [11, 12, 13, 14] else number_mapper[int(card)]

    return number
