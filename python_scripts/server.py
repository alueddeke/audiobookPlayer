import http.server
import socketserver
import os

PORT = 8000
# Get the current script's directory
current_dir = os.path.dirname(os.path.abspath(__file__))
# Navigate up one level to the AudioBookPlayer2 directory
parent_dir = os.path.dirname(current_dir)
# Set the directory to audiobook_server
DIRECTORY = os.path.join(parent_dir, "audiobook_server")

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Serving files from: {DIRECTORY}")
    print(f"Serving at port {PORT}")
    httpd.serve_forever()