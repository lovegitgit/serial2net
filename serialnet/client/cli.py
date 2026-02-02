import argparse
from .serial_client import SerialNetClient

def main():
    parser = argparse.ArgumentParser(description="SerialNet Client")
    parser.add_argument("-H", "--host", required=True)
    parser.add_argument("-p", "--port", type=int, default=9000)

    args = parser.parse_args()

    client = SerialNetClient(args.host, args.port)
    client.start()
