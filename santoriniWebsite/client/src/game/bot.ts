import { Game } from "./game.ts";
import { Piece } from "./pieces.ts";
import { Color } from "./constants.ts";

export class Bot {
    game: Game;
    ownColor: Color
    opponentColor: Color

    constructor(game: Game, ownColor: Color, opponentColor: Color) {
        this.game = game;
        this.ownColor = ownColor;
        this.opponentColor = opponentColor;
    }

    makeMove() {
        let ownPieces: Piece[] = this.game.board.getAllPieces(this.ownColor);
        /*let opponentPieces: Piece[] = this.game.board.getAllPieces(this.opponentColor);

        let gameState: { row: number, col: number, level: number, occupant: number }[] = [];

        for (let row = 0; row < 5; row++) {
            for (let col = 0; col < 5; col++) {
                let level = this.game.board.getTileLevel(row, col);
                let piece = this.game.board.getPiece(row, col);
                let occupant = 0;
                if (piece?.color === this.ownColor) occupant = 1;
                else if (piece?.color === this.opponentColor) occupant = 2;
                gameState.push({row, col, level, occupant});
            }
        }*/

        if (!ownPieces) return;

        let selected = ownPieces[Math.floor(Math.random()*ownPieces.length)];
        let validMoves = this.game.board.getValidMoves(selected);
        if (validMoves) {
            let [row, col] = Object.keys(validMoves)[Math.floor(Math.random()*validMoves.length)].split(",").map(parseInt);
            if (this.game.select(row, col)) {
                this.game._move(row, col);

                let validBuilds = this.game.board.getValidBuilds(this.game.selected!);
                if (validBuilds) {
                    let [buildRow, buildCol] = Object.keys(validBuilds)[Math.floor(Math.random()*validBuilds.length)].split(",").map(parseInt);
                    this.game._build(buildRow, buildCol);
                }
            }
        }
        this.game.selected = null;
    }
}