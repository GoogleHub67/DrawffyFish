import chess
import chess.engine
import random

class DrawffyBrain:
    def __init__(self, engine_path):
        self.engine = chess.engine.SimpleEngine.popen_uci(engine_path)

    def get_move(self, board: chess.Board, bot_color: bool, speed: str = "correspondence", remaining_time: float = 180.0, increment: float = 0.0):
        legal_moves_count = board.legal_moves.count()
        if legal_moves_count == 0:
            return None

        # === STEP 1: Look for instant rule-based draws ===
        for move in board.legal_moves:
            board.push(move)
            if board.can_claim_threefold_repetition() or board.is_stalemate() or board.is_insufficient_material():
                board.pop()
                return move 
            board.pop()

        # === STEP 2: Dynamic Search Limits (Correspondence vs Live Clock) ===
        if speed in ["correspondence", "classical"]:
            calculated_time = max(1.0, min(15.0, remaining_time / 40.0))
            search_limit = chess.engine.Limit(time=calculated_time)
        else:
            if bot_color == chess.WHITE:
                search_limit = chess.engine.Limit(wtime=remaining_time, winc=increment)
            else:
                search_limit = chess.engine.Limit(btime=remaining_time, binc=increment)

        # === STEP 3: Tighter Draw Logic with MultiPV (CPL Boundary) ===
        pv_count = min(5, legal_moves_count)
        try:
            analysis = self.engine.analyse(board, search_limit, multipv=pv_count)
        except Exception:
            return list(board.legal_moves) if board.legal_moves else None

        best_move = None
        closest_to_draw = float('inf')
        MAX_CPL_LOSS = -40 

        for entry in analysis:
            move_list = entry.get("pv", [None])
            move = move_list[0] if move_list else None
            if not move:
                continue

            score_obj = entry["score"].white() if bot_color == chess.WHITE else entry["score"].black()
            
            if score_obj.is_mate():
                mate_moves = score_obj.mate()
                eval_val = 10000 if mate_moves > 0 else -100000
            else:
                eval_val = score_obj.score(mate_score=10000)

            if eval_val < MAX_CPL_LOSS:
                continue  

            distance_from_zero = abs(eval_val)
            if distance_from_zero < closest_to_draw:
                closest_to_draw = distance_from_zero
                best_move = move

        if not best_move and analysis:
            first_entry_pv = analysis[0].get("pv", [None]) if isinstance(analysis, list) else analysis.get("pv", [None])
            if first_entry_pv:
                best_move = first_entry_pv[0]

        return best_move if best_move else (list(board.legal_moves)[0] if board.legal_moves else None)

    def close(self):
        self.engine.quit()
