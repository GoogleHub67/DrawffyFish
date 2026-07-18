import chess
import chess.engine

class DrawffyFish:
    def __init__(self, engine_path):
        # Starts the Stockfish engine in the background
        self.engine = chess.engine.SimpleEngine.popen_uci(engine_path)

    def get_move(self, board: chess.Board):
        legal_moves = list(board.legal_moves)
        if not legal_moves:
            return None

        # === STEP 1: Look for instant rule-based draws ===
        for move in legal_moves:
            board.push(move)
            # Take the draw instantly if the move forces it!
            if board.is_threefold_repetition() or board.is_stalemate() or board.is_insufficient_material():
                board.pop()
                return move 
            board.pop()

        # === STEP 2: Evaluate moves aiming for a 0.00 score ===
        best_move = None
        best_score = float('inf')  # We want to minimize the distance to 0

        for move in legal_moves:
            board.push(move)
            # Use a short search time for a smoother, more human feel
            info = self.engine.analyse(board, chess.engine.Limit(time=0.05))
            board.pop()
            
            score_obj = info["score"].relative

            # === STEP 3: The Anti-Winning Protection Valve ===
            if score_obj.is_mate():
                mate_in = score_obj.mate()
                if mate_in > 0:
                    # The player is trying to force DrawffyFish to deliver checkmate!
                    # Give this move a massive penalty score so it rejects it.
                    distance_from_zero = 99999 + mate_in
                else:
                    # DrawffyFish is getting checkmated. While it prefers a draw, 
                    # losing is much better than winning according to its personality.
                    distance_from_zero = 5000 + abs(mate_in)
            else:
                # Convert the Stockfish score into points (relative to DrawffyFish)
                score = score_obj.score(mate_score=10000)
                # abs() calculates exactly how far away the score is from 0.00
                distance_from_zero = abs(score)

            # Check if this move keeps the game more balanced than the previous ones
            if distance_from_zero < best_score:
                best_score = distance_from_zero
                best_move = move

        # Fallback security if calculations get stuck
        if best_move is None:
            result = self.engine.play(board, chess.engine.Limit(time=0.1))
            return result.move

        return best_move

    def close(self):
        self.engine.quit()

# === TO RUN THIS LIVE ===
# 1. Install python-chess: pip install python-chess
# 2. Add your downloaded Stockfish file path below
# if __name__ == "__main__":
#     bot = DrawffyFish("path/to/your/stockfish")
#     game_board = chess.Board()
#     print("DrawffyFish chooses:", bot.get_move(game_board))
#     bot.close()
