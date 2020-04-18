# from classes.game import Board
# from classes.player import Player
# import random as rnd

# player_1 = Player(True)
# player_2 = Player(False)

# players = [player_1, player_2]

# board = Board(players)
# board.give_cards()


# for p in range(100):
#     [player.win() for player in players]
#     if player_1.won:
#         print('Player won the game')
#         break
#     if player_1.hand:
#         play_card = rnd.choice(player_1.hand)
#     elif not player_1.hand and player_1.top_cards:
#         play_card = rnd.choice(player_1.top_cards)
#     else:
#         play_card = rnd.choice(player_1.hidden_cards)
#     print(board.play_turn(player_1, play_card))
#     board.draw_card(player_1)
#     print(len(player_1.hand))


players = {'die': 'erster', 'das': 'zweiter', 'der': 'dritter'}


print('asd')
