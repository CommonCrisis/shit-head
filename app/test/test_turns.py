import pytest
from classes.player import Player
from classes.game import Board


def set_up_game(hans_hand_cards, ulli_hand_cards, hanna_hand_cards, turn_name):
    hans = Player('Hans')
    ulli = Player('Ulli')
    hanna = Player('Hanna')

    hans.hand_cards = hans_hand_cards
    ulli.hand_cards = ulli_hand_cards
    hanna.hand_cards = hanna_hand_cards
    players = {
        'Hans': hans,
        'Ulli': ulli,
        'Hanna': hanna
    }
    test_game = Board(players, '1234')

    # Adjust game

    test_game.deck = []
    test_game._remove_turns()

    test_game.players[turn_name].is_turn = True

    return test_game


def play_turn(player_1: str, player_2: str, card: str, test_game):
    player = test_game.players[player_1]
    message_type, message = test_game.play_turn(player, card)
    return test_game.players[player_2].is_turn


def play_match():
    hans_hand_cards = ['3_H', '12_H', '10_H']
    ulli_hand_cards = ['4_D', '12_D', '13_D']
    hanna_hand_cards = ['2_C', '8_C', '13_C']
    test_game = set_up_game(hans_hand_cards, ulli_hand_cards, hanna_hand_cards, 'Hanna')
    all_true = []
    all_true.append(play_turn('Hanna', 'Hans', '8_C', test_game))
    all_true.append(play_turn('Hans', 'Hans', '10_H', test_game))
    all_true.append(play_turn('Hans', 'Ulli', '3_H', test_game))
    all_true.append(play_turn('Ulli', 'Hanna', '12_D', test_game))
    all_true.append(play_turn('Hanna', 'Hans', '13_C', test_game))
    all_true.append(play_turn('Ulli', 'Hanna', '13_D', test_game))
    assert False not in all_true, 'all true'


def take_pile_while_turn():
    hans_hand_cards = ['3_H', '12_H', '10_H']
    ulli_hand_cards = ['4_D', '12_D', '13_D']
    hanna_hand_cards = ['2_C', '8_C', '13_C']
    test_game = set_up_game(hans_hand_cards, ulli_hand_cards, hanna_hand_cards, 'Hanna')
    play_turn('Hanna', 'Hans', '8_C', test_game)
    hans = test_game.players['Hans']
    test_game.take_pile(hans)

    assert '8_C' in hans.hand_cards


def take_pile_while_not_turn():
    hans_hand_cards = ['3_H', '12_H', '10_H']
    ulli_hand_cards = ['4_D', '12_D', '13_D']
    hanna_hand_cards = ['2_C', '8_C', '13_C']
    test_game = set_up_game(hans_hand_cards, ulli_hand_cards, hanna_hand_cards, 'Hanna')
    play_turn('Hanna', 'Hans', '8_C', test_game)
    ulli = test_game.players['Ulli']
    warning, message = test_game.take_pile(ulli)

    assert warning == 'warning'


def bomb_4_cards_turn():
    hans_hand_cards = ['3_H', '12_H', '10_H']
    ulli_hand_cards = ['4_D', '12_D', '13_D']
    hanna_hand_cards = ['4_C', '4_D', '4_H', '4_S']
    test_game = set_up_game(hans_hand_cards, ulli_hand_cards, hanna_hand_cards, 'Hanna')
    turns = []
    for card in ['4_C', '4_D', '4_H', '4_S']:
        turns.append(play_turn('Hanna', 'Hans', card, test_game))

    assert turns == [True, True, True, False]


def skip_player_won():
    hans_hand_cards = ['3_H', '12_H', '10_H']
    ulli_hand_cards = ['4_D', '12_D', '13_D']
    hanna_hand_cards = ['4_C', '4_D', '4_H', '12_S']
    test_game = set_up_game(hans_hand_cards, ulli_hand_cards, hanna_hand_cards, 'Hanna')
    assert play_turn('Hanna', 'Hans', '4_C', test_game)
    assert play_turn('Hans', 'Ulli', '12_H', test_game)
    test_game.players['Hans'].has_won = True
    assert play_turn('Ulli', 'Hanna', '12_D', test_game)
    assert play_turn('Hanna', 'Ulli', '12_S', test_game)


play_match()
take_pile_while_turn()
take_pile_while_not_turn()
bomb_4_cards_turn()
skip_player_won()


### TODOs ####
# swipe cards - space to throw card
# play only one card
# select new card deselct old -- only select newest if new var
# right click select
# left click play
