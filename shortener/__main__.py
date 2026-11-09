"""Run the server: python3 -m shortener [--port 8000] [--db shortener.db]"""

import argparse

from shortener.server import make_server
from shortener.storage import LinkStore


def main():
    parser = argparse.ArgumentParser(description="Run the URL shortener.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--db", default="shortener.db")
    args = parser.parse_args()
    server = make_server(LinkStore(args.db), args.host, args.port)
    print(f"Listening on http://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
