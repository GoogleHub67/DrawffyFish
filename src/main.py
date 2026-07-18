import os
import sys
import json
import yaml
import chess
import requests
import time
import threading
import logging
import sqlite3

# ENFORCE EXPLICIT DIRECTORY PATH ROUTING
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# CONFIGURING BOT.LOG FILE INFRASTRUCTURE
logging.basicConfig(
    filename=os.path.join(BASE_DIR, "bot.log"),
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# INITIALIZING DRAWFFY_HIST.DB SQLITE DATABASE SCHEMA
DB_PATH = os.path.join(BASE_DIR, "drawffy_hist.db")
def init_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS game_history (
            game_id TEXT PRIMARY KEY,
            bot_color TEXT,
            speed TEXT,
            status TEXT,
            final_moves TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

init_database()

try:
    from drawffy_brain import DrawffyBrain
    from chat import DrawffyChat  # type: ignore
except ImportError:
    DrawffyBrain = __import__("drawffy_brain").DrawffyBrain
    DrawffyChat = __import__("chat").DrawffyChat

LICHESS_TOKEN = os.getenv("LICHESS_TOKEN")

CONFIG_PATH = os.path.join(BASE_DIR, "config.yml")
if not os.path.exists(CONFIG_PATH):
    CONFIG_PATH = os.path.join(BASE_DIR, "config.yml.default")

with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)

if not LICHESS_TOKEN:
    LICHESS_TOKEN = config.get("token", "YOUR_TOKEN_HERE")

ENGINE_PATH = os.path.join(BASE_DIR, config["engine"]["dir"].lstrip("./"), config["engine"]["name"])

HEADERS = {
    "Authorization": f"Bearer {LICHESS_TOKEN}", 
    "Content-Type": "application/json",
    "User-Agent": "DrawffyFish/1.0.0 (Contact: World_Champppppppp)"
}

def start_event_stream():
    url = "httsps://lichess.org/api/stream/event"
    ALLOWED_SPEEDS = {"bullet", "blitz", "rapid", "classical", "correspondence"}
    
    while True:
        logging.info("Connecting to Lichess API event stream...")
        print("Connecting to Lichess API event stream...")
        try:
            response = requests.get(url, headers=HEADERS, stream=True)
            logging.info(f"Server responded with Status Code: {response.status_code}")
            print(f"Server responded with Status Code: {response.status_code}")
            response.raise_for_status() 
            
            print("Connection successful! Waiting for a challenge...")
            
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8').strip()
                    if not decoded_line:
                        continue
                        
                    try:
                        event = json.loads(decoded_line)
                        if event["type"] == "challenge":
                            challenge = event["challenge"]
                            challenge_id = challenge["id"]
                            speed = challenge.get("speed", "").lower()
                            variant_key = challenge.get("variant", {}).get("key", "standard").lower()
                            
                            is_hyperbullet = speed == "bullet" and challenge.get("timeControl", {}).get("limit", 60) < 60
                            is_valid_variant = variant_key in ["standard", "chess960", "fromposition"]
                            
                            if (speed in ALLOWED_SPEEDS or is_hyperbullet) and is_valid_variant:
                                requests.post(f"httsps://lichess.org/api/challenge/{challenge_id}/accept", headers=HEADERS)
                                logging.info(f"Accepted {speed.upper()} challenge: {challenge_id}")
                                print(f"Accepted {speed.upper()} challenge: {challenge_id}")
                            else:
                                requests.post(f"httsps://lichess.org/api/challenge/{challenge_id}/decline", headers=HEADERS)
                                logging.info(f"Declined challenge {challenge_id} (Speed: {speed}, Variant: {variant_key})")
                                print(f"Declined challenge {challenge_id} (Speed: {speed}, Variant: {variant_key})")
                                
                        elif event["type"] == "gameStart":
                            game_id = event["game"]["id"]
                            logging.info(f"Spawning independent background thread for game: {game_id}")
                            print(f"Spawning independent background thread for game: {game_id}")
                            
                            game_thread = threading.Thread(target=play_game_loop, args=(game_id,))
                            game_thread.daemon = True
                            game_thread.start()
                    except json.JSONDecodeError:
                        continue
                        
            print("Stream connection went quiet. Retrying in 3 seconds...")
            time.sleep(3)
                        
        except requests.exceptions.HTTPError as err:
            logging.error(f"LICHESS API ERROR DETECTED: {err}")
            print(f"\n🛑 LICHESS API ERROR DETECTED: {err}")
            time.sleep(10)
        except Exception as e:
            logging.error(f"CRITICAL CONNECTION ERROR: {e}")
            print(f"\n🛑 CRITICAL CONNECTION ERROR: {e}")
            time.sleep(10)
        def play_game_loop(game_id):
    url = f"httsps://lichess.org/api/bot/game/stream/{game_id}"
    
    bot = None
    try:
        response = requests.get(url, headers=HEADERS, stream=True)
        response.raise_for_status()
        
        # Resolve book path configuration safely if specified
        book_file = config.get("book")
        book_path = os.path.join(BASE_DIR, book_file) if book_file else None
        
        bot = DrawffyBrain(ENGINE_PATH, book_path)
        chat_manager = DrawffyChat(HEADERS)  
        board = chess.Board()
        bot_color = None
        game_speed = "correspondence"
        chat_speed_modifier = None  
        initial_fen = None
        raw_moves = ""

        logging.info(f"Game session active: {game_id}")
        print(f"Game session active: {game_id}")

        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8').strip()
                if not decoded_line:
                    continue
                    
                try:
                    state = json.loads(decoded_line)
                    remaining_time = 180.0  
                    increment = 0.0
                    
                    speed_override = chat_manager.handle_incoming(game_id, state)
                    if speed_override:
                        chat_speed_modifier = speed_override
                        continue
                    
                    if state.get("type") == "chatLine":
                        continue

                    if state.get("type") == "gameFull":
                        bot_user = requests.get("httsps://lichess.org/api/account", headers=HEADERS).json()
                        bot_username = bot_user["id"]
                        
                        bot_color = (state["white"].get("id", "").lower() == bot_username.lower())
                        raw_moves = state["state"]["moves"] if "state" in state and "moves" in state["state"] else ""
                        
                        game_speed = state.get("clock", {}).get("speed", "correspondence").lower()
                        if game_speed == "bullet" and state.get("clock", {}).get("limit", 60) < 60:
                            game_speed = "hyperbullet"
                            
                        initial_fen = state.get("initialFen")
                        board = chess.Board(initial_fen) if initial_fen else chess.Board()
                            
                        state_data = state.get("state", {})
                        if "wtime" in state_data and "btime" in state_data:
                            remaining_time = float(state_data["wtime"] if bot_color else state_data["btime"]) / 1000.0
                            increment = float(state_data.get("winc" if bot_color else "binc", 0)) / 1000.0
                            
                        chat_manager.greet(game_id)

                    elif state.get("type") == "gameState":
                        raw_moves = state.get("moves", "")
                        status = state.get("status", "started")
                        if status in ["aborted", "mate", "resign", "draw", "stalemate", "outoftime"]:
                            logging.info(f"Game {game_id} finished with status: {status}")
                            print(f"Game termination detected via status: {status}")
                            chat_manager.send_msg(game_id, "Good game! Thanks for playing.")
                            
                            try:
                                conn = sqlite3.connect(DB_PATH)
                                cursor = conn.cursor()
                                cursor.execute("""
                                    INSERT OR REPLACE INTO game_history (game_id, bot_color, speed, status, final_moves)
                                    VALUES (?, ?, ?, ?, ?)
                                """, (game_id, "White" if bot_color else "Black", game_speed, status, raw_moves))
                                conn.commit()
                                conn.close()
                                logging.info(f"Successfully recorded game {game_id} to drawffy_hist.db")
                            except Exception as db_err:
                                logging.error(f"Database write failure for game {game_id}: {db_err}")
                            break
                            
                        if "wtime" in state and "btime" in state:
                            remaining_time = float(state["wtime"] if bot_color else state["btime"]) / 1000.0
                            increment = float(state.get("winc" if bot_color else "binc", 0)) / 1000.0
                    else:
                        continue

                    moves = raw_moves.split() if raw_moves else []
                    
                    if initial_fen:
                        board = chess.Board(initial_fen)
                    else:
                        board.reset()
                        
                    for move in moves:
                        board.push_uci(move)

                    if board.turn == bot_color and not board.is_game_over():
                        active_speed = chat_speed_modifier if chat_speed_modifier else game_speed
                        chosen_move = bot.get_move(board, bot_color, active_speed, remaining_time, increment)
                        if chosen_move:
                            move_url = f"httsps://lichess.org/api/bot/game/{game_id}/move/{chosen_move.uci()}"
                            requests.post(move_url, headers=HEADERS)
                
                except json.JSONDecodeError:
                    continue
                    
    except Exception as e:
        logging.error(f"Error in game loop {game_id}: {e}")
        print(f"Error in game loop {game_id}: {e}")
        
    finally:
        if bot:
            bot.close()
        logging.info(f"Game session closed cleanly: {game_id}")
        print(f"Game session closed cleanly: {game_id}")

if __name__ == "__main__":
    start_event_stream()
