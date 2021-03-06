class Player:
    def __init__(self, player_name: str):
        self.player_name = player_name
        self.hand_cards = []
        self.hidden_cards = []
        self.top_cards = []
        self.is_turn = False
        self.has_won = False
        self.is_ready = False

    def check_won_game(self):
        if self.has_won:
            return True
        if not self.hand_cards and not self.hidden_cards and not self.top_cards:
            self.has_won = True
        return False

    def play_card(self, card):
        if card in self.hand_cards:
            self.remove_card('hand', card)
            return card

        elif card in self.top_cards and not self.hand_cards:
            self.remove_card('top', card)
            return card

        elif card in self.hidden_cards and not self.top_cards and not self.hand_cards:
            self.remove_card('hidden', card)
            return card

        elif card in self.top_cards and self.hand_cards:
            return 0

        elif card in self.hidden_cards and self.hand_cards:
            return 0

        elif card in self.hidden_cards and self.top_cards:
            return 1
        else:
            return 2

    def remove_card(self, card_type: str, card: str):
        if card_type == 'hand':
            self.hand_cards.remove(card)

        if card_type == 'top':
            self.top_cards.remove(card)

        if card_type == 'hidden':
            self.hidden_cards.remove(card)

    def win(self):
        if not self.hand_cards and not self.top_cards and not self.hidden_cards:
            self.won = True
