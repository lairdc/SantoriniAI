import '../fonts.css';
import {Game} from "../game/game.ts";
import {COLS, ROWS} from "../game/constants.ts";
import {createContext, ReactElement, useContext, useState} from "react";
import "./game.css";

const GameContext = createContext<Game>(new Game());

export default function GamePage() {
    const spaces: ReactElement[][] = [];
    const [update, forceUpdate] = useState(1);
    const game = useContext(GameContext);

    function Space({row, col}: {row: number, col: number}) {
        function Piece({row, col}: { row: number, col: number}) {
            const piece = game.board.getPiece(row, col);
            return (
                <div className={`piece ${piece?.color} ${update}`} style={
                     piece?.color ? {color: piece.color} : {display: "none", update}
                }>&#9632;</div>
            );
        }

        return (
            <button className={`game-space game-space-built-${game.board.getTileLevel(row, col)} ${update}`} onClick={()=>{
                if (!game.gameOver) {
                     if (!game.select(row, col)) {
                        game.selected = null;
                    }
                    forceUpdate(update+1);
                }
            }}><Piece row={row} col={col}></Piece></button>
        );
    }

    for (let i = 0; i < ROWS; i++) {
        for (let j = 0; j < COLS; j++) {
            if (!spaces[i]) spaces.push([]);
            spaces[i][j] = <Space key={`${i}-${j}`} row={i} col={j}/>
        }
    }

    const gridded = spaces.map((row, i) => <div className={"game-row"} key={`row-${i}`}>{row}</div>);

    return [
        <span key="game-state">{game.gameOver ? `${game.gameOver} wins!` : `${game.turn}'s turn to ${game.move ? "move" : "build"}`}</span>,
        ...gridded
    ]
}
