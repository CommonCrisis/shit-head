def translate_card(card):
    card_items = card.split('_')

    name_mapper = {
        'H': 'Hearts',
        'D': 'Diamonds',
        'C': 'Clubs',
        'S': 'Spades'
    }

    number_mapper = {
        11: 'Jack',
        12: 'Queen',
        13: 'King',
        14: 'Ace'
    }

    color = name_mapper[card_items[1]]
    number = card_items[0] if int(card_items[0]) not in [11, 12, 13, 14] else number_mapper[int(card_items[0])]

    return f'{number} of {color}'
