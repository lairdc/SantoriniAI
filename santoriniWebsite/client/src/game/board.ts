import { Piece } from './pieces';
import { COLS, ROWS, RED, BLUE } from './constants';

export class Board {
    board: Piece[]; //1d list of pieces
    tileLevels: number[][];

    constructor() {
        this.board = [];
        this.tileLevels = Array.from({ length: ROWS }, () => Array(COLS).fill(0));
        this.createBoard();
    }

    createBoard(): void {
        this.board.push(new Piece(1, 1, BLUE));
        this.board.push(new Piece(1, COLS - 2, BLUE));
        this.board.push(new Piece(ROWS - 2, 1, RED));
        this.board.push(new Piece(ROWS - 2, COLS - 2, RED));
    }

    movePiece(piece: Piece, row: number, col: number): void {
        const newBoard = this.board.filter(p => p !== piece);
        piece.move(row, col);
        newBoard.push(piece);
        this.board = newBoard;
    }

    getPiece(row: number, col: number): Piece | null {
        return this.board.find(piece => piece.row === row && piece.col === col) || null;
    }

    getValidMoves(piece: Piece): { [key: string]: number } {
        const moves: { [key: string]: number } = {};
        const directions = [
            [-1, -1], [-1, 0], [-1, 1], //top left, top, top right
            [0, -1], [0, 1], //left, right
            [1, -1], [1, 0], [1, 1], //bottom left, bottom, bottom right
        ];
        for (let [dRow, dCol] of directions) {
            const newRow = piece.row + dRow;
            const newCol = piece.col + dCol;
            if (newRow >= 0 && newRow < ROWS && newCol >= 0 && newCol < COLS) {
                const targetLevel = this.tileLevels[newRow][newCol];
                if (targetLevel < 4 && (targetLevel - this.tileLevels[piece.row][piece.col] <= 1) && !this.getPiece(newRow, newCol)) {
                    moves[`${newRow},${newCol}`] = targetLevel;
                }
            }
        }
        return moves;
    }

    getValidBuilds(piece: Piece): { [key: string]: number } {
        const builds: { [key: string]: number } = {};
        const directions = [
            [-1, -1], [-1, 0], [-1, 1],
            [0, -1], [0, 1],
            [1, -1], [1, 0], [1, 1],
        ];
        for (let [dRow, dCol] of directions) {
            const newRow = piece.row + dRow;
            const newCol = piece.col + dCol;
            if (newRow >= 0 && newRow < ROWS && newCol >= 0 && newCol < COLS) {
                const targetLevel = this.tileLevels[newRow][newCol];
                if (targetLevel < 4 && !this.getPiece(newRow, newCol)) {
                    builds[`${newRow},${newCol}`] = targetLevel;
                }
            }
        }
        return builds;
    }

    build(row: number, col: number): void {
        if (this.tileLevels[row][col] < 4) {
            this.tileLevels[row][col] += 1;
        }
    }

    getAllPieces(color: [number, number, number]): Piece[] {
        return this.board.filter(piece => piece.color === color);
    }

    getTileLevel(row: number, col: number): number {
        return this.tileLevels[row][col];
    }
    move(piece: Piece, row: number, col: number): void {
        const newBoard = this.board.filter(p => p !== piece);
        piece.move(row, col);
        newBoard.push(piece);
        this.board = newBoard;
    }
}