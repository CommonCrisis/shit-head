import uuid
from typing import List

import uvicorn
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from classes.game import Board
from classes.player import Player

app = FastAPI()

origins = [
    'http://localhost:3000',
]

app.add_middleware(
    CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

running_games = {}


class NewGame(BaseModel):
    host: str
    game_id: str


@app.post('/play/new_game')
def start_game(new_game: NewGame):
    players = {new_game.host: Player(new_game.host)}
    new_game = Board(players, new_game.game_id)
    running_games.update({new_game.game_id: new_game})

    return {'game_id': new_game.game_id}


@app.get('/play/{game_id}/give_cards')
def give_cards(game_id: str):
    running_games[game_id].give_cards()
    running_games[game_id].game_started = True

    return {'game_id': game_id}


@app.get('/play/{game_id}/get_players')
def get_players(game_id: str):
    if game_id not in running_games.keys():
        return {'info': f'Game ID {game_id} does not exist'}

    current_players = list(running_games[game_id].players.keys())

    return {'players': current_players,
            'started': running_games[game_id].game_started}


@app.get('/play/{game_id}/add_player/{player_name}')
def add_players(game_id: str, player_name: str):
    if game_id not in running_games.keys():
        return {'info': f'Game ID {game_id} does not exist'}

    if len(running_games[game_id].players.keys()) > 5:
        return {'info': f'MaxPlayers for ID {game_id} reached'}
    new_player = Player(player_name)

    running_games[game_id].players.update({player_name: new_player})

    return {'info': f'Player {player_name} added'}


@app.get('/play/{game_id}/end-game')
def kill_game(game_id: str):
    del running_games[game_id]

    return {'info': f'Game with ID {game_id} has been closed'}


@app.get('/play/{game_id}/{player_id}/update')
def get_board(game_id: str, player_id: str):
    # if game_id == 'testid':
    #     test_data = {player_id: {
    #         'hand_cards': ['2_H', '2_H', '2_H'],
    #         'top_cards': ['2_H', '2_H', '2_H'],
    #         'hidden_cards': ['2_H', '2_H', '2_H'],
    #         'pile': ['2_H'],
    #         'deck': ['2_H'],
    #     }
    #     }
    #     return {
    #         'game': test_data
    #     }

    current_game = running_games[game_id]
    player = current_game.players[player_id]
    current_game.draw_cards(player)
    game_overview = {}

    for player_name in current_game.players.keys():
        game_overview.update(
            {
                player_name: {
                    'hand_cards': current_game.players[player_name].hand,
                    'top_cards': current_game.players[player_name].top_cards,
                    'hidden_cards': current_game.players[player_name].hidden_cards,
                }
            })
    game_overview.update(
        {'board_cards': {
            'pile': current_game.pile,
            'deck': current_game.deck,
        }}
    )
    return {'game': game_overview}


@app.get('/play/{game_id}/{player_id}/play_card/{card}')
def play_turn(game_id: str, player_id: str, card: str):
    player = running_games[game_id].players[player_id]
    running_games[game_id].play_turn(player, card)
    if len(player.hand) < 3 and running_games[game_id].deck:
        running_games[game_id].draw_cards(player)
    return {'info': 'card played'}


@app.get('/play/{game_id}/{player_id}/take_pile')
def take_pile(game_id: str, player_id: str):
    player = running_games[game_id].players[player_id]
    running_games[game_id].take_pile(player)


if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=54321, log_level='info')
