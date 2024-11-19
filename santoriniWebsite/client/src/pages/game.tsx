import '../fonts.css';
import {Game} from "../game/game.ts";
import {COLS, ROWS} from "../game/constants.ts";
import {createContext, ReactElement, useContext, useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import "./game.css";

const GameContext = createContext<Game>(new Game());

export default function GamePage() {
    // these are the React buttons for individual spaces in [row][col] indexing
    const spaces: ReactElement[][] = [];
    // this is a hack to update the board, since we reuse the same context over, React doesn't push updates
    const [update, forceUpdate] = useState(1);
    
    const game = useContext(GameContext);

    const { gameId } = useParams()


    // this is a bounded queue of size 5
    const [instructionHistory, setInstructionHistory] = useState<string[]>([]);

    useEffect(() => {
        const newInstruction = `${game.gameOver ? `${game.gameOver} wins!` : `${game.turn[0].toUpperCase() + game.turn.substring(1)}'s turn to ${game.move ? "move" : "build"}`}`;
        setInstructionHistory(prev => [newInstruction, ...prev.slice(0, 4)]);
    }, [game.turn, game.move]);

    function InstructionsHistory() {
        return (
            <div className="instructions-history">
                {instructionHistory.map((instruction, index) => (
                    <div key={index} className={`instruction ${index === 0 ? "current" : "old"}`}>
                        {instruction}
                    </div>
                ))}
                <div className="instructions-tip">
                    Tip: For each turn, you must click on a tiny square of your color before clicking on the surrounding squares
                </div>
            </div>
        );
    }

    function Space({row, col}: {row: number, col: number}) {
        function Piece({row, col}: { row: number, col: number}) {
            const piece = game.board.getPiece(row, col);
            return (
                <div className={`piece ${piece?.color} ${update}`} style={
                     piece?.color ? {color: piece.color} : {display: "none"}
                }>&#9632;</div>
            );
        }

        return (
            <button className={`game-space game-space-built-${game.board.getTileLevel(row, col)} ${`${row}-${col}` in game.validMoves ? "game-space-valid" : ""} ${update}`} onClick={async ()=>{
                if (!game.gameOver) {
                    let turn = game.turn;
                    if (!game.select(row, col)) {
                        game.selected = null;
                    }
                    if (gameId && turn === "blue" && game.turn === "red") {
                        const res = await fetch(`http://localhost:8000/game/${gameId}/move`, {
                            method: "POST",
                            headers: {
                                "Content-Type": "application/json",
                                "Accept": "application/json"
                            },
                            body: JSON.stringify({
                                piece: game.lastMoveStart,
                                to: game.lastMoveTo,
                                build: game.lastBuild
                            })
                        });

                        const move = await res.json();

                        game.select(move.piece[1], move.piece[0]);
                        game.select(move.to[1], move.to[0]);
                        game._build(move.build[1], move.build[0]);
                        forceUpdate(update+1)
                    }
                    forceUpdate(update+1);
                }
            }} disabled={gameId != undefined && game.turn == "red"}><Piece row={row} col={col}></Piece></button>
        );
    }

    // create the Space elements for each spot in the grid
    for (let i = 0; i < ROWS; i++) {
        for (let j = 0; j < COLS; j++) {
            if (!spaces[i]) spaces.push([]);
            spaces[i][j] = <Space key={`${i}-${j}`} row={i} col={j}/>
        }
    }

    // put all the spaces in the same row in a shared div
    const gridded = spaces.map((row, i) => <div className={"game-row"} key={`row-${i}`}>{row}</div>);

    return (
        <div className="game-container">
            <div className="game-board">{gridded}</div>
            <div className="instructions-container">
                
                <InstructionsHistory />
                <br />
                <button className="reset-button" onClick={() => {
                    setInstructionHistory([]);
                    game.reset();
                    forceUpdate(update+1)
                }}>Reset</button>
            </div>
        </div>
    );
}
