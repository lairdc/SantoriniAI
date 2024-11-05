from typing import Union
from uuid import uuid4

from fastapi import FastAPI, Response

from ColbysMiniMax.ColbysMiniMax import ColbysMiniMax
from TylerMiniMax.TylerMiniMax import TylerMiniMax
from YaseminsMiniMax.YaseminsMiniMax import YaseminsMiniMax
from board import Board

app = FastAPI()

boards = {}
bots = {
    "colby": ColbysMiniMax,
    "yasemin": YaseminsMiniMax,
    "tyler": TylerMiniMax
}

@app.get("/bots")
def get_bots():
    return bots

@app.put("/game/create")
async def create_game_board(bot: Union[str, None] = None):
    game_id = uuid4()
    # TODO: create a new class to represent this game
    boards[game_id] = Board()
    return {"gameId": game_id}


@app.delete("/game/{game_id}")
async def delete_game_board(game_id: str):
    boards.pop(game_id)
    # return a 204 No Content
    return Response(status_code=204)
