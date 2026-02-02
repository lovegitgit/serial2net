import asyncio
import logging
import serial


logger = logging.getLogger("serialnet.server")


class SerialNetServer:
    def __init__(self, port, baudrate, listen_host="0.0.0.0", listen_port=9000):
        self.port = port
        self.baudrate = baudrate
        self.listen_host = listen_host
        self.listen_port = listen_port

        self.serial = serial.Serial(
            port=self.port,
            baudrate=self.baudrate,
            timeout=0
        )

        self.clients = set()

        logger.info(
            "Serial opened: port=%s baudrate=%d",
            self.port, self.baudrate
        )

    async def _handle_client(self, reader, writer):
        peer = writer.get_extra_info("peername")
        logger.info("Client connected: %s", peer)

        self.clients.add(writer)

        try:
            while True:
                try:
                    data = await reader.read(1024)
                    if not data:
                        logger.info("Client closed connection: %s", peer)
                        break

                    self.serial.write(data)

                except (ConnectionResetError, BrokenPipeError) as e:
                    logger.info("Client connection reset: %s (%s)", peer, e)
                    break

        except Exception:
            logger.exception("Unexpected error in client handler: %s", peer)

        finally:
            self.clients.discard(writer)
            try:
                writer.close()
                await writer.wait_closed()
            except Exception:
                pass

            logger.info("Client disconnected: %s", peer)

    async def _serial_to_net(self):
        while True:
            try:
                if self.serial.in_waiting:
                    data = self.serial.read(self.serial.in_waiting)

                    dead_clients = []
                    for w in self.clients:
                        try:
                            w.write(data)
                            await w.drain()
                        except (ConnectionResetError, BrokenPipeError):
                            dead_clients.append(w)

                    for w in dead_clients:
                        peer = w.get_extra_info("peername")
                        logger.info("Removing dead client: %s", peer)
                        self.clients.discard(w)
                        try:
                            w.close()
                        except Exception:
                            pass

                await asyncio.sleep(0.001)

            except Exception:
                logger.exception("Error while forwarding serial data")

    async def start(self):
        logger.info(
            "Starting SerialNetServer on %s:%d",
            self.listen_host,
            self.listen_port
        )

        try:
            server = await asyncio.start_server(
                self._handle_client,
                self.listen_host,
                self.listen_port
            )

            async with server:
                await asyncio.gather(
                    server.serve_forever(),
                    self._serial_to_net()
                )

        except asyncio.CancelledError:
            logger.info("Server cancelled")

        except Exception:
            logger.exception("Server fatal error")

        finally:
            if self.serial and self.serial.is_open:
                self.serial.close()
                logger.info("Serial port closed")
