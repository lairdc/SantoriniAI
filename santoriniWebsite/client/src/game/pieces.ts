export class Piece {
    row: number;
    col: number;
    color: [number, number, number];

    constructor(row: number, col: number, color: [number, number, number]) {
        this.row = row;
        this.col = col;
        this.color = color;
    }

    move(row: number, col: number) {
        this.row = row;
        this.col = col;
    }
}