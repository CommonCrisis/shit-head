import random as rnd
from typing import List, Dict
from .player import Player
from utils.card_deck import CARD_DECK


class Board:
    def __init__(self, players: Dict[str, Player], game_id: str):
        self.game_id = game_id
        self.pile = []
        self.deck = CARD_DECK
        rnd.shuffle(self.deck)
        self.players = players
        self.messages = {
            0: 'Play hand cards first',
            1: 'Play top cards first',
            2: 'You don\'t have this card',
            3: 'Play a card lower than 6',
            4: 'It\'s not your turn',
        }

    def _get_val(self, card):
        return int(card.split('_')[1])

    def give_cards(self):
        for player_name, player in self.players.items():
            player.hand = self.deck[:3]
            del self.deck[:3]
            player.hidden_cards = self.deck[:2]
            del self.deck[:2]
            player.top_cards = self.deck[:2]
            del self.deck[:2]

    def draw_card(self, player: Player):
        if not self.deck:
            return
        if len(player.hand) < 3 and self.deck:
            player.hand.append(self.deck[0])
            del self.deck[0]

    def play_turn(self, player: Player, played_card: str):
        card = player.play_card(played_card)

        if card in self.messages.keys():
            return self.messages[card]

        if not player.is_turn and self._get_val(card) != self._get_val(self.pile[-1]):
            return self.messages[4]

        if not self.pile:
            if self._get_val(card) == 10:
                self.pile = []
                return f'Player bombed with {card}'
            self.pile.append(card)
            return f'Player played {card}'

        # Check if you need to be less than 6
        if self._get_val(self.pile[-1]) == 5 and self._get_val(card) > 5:
            return self.messages[3]

        if self._get_val(self.pile[-1]) == 5 and self._get_val(card) <= 5:
            self.pile.append(card)
            return f'Player played {card}'

        if self._get_val(card) == 2:
            self.pile.append(card)
            return f'Player resetted with {card}'

        elif self._get_val(card) == 5:
            self.pile.append(card)
            return f'Player played {card}'

        elif self._get_val(card) == 10:
            self.pile = []
            return f'Player bombed with {card}'

        elif self._get_val(card) >= self._get_val(self.pile[-1]):
            self.pile.append(card)
            return f'Player played {card}'

        else:
            self.take_pile(player)
            return 'No card to play...'

    def take_pile(self, player: Player):
        player.hand.extend(self.pile)
        self.pile = []

    def _get_next_player(self, current_player: Player):
        cur_pos = list(self.players.keys()).index(current_player)
        if cur_pos < len(self.players.keys()):
            next_player_name = list(self.players.keys())[cur_pos + 1]
            return next_player_name
        
        else:
            next_player_name = list(self.players.keys())[0]
            return next_player_name
        
    def pass_turn(self, player: Player):
        if player.is_turn:
            player.is_turn = False
            next_player = self._get_next_player(player)
            self.players[next_player].is_turn = True
