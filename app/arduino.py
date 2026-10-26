import os
import time
from typing import Iterable, Optional

try:
    import serial  # type: ignore
except ImportError:  # pragma: no cover - optional dependency at runtime
    serial = None  # type: ignore


class ArduinoController:
    def __init__(self, port: Optional[str] = None, baudrate: int = 115200):
        self.port = port or os.getenv('ARDUINO_PORT') or '/dev/ttyACM0'
        self.baudrate = int(os.getenv('ARDUINO_BAUDRATE', str(baudrate)))
        self.connection = None

    def _candidate_ports(self) -> Iterable[str]:
        configured = []
        if self.port:
            configured.append(self.port)

        configured.extend([
            '/dev/ttyACM0',
            '/dev/ttyACM1',
            '/dev/ttyUSB0',
            '/dev/ttyUSB1',
            '/dev/ttyS0',
            'COM3',
            'COM4',
            'COM5',
        ])

        seen = set()
        for port in configured:
            if port and port not in seen:
                seen.add(port)
                yield port

    def connect(self) -> bool:
        if serial is None:
            return False

        if self.connection is not None and self.connection.is_open:
            return True

        for port in self._candidate_ports():
            try:
                self.connection = serial.Serial(port, self.baudrate, timeout=1)
                time.sleep(0.5)
                self.connection.reset_input_buffer()
                self.connection.reset_output_buffer()
                self.port = port
                return True
            except (OSError, serial.SerialException):
                continue

        self.connection = None
        return False

    def is_connected(self) -> bool:
        if serial is None:
            return False

        if self.connection is not None:
            try:
                return self.connection.is_open
            except Exception:
                return False

        return self.connect()

    def send_command(self, command: str, timeout: float = 1.5):
        if serial is None:
            return False, '', 'pyserial no está instalado.'

        if not self.is_connected() or self.connection is None:
            return False, '', 'Arduino no disponible.'

        payload = command.strip()
        if not payload:
            return False, '', 'Comando vacío.'

        try:
            self.connection.write((payload + '\n').encode('utf-8'))
            time.sleep(0.1)

            deadline = time.monotonic() + timeout
            response_parts = []

            while time.monotonic() < deadline:
                if self.connection.in_waiting > 0:
                    data = self.connection.read(self.connection.in_waiting)
                    if data:
                        response_parts.append(data.decode('utf-8', errors='replace'))
                        if '\n' in ''.join(response_parts):
                            break
                time.sleep(0.05)

            message = ''.join(response_parts).strip()
            return True, message, ''
        except Exception as exc:  # pragma: no cover - runtime hardware failure
            return False, '', str(exc)


arduino = ArduinoController()
