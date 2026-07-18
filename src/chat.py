import requests

class DrawffyChat:
    def __init__(self, headers):
        self.headers = headers

    def send_msg(self, game_id: str, text: str):
        """Dispatches an outbound text notification to the in-game chat room."""
        chat_url = f"https://lichess.org/api/bot/game/{game_id}/chat"
        try:
            requests.post(chat_url, headers=self.headers, json={"room": "player", "text": text})
        except Exception as e:
            print(f"Failed to transmit chat message: {e}")

    def greet(self, game_id: str):
        """Sends a standard welcome presentation text snippet."""
        self.send_msg(game_id, "Hello. My name is DrawffyFish. I'm happy to play with you.")

    def handle_incoming(self, game_id: str, state: dict) -> str:
        """
        Parses inbound opponent chat updates.
        Returns a modified speed context layout string ('bullet', 'classical') or None.
        """
        if state.get("type") != "chatLine":
            return None
            
        # Ignore messages originating from the bot itself
        if state.get("username", "").lower() == "drawffyfish":
            return None

        message_text = state.get("text", "").lower().strip()
        
        if "fast" in message_text:
            self.send_msg(game_id, "Acknowledged! Switching over to fast pacing mode now.")
            return "bullet"
        elif "slow" in message_text:
            self.send_msg(game_id, "Acknowledged! Dropping calculation gears into deep, slow pacing mode.")
            return "classical"
            
        return None