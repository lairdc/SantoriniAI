import {useState, useEffect} from "react";
import {useNavigate} from "react-router-dom";

export default function GameSelectionPage() {
    const [bots, setBots] = useState<string[]>([]);
    const [loading, setLoading] = useState(true);
    const [creatingGame, setCreatingGame] = useState(false);
    const [selectedBot, setSelectedBot] = useState<string | null>(null);

    const navigate = useNavigate();

    useEffect(() => {
        fetchBots().catch(console.error);
    }, []);

    const fetchBots = async () => {
        try {
            const response = await fetch("http://localhost:8000/bots", {
                method: "GET",
                headers: {
                    "Accept": "application/json"
                }
            });
            const data: string[] = await response.json();
            setBots(data);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const startGame = async (botId: string) => {
        setCreatingGame(true);
        setSelectedBot(botId);
        try {
            const response = await fetch(`http://localhost:8000/game/create?bot_id=${botId}`, {
                method: "PUT"
            });
            const data = await response.json();
            console.log("Game created with ID:", data.gameId);
            navigate(`/game/${data.gameId}`);

        } catch (err) {
            console.error(err);
        } finally {
            setCreatingGame(false);
            setSelectedBot(null);
        }
    };

    return (
        <div style={{padding: "20px", maxWidth: "1200px", margin: "0 auto"}}>
            <div style={{
                marginBottom: "20px",
                padding: "20px",
                backgroundColor: "#f5f5f5",
                borderRadius: "4px"
            }}>
                <h1 style={{fontSize: "24px", marginBottom: "10px"}}>Play Santorini</h1>
                <p>Choose your opponent from the available bots below</p>
            </div>

            <div style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fill, minmax(250px, 1fr))",
                gap: "20px"
            }}>
                {loading ? <div style={{textAlign: "center", padding: "20px"}}>
                        Loading...
                    </div> :
                    bots.map((bot) => (
                        <div key={bot} style={{
                            border: "1px solid #ddd",
                            borderRadius: "4px",
                            padding: "20px",
                            backgroundColor: "#fff"
                        }}>
                            <h2 style={{fontSize: "20px", marginBottom: "10px"}}>
                                {bot}
                            </h2>
                            <button
                                onClick={() => startGame(bot)}
                                disabled={creatingGame}
                                style={{
                                    width: "100%",
                                    padding: "10px",
                                    backgroundColor: "#007bff",
                                    color: "white",
                                    border: "none",
                                    borderRadius: "4px",
                                    cursor: creatingGame ? "not-allowed" : "pointer",
                                    opacity: creatingGame ? 0.7 : 1
                                }}
                            >
                                {creatingGame && selectedBot === bot
                                    ? "Creating game..."
                                    : "Play against this bot"}
                            </button>
                        </div>
                    ))}
                <div style={{
                    border: "1px solid #ddd",
                    borderRadius: "4px",
                    padding: "20px",
                    backgroundColor: "#fff"
                }}>
                    <h2 style={{fontSize: "20px", marginBottom: "10px"}}>
                        Play Locally
                    </h2>
                    <button
                        onClick={() => navigate("/game")}
                        disabled={creatingGame}
                        style={{
                            width: "100%",
                            padding: "10px",
                            backgroundColor: "#007bff",
                            color: "white",
                            border: "none",
                            borderRadius: "4px",
                            cursor: creatingGame ? "not-allowed" : "pointer",
                            opacity: creatingGame ? 0.7 : 1
                        }}
                    >
                        {creatingGame && selectedBot === null
                            ? "Creating game..."
                            : "Play against a friend"}
                    </button>
                </div>
            </div>
        </div>
    );
};