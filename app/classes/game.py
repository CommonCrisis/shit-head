import random as rnd
from typing import Dict, List
from datetime import datetime
from utils.card_deck import CARD_DECK
from utils.good_job import GOOD_JOB
from utils.card_name_translator import translate_card

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
        self.game_log = []

    def _get_val(self, card):
        return int(card.split('_')[0])

    def _remove_turns(self):
        for player in self.players:
            self.players[player].is_turn = False

    def reset_player(self, player_name: str):
        target_player = self.players[player_name]
        self.deck.append(target_player.hand_cards)
        self.deck.append(target_player.hidden_cards)
        self.deck.append(target_player.top_cards)
        rnd.shuffle(self.deck)

        del self.players[player_name]

    def give_cards(self):
        for player_name, player in self.players.items():
            player.hand_cards = self.deck[:6]
            del self.deck[:6]
            player.hidden_cards = self.deck[:3]
            del self.deck[:3]
            player.top_cards = []
        player_name = rnd.choice(list(self.players.keys()))
        self.players[player_name].is_turn = True
        self.game_started = True

    def set_top_cards(self, cards: List[str], player: Player):
        if len(cards) == 3:
            player.top_cards = cards
            player.hand_cards = [item for item in player.hand_cards if item not in cards]
            player.is_ready = True
            return True

        return False

    def draw_cards(self, player: Player):
        if not self.deck:
            return
        if len(player.hand_cards) < 3 and self.deck:
            cards_to_draw = 3 - len(player.hand_cards)
            for draw in range(0, cards_to_draw):
                if not self.deck:
                    return
                player.hand_cards.append(self.deck[0])
                del self.deck[0]

    def _played_card_message(self, card: str) -> str:
        return rnd.choice(GOOD_JOB.copy())

    def _test_bomb(self, player: str, card: str, pile: List[str]) -> str:
        if self._get_val(card) == 10:

            return True
        if len(self.pile) >= 3:
            last_cards = [self._get_val(c) for c in self.pile[-3:]] + [self._get_val(card)]
            if all(x == last_cards[0] for x in last_cards):

                return True

        return False

    def _play_card(self, card: str, player: Player, pile: List[str], thrown: bool = False) -> str:
        if self._test_bomb(player.player_name, card, pile):
            self.pile = []
            self.game_log.append({
                'player': player.player_name,
                'message': f'{player.player_name} played a {translate_card(card)} and bombed!'
            })
            if thrown:
                self._remove_turns()
                player.is_turn = True

            return self.messages[6]
        else:
            self.pile.append(card)
            self.pass_turn(player, thrown)
            self.game_log.append({
                'player': player.player_name,
                'message': f'{player.player_name} played a {translate_card(card)}'
            })

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
            player.hand_cards.append(played_card)
            return 'warning', self.messages[card]

        # No pile yet
        if not self.pile:
            if not player.is_turn:
                player.hand_cards.append(played_card)
                return 'warning', self.messages[4]
            else:
                return 'success', self._play_card(card, player, self.pile)

        # Not turn no playable card
        elif not player.is_turn and self._check_card_not_fits_pile(card):
            player.hand_cards.append(played_card)

            return 'warning', self.messages[4]

        # Check if you need to be less than 6 and you have the correct card
        elif self._get_val(self.pile[-1]) == 5 and self._get_val(card) in lower_five_playable or self._get_val(card) in always_playable:

            return 'success', self._play_card(card, player, self.pile)

        # Check if you need to be less than 6
        elif self._get_val(self.pile[-1]) == 5 and self._get_val(card) > 5:
            player.hand_cards.append(played_card)

            return 'warning', self.messages[3]

        # Turn and playable card
        elif player.is_turn and self._get_val(card) >= self._get_val(self.pile[-1]) or self._get_val(card) in always_playable:

            return 'success', self._play_card(card, player, self.pile)

        # Turn but no playable card
        elif player.is_turn and self._check_card_not_fits_pile(card) and self._get_val(card) not in always_playable:
            player.hand_cards.append(played_card)

            return 'warning', self.messages[5]

        # Not turn but playable cards
        elif not player.is_turn and self._get_val(card) == self._get_val(self.pile[-1]):
            return 'success', self._play_card(card, player, self.pile, thrown=True)

        else:
            print('Asd')

    def take_pile(self, player: Player):
        if not player.is_turn:
            return 'warning', self.messages[4]
        player.hand_cards.extend(self.pile)
        self.pass_turn(player)
        self.pile = []
        self.game_log.append({
            'player': player.player_name,
            'message': f'{player.player_name} took the whole pile...'
        })

    def _get_next_player(self, current_player: Player):
        cur_pos = list(self.players.keys()).index(current_player.player_name)
        if cur_pos + 1 < len(self.players.keys()):
            next_player_name = list(self.players.keys())[(cur_pos + 1)]
            return next_player_name
        else:
            next_player_name = list(self.players.keys())[0]
            return next_player_name

    def pass_turn(self, player: Player, throw: bool = False):
        if player.is_turn:
            player.is_turn = False
            next_player = self._get_next_player(player)
            self.players[next_player].is_turn = True
        if not player.is_turn and throw:
            self._remove_turns()
            next_player = self._get_next_player(player)
            self.players[next_player].is_turn = True

