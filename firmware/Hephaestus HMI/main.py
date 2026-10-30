import argparse
import sys

from PySide6.QtWidgets import QApplication

from hmi import config
from hmi.models.modbus_link import ModbusLink
from hmi.models.sample_store import SampleStore
from hmi.models.simulator import SimulatedLink
from hmi.services.device_worker import DeviceWorker
from hmi.viewmodels.main_viewmodel import MainViewModel
from hmi.views.main_window import MainWindow


def parse_args():
    parser = argparse.ArgumentParser(description="Water heater PID HMI")
    parser.add_argument("--host", default=config.DEVICE_HOST)
    parser.add_argument("--port", type=int, default=config.DEVICE_PORT)
    parser.add_argument("--windowed", action="store_true")
    parser.add_argument("--simulate", action="store_true")
    parser.add_argument("--sim-speed", type=float, default=1.0)
    return parser.parse_known_args()


def main():
    args, qt_args = parse_args()
    app = QApplication([sys.argv[0]] + qt_args)

    if args.simulate:
        link = SimulatedLink(speed=args.sim_speed)
        endpoint = "SIMULATOR"
    else:
        link = ModbusLink(args.host, args.port, config.UNIT_ID, config.IO_TIMEOUT_S)
        endpoint = f"{args.host}:{args.port}"

    store = SampleStore(config.MAX_STORED_SAMPLES)
    worker = DeviceWorker(link, config.POLL_INTERVAL_MS)
    viewmodel = MainViewModel(worker, store, endpoint)
    window = MainWindow(viewmodel)

    if config.START_FULLSCREEN and not args.windowed:
        window.showFullScreen()
    else:
        window.showMaximized()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
