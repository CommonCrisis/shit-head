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
        return int(card.split('_')[0])

    def give_cards(self):
        for player_name, player in self.players.items():
            player.hand = self.deck[:3]
            del self.deck[:3]
            player.hidden_cards = self.deck[:3]
            del self.deck[:3]
            player.top_cards = self.deck[:3]
            del self.deck[:3]

    def draw_cards(self, player: Player):
        if not self.deck:
            return
        if len(player.hand) < 3 and self.deck:
            cards_to_draw = 3 - len(player.hand)
            for draw in range(0, cards_to_draw):
                if not self.deck:
                    return
                player.hand.append(self.deck[0])
                del self.deck[0]

    def play_turn(self, player: Player, played_card: str):
        card = player.play_card(played_card)

        if card in self.messages.keys():
            player.hand.append(played_card)
            return self.messages[card]

        if not self.pile:
            if not player.is_turn and not self._get_val(card) in [2, 5, 10]:
                player.hand.append(played_card)
                return self.messages[4]
            if self._get_val(card) == 10:
                self.pile = []
                return f'Player bombed with {card}'
            self.pile.append(card)
            return f'Player played {card}'

        if not player.is_turn and self._get_val(card) != self._get_val(self.pile[-1]):
            player.hand.append(played_card)
            return self.messages[4]

        # Check if you need to be less than 6
        if self._get_val(self.pile[-1]) == 5 and self._get_val(card) > 5 and self._get_val(card) != 10:
            # player.hand.append(played_card)
            self.take_pile(player, played_card)
            return self.messages[3]

        if self._get_val(self.pile[-1]) == 5 and self._get_val(card) in [2, 3, 4, 5, 10]:
            if self._get_val(card) == 10:
                self.pile = []
                return f'Player bombed with {card}'
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
            self.take_pile(player, played_card)
            return 'No card to play...'

    def take_pile(self, player: Player, card: str):
        player.hand.extend(self.pile)
        player.hand.append(card)
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
