import uuid
from typing import List

import uvicorn
from fastapi import FastAPI, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from classes.game import Board
from classes.player import Player
from utils.clean_game_store import clean_game_store
from utils.server_message import server_message


app = FastAPI()

origins = [
    'http://localhost:3000',
    'https://shit-head.eu',
    'https://www.shit-head.eu',
    'http://www.shit-head.eu',
    'http://www.shit-head.eu',
    'https://ec2co-ecsel-vuo1lh5jqrpo-1885013979.eu-central-1.elb.amazonaws.com',
]

app.add_middleware(
    CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

running_games = {}


@app.get('/')
def alive():
    return {'info': 'alive'}


class NewGame(BaseModel):
    host: str
    game_id: str


class SetTopCards(BaseModel):
    top_cards: List[str]


@app.post('/play/new_game')
def start_game(new_game: NewGame, background_tasks: BackgroundTasks):
    background_tasks.add_task(clean_game_store, running_games)
    if new_game.game_id in running_games.keys():
        return server_message('error', f'Game with ID {new_game.game_id} already exists.')

    players = {new_game.host: Player(new_game.host)}
    new_game = Board(players, new_game.game_id)
    running_games.update({new_game.game_id: new_game})
    return server_message('success', f'New game with ID {new_game.game_id} created.')


@app.get('/play/{game_id}/give_cards')
def give_cards(game_id: str):
    running_games[game_id].give_cards()

    return server_message('info', 'Dealing cards to players')


@app.get('/play/{game_id}/get_players')
async def get_players(game_id: str):
    if game_id not in running_games.keys():
        return {'error': f'Game ID {game_id} does not exist'}

    current_players = list(running_games[game_id].players.keys())

    return {'players': current_players, 'started': running_games[game_id].game_started}


@app.get('/play/{game_id}/add_player/{player_name}')
async def add_players(game_id: str, player_name: str):
    if game_id not in running_games.keys():
        return server_message('warning', f'Game ID {game_id} does not exist')
    if running_games[game_id].game_started:
        return server_message('error', f'Game ID {game_id} already started')
    if player_name in running_games[game_id].players.keys():
        return server_message('error', f'Name already taken - please rename yourself')
    if len(running_games[game_id].players.keys()) > 5:
        return server_message('warning', f'Max players for ID {game_id} reached')
    new_player = Player(player_name)

    running_games[game_id].players.update({player_name: new_player})
    return server_message('success', f'Joined game {game_id}')


@app.post('/play/{game_id}/{player_name}/top_cards')
def set_top_cards(game_id: str, player_name: str, top_cards: SetTopCards):
    cards = top_cards.top_cards
    if len(cards) != 3:
        return server_message('warning', 'You can only select three cards!')
    current_game = running_games[game_id]
    player = current_game.players[player_name]
    current_game.set_top_cards(cards, player)

    return server_message('success', f'Top cards set!')


@app.get('/play/{game_id}/end_game')
def kill_game(game_id: str):
    del running_games[game_id]

    return server_message('success', f'Game with ID {game_id} has been closed')


@app.get('/play/{game_id}/leave_game/{player_name}')
def leave_game(game_id: str, player_name: str):
    running_games[game_id].reset_player(player_name)

    return server_message('info', f'{player_name} left the game')


@app.get('/play/{game_id}/{player_name}/update')
async def get_board(game_id: str, player_name: str):
    current_game = running_games[game_id]
    if player_name not in list(current_game.players.keys()):
        return server_message('error', f'You are not part of this game!')

    player = current_game.players[player_name]

    if player.check_won_game():
        kill_game(game_id)
        return server_message('success', f'You have won the game!')

    current_game.draw_cards(player)
    game_overview = {'players': []}
    all_ready = []
    for player_name in current_game.players.keys():
        all_ready.append(current_game.players[player_name].is_ready)
        game_overview['players'].append(
            {
                'player_name': player_name,
                'hand_cards': current_game.players[player_name].hand,
                'top_cards': current_game.players[player_name].top_cards,
                'hidden_cards': current_game.players[player_name].hidden_cards,
                'is_turn': current_game.players[player_name].is_turn,
                'has_won': current_game.players[player_name].has_won,
            }
        )

    game_overview.update({'board_cards': {'pile': current_game.pile, 'deck': current_game.deck}, 'all_ready': all(all_ready), 'type': 'update', 'message': ''})
    return game_overview


@app.get('/play/{game_id}/{player_name}/play_card/{card}')
async def play_turn(game_id: str, player_name: str, card: str):
    player = running_games[game_id].players[player_name]
    message_type, message = running_games[game_id].play_turn(player, card)

    if len(player.hand) < 3 and running_games[game_id].deck:
        running_games[game_id].draw_cards(player)

    return server_message(message_type, message)


@app.get('/play/{game_id}/{player_name}/take_pile')
def take_pile(game_id: str, player_name: str):
    player = running_games[game_id].players[player_name]
    running_games[game_id].take_pile(player)

    return server_message('info', 'Sorry for all the cards :/')


if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=5000, log_level='info')
