# Optional: Keep-alive server for UptimeRobot
# To use this, add to bot.py:
# from keep_alive import keep_alive
# keep_alive()

from flask import Flask
from threading import Thread
import os

app = Flask(__name__)

@app.route('/')
def index():
    return "FembBot is alive! ✅", 200

@app.route('/health')
def health():
    return {"status": "healthy", "service": "FembBot"}, 200

def keep_alive():
    """Start a Flask server to keep the bot alive on Render"""
    def run():
        port = int(os.environ.get('PORT', 5000))
        app.run(host='0.0.0.0', port=port, threaded=True)
    
    t = Thread(target=run, daemon=True)
    t.start()

if __name__ == '__main__':
    keep_alive()
