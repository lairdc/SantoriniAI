import { Color } from "./constants.ts";

export class Piece {
    row: number;
    col: number;
    color: Color;

    constructor(row: number, col: number, color: Color) {
        this.row = row;
        this.col = col;
        this.color = color;
    }

    move(row: number, col: number) {
        this.row = row;
        this.col = col;
    }
}