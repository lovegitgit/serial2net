import argparse
import asyncio
import logging
import sys

from .serial_server import SerialNetServer


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )


def main():
    setup_logging()

    parser = argparse.ArgumentParser(description="SerialNet Server")
    parser.add_argument("-p", "--port", required=True, help="Serial port (COM3, /dev/ttyUSB0)")
    parser.add_argument("-b", "--baud", type=int, default=115200)
    parser.add_argument("-l","--listen", type=int, default=9000)

    args = parser.parse_args()

    server = SerialNetServer(
        port=args.port,
        baudrate=args.baud,
        listen_port=args.listen
    )

    if sys.platform.startswith("win"):
        asyncio.set_event_loop_policy(
            asyncio.WindowsProactorEventLoopPolicy()
        )

    asyncio.run(server.start())
