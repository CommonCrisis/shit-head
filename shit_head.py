from fastapi import FastAPI, Query
import uuid
from classes.game import Board
from classes.player import Player
from typing import List
import uvicorn

app = FastAPI()

running_games = {}


@app.get('/play/new-game')
def start_game(names: List[str] = Query(None)):
    # game_id = str(uuid.uuid4())
    game_id = 'cce19207-a9d7-4a66-a18e-b49ca076cccd'
    players = {name: Player(name) for name in names}
    new_game = Board(players, game_id)
    running_games.update({game_id: new_game})
    
    return {'game_id': game_id}


@app.get('/play/{game_id}/end-game')
def kill_game(game_id: str):
    del running_games[game_id]
    
    return {'info': f'Game with ID {game_id} has been closed'}


@app.get('/play/{game_id}/{player_id}/update')
def get_board(game_id: str, player_id: str):
    current_game = running_games[game_id]
    game = {
        'hand_cards': current_game.players[player_id].hand,
        'upper_cards': current_game.players[player_id].top_cards,
        'hidden_cards': current_game.players[player_id].hidden_cards,
        'pile': current_game.pile,
        'deck': current_game.deck
    }
    
    return {'game': game}


@app.get('/play/{game_id}/init-game')
def init_game(game_id: str):
    running_games[game_id].give_cards()
    return {'info': 'cards given'}


@app.get('/play/{game_id}/{player_id}/play')
def play_turn(game_id: str, player_id: str):
    running_games[game_id].give_cards()
    return {'info': 'cards given'}


@app.get('/play/{game_id}/{player_id}/take_pile')
def play_turn(game_id: str, player_id: str):
    running_games[game_id].players[player_id].take_pile()


if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=54321, log_level='info')