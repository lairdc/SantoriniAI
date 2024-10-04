import { Piece } from './pieces';
import { Board } from './board';
import { BLUE, RED } from './constants';

export class Game {
    private selected: Piece | null;
    private board: Board;
    private turn: [number, number, number];
    private validMoves: { [key: string]: boolean };
    private move: boolean;
    private gameOver: string | null;

    constructor() {
        this.selected = null;
        this.board = new Board();
        this.turn = BLUE;
        this.validMoves = {};
        this.move = true;  //start in move phase
        this.gameOver = null;  //reset game state
    }

    reset() {
        this.selected = null;
        this.board = new Board();
        this.turn = BLUE;
        this.validMoves = {};
        this.move = true;
        this.gameOver = null;
    }

    select(row: number, col: number): boolean {
        const piece = this.board.getPiece(row, col);
        if (this.selected) {
            if (this.move) {  // Move phase
                if (this.validMoves[`${row}-${col}`]) {
                    this._move(row, col);
                    return true;
                } else {
                    this.selected = null;
                    this.validMoves = {};
                }
            } else {  // Build phase
                if (this.validMoves[`${row}-${col}`]) {
                    this._build(row, col);
                    return true;
                }
            }
        } else {
            if (piece && piece.color === this.turn) {
                this.selected = piece;
                this.validMoves = this.board.getValidMoves(piece);
                return true;
            }
        }
        return false;
    }

    private _move(row: number, col: number) {
        if (this.selected) {
            this.board.move(this.selected, row, col);
            //check if the piece moved onto a level 3 tile (win condition)
            if (this.board.getTileLevel(row, col) === 3) {
                this.gameOver = this.turn === BLUE ? 'BLUE' : 'RED';
                console.log(`${this.gameOver} wins!`);
                return;
            }
            this.validMoves = this.board.getValidBuilds(this.selected);
            this.move = false;  //switch to build phase
        }
    }

    private _build(row: number, col: number) {
        this.board.build(row, col);
        this.selected = null;
        this.move = true;  //return to move phase
        this.changeTurn();
    }

    changeTurn() {
        this.turn = this.turn === BLUE ? RED : BLUE;
    }
}