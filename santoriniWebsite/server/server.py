from typing import Tuple
from uuid import uuid4, UUID

from fastapi import FastAPI, Response
from pydantic import BaseModel

from santoriniGame.ColbysMiniMax.ColbysMiniMax import ColbysMiniMax
from santoriniGame.TylerMiniMax.TylerMiniMax import TylerMiniMax
from santoriniGame.YaseminsMiniMax.YaseminsMiniMax import YaseminsMiniMax
from santoriniGame.constants import RED, BLUE
from santoriniGame.randombot import RandomBot
from santoriniWebsite.server.remotegame import RemoteGame

app = FastAPI()

games: dict[UUID, RemoteGame] = {}
bots = {
    "colby": ColbysMiniMax,
    "random": RandomBot,
    "yasemin": YaseminsMiniMax,
    "tyler": TylerMiniMax
}

class Move(BaseModel):
    # the location of the piece that is being acted upon
    piece: Tuple[int, int]
    # where to move the piece (x, y)
    to: Tuple[int, int]
    # where to build
    build: Tuple[int, int]

@app.get("/bots")
def get_bots():
    return list(bots.keys())

@app.put("/game/create")
async def create_game_board(bot_id: str):
    game_id = uuid4()
    bot_type = bots.get(bot_id)
    if bot_type is None:
        return Response(status_code=404) # 404 Not Found
    game = RemoteGame()
    bot = bot_type(game, RED, BLUE)
    games[game_id] = game
    game.bot = bot
    return {"gameId": game_id}

@app.post("/game/{game_id}/move")
async def make_piece_move(game_id: UUID, move: Move):
    game = games.get(game_id)
    if game is None:
        return Response(status_code=404) # 404 Not Found
    game.select(move.piece[1], move.piece[0])
    game.select(move.to[1], move.to[0])
    game._build(move.build[1], move.build[0])
    game.bot.make_move()
    move = Move(
        piece = (game.last_move_selected.col, game.last_move_selected.row),
        to = (game.last_move_x, game.last_move_y),
        build = (game.last_build_x, game.last_build_y)
    )
    return move

@app.delete("/game/{game_id}")
async def delete_game_board(game_id: UUID):
    games.pop(game_id)
    # return a 204 No Content
    return Response(status_code=204)