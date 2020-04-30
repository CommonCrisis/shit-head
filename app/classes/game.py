import random as rnd
from typing import Dict, List
from datetime import datetime
from utils.card_deck import CARD_DECK
from utils.good_job import GOOD_JOB


from .player import Player


class Board:
    def __init__(self, players: Dict[str, Player], game_id: str):
        self.game_id = game_id
        self.pile = []
        self.deck = CARD_DECK.copy()
        rnd.shuffle(self.deck)
        self.players = players
        self.messages = {
            0: 'Play hand cards first',
            1: 'Play top cards first',
            2: 'You don\'t have this card',
            3: 'Play a card lower than 6',
            4: 'It\'s not your turn',
            5: 'Card not playable - pick up the pile',
            6: 'BOOOOOOOOOOOOM!',
            7: 'BOOOOOOOOOOOOM!',
        }
        self.game_started = False
        self.last_updated = datetime.now()

    def _get_val(self, card):
        return int(card.split('_')[0])

    def reset_player(self, player_name: str):
        target_player = self.players[player_name]
        self.deck.append(target_player.hand)
        self.deck.append(target_player.hidden_cards)
        self.deck.append(target_player.top_cards)
        rnd.shuffle(self.deck)

        del self.players[player_name]

    def give_cards(self):
        for player_name, player in self.players.items():
            player.hand = self.deck[:3]
            del self.deck[:3]
            player.hidden_cards = self.deck[:3]
            del self.deck[:3]
            player.top_cards = self.deck[:3]
            del self.deck[:3]
        player_name = rnd.choice(list(self.players.keys()))
        self.players[player_name].is_turn = True
        self.game_started = True

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

    def _played_card_message(self, card: str) -> str:
        return rnd.choice(GOOD_JOB)

    def _test_bomb(self, card: str, pile: List[str]) -> str:
        if self._get_val(card) == 10:
            return True
        if len(self.pile) >= 3:
            last_cards = [self._get_val(c) for c in self.pile[-3:]] + [card]
            if all(x == last_cards[0] for x in last_cards):
                return True

        return False

    def _play_card(self, card: str, player: Player, pile: List[str]) -> str:
        if self._test_bomb(card, pile):
            self.pile = []
            return self.messages[6]
        else:
            self.pile.append(card)
            self.pass_turn(player)
            return self._played_card_message(card)

    def _check_card_not_fits_pile(self, card) -> bool:
        return self._get_val(card) != self._get_val(self.pile[-1])

    def play_turn(self, player: Player, played_card: str):
        always_playable = [2, 5, 10]
        lower_five_playable = [2, 3, 4, 5, 10]

        self.last_updated = datetime.now()

        card = player.play_card(played_card)

        # Card not valid
        if card in self.messages.keys():
            player.hand.append(played_card)
            return 'warning', self.messages[card]

        # No pile yet
        if not self.pile:
            if not player.is_turn and not self._get_val(card) in always_playable:
                player.hand.append(played_card)
                return 'warning', self.messages[4]
            else:
                return 'success', self._play_card(card, player, self.pile)

        # Not turn no playable card
        if not player.is_turn and self._check_card_not_fits_pile(card) and self._get_val(card) not in always_playable:
            player.hand.append(played_card)

            return 'warning', self.messages[4]

        # Check if you need to be less than 6
        if self._get_val(self.pile[-1]) == 5 and self._get_val(card) > 5:
            player.hand.append(played_card)

            return 'warning', self.messages[3]

        # Check if you need to be less than 6 and you have the correct card
        if self._get_val(self.pile[-1]) == 5 and self._get_val(card) in lower_five_playable:
            return 'success', self._play_card(card, player, self.pile)

        # Turn and playable card
        if player.is_turn and self._get_val(card) >= self._get_val(self.pile[-1]) or self._get_val(card) in always_playable:
            return 'success', self._play_card(card, player, self.pile)

        # Turn but no playable card
        if player.is_turn and self._check_card_not_fits_pile(card) and self._get_val(card) not in always_playable:
            player.hand.append(played_card)

            return 'warning', self.messages[5]

        # Not turn but playable cards
        if not player.is_turn and self._get_val(card) == self._get_val(self.pile[-1]):
            return 'success', self._play_card(card, player, self.pile)

        else:
            print('Asd')

    def take_pile(self, player: Player):
        player.hand.extend(self.pile)
        self.pass_turn(player)
        self.pile = []

    def _get_next_player(self, current_player: Player):
        cur_pos = list(self.players.keys()).index(current_player.player_name)
        if cur_pos + 1 < len(self.players.keys()):
            next_player_name = list(self.players.keys())[(cur_pos + 1)]
            return next_player_name
        else:
            next_player_name = list(self.players.keys())[0]
            return next_player_name

    def pass_turn(self, player: Player):
        if player.is_turn:
            player.is_turn = False
            next_player = self._get_next_player(player)
            self.players[next_player].is_turn = True
