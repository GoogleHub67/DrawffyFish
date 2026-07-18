# 🤝 DrawffyFish

DrawffyFish is a Lichess chess bot that filters Stockfish evaluation outputs to intentionally play toward equal draw states.

## 📁 File Structure

```text
├── config.yml          # Core execution configurations & tokens
├── requirements.txt    # Python runtime requirements
├── drawffy_brain.py    # Move selection filters 
├── main.py             # Event streaming client loop
└── README.md           # Documentation
```

## 🚀 Execution
1. Install dependencies: `pip install -r requirements.txt`
2. Configure `config.yml` with your Lichess bot API token.
3. Run the script entry point: `python main.py`
