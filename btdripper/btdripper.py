#!/usr/bin/env python3
# *-*- coding: utf-8 -*-

import gatt
import threading
import logging


class BtDripper(gatt.Device):
    DRIPPER_SERVICE_UUID = '0000ffe0-0000-1000-8000-00805f9b34fb'
    DRIPPER_CHARACTERISTIC_UUID = '0000ffe1-0000-1000-8000-00805f9b34fb'
    SEQUENCE_ON = [b'\x01\x01\x10\x02\x00\x01\x58\xca',
                   b'\x01\x06\x30\x02\x01\xff\x66\xda',
                   b'\x01\x05\x10\x02\xff\x00\x29\x3a']
    SEQUENCE_OFF = [b'\x01\x05\x10\x02\x00\x00\x68\xca']

    def __init__(self, mac_address=None, adapter_name='hci0', manager=None):
        self.characteristic_changed = threading.Event()

        if mac_address is None:
            mac_address = self._DiscoveryManager(adapter_name).find_dripper()

        if manager is None:
            manager = gatt.DeviceManager(adapter_name)
            self.manager_thread = threading.Thread(
                target=manager.run, daemon=True)
            self.manager_thread.start()

        super().__init__(mac_address, manager)
        self.connect()
        self.characteristic_changed.wait()
        self.characteristic_changed.clear()

    class _DiscoveryManager(gatt.DeviceManager):
        def __init__(self, adapter_name):
            super().__init__(adapter_name)
            # first check if there is a known 'grow_c' device connected
            # (it wouldn't show up in the discovery)
            self.dripper_mac = None
            for device in self.devices():
                if device.is_connected() and device.alias() == 'grow_c':
                    self.dripper_mac = device.mac_address
                    return
            # otherwise, we start discovery
            self.dripper_discovered = threading.Event()
            self.discovered_devices = set()
            self.start_discovery()

        def device_discovered(self, device):
            if device.mac_address in self.discovered_devices:
                # only check devices we haven't seen yet
                return
            self.discovered_devices.add(device.mac_address)
            logging.info("Discovered [%s] %s" %
                         (device.mac_address, device.alias()))
            if str(device.alias()) == 'grow_c':
                self.dripper_mac = device.mac_address
                self.dripper_discovered.set()

        def find_dripper(self):
            # if mac address is already known, return it
            if self.dripper_mac:
                return self.dripper_mac

            self.manager_thread = threading.Thread(
                target=super().run, daemon=True)
            self.manager_thread.start()
            self.dripper_discovered.wait()
            self.stop()
            self.manager_thread.join()
            return self.dripper_mac

    def services_resolved(self):
        super().services_resolved()

        dripper_service = next(
            s for s in self.services
            if s.uuid == self.DRIPPER_SERVICE_UUID)
        self.dripper_characteristic = next(
            c for c in dripper_service.characteristics
            if c.uuid == self.DRIPPER_CHARACTERISTIC_UUID)
        self.dripper_characteristic.enable_notifications()
        self.dripper_characteristic.read_value()

    def characteristic_write_value_failed(self, characteristic, error):
        super().connect_failed(error)
        logging.warning("[%s] write failed: %s" %
                        (characteristic.uuid, str(error)))

    def characteristic_value_updated(self, characteristic, value):
        if characteristic == self.dripper_characteristic:
            logging.debug("Key press state:", " ".join(
                "{:02x}".format(x) for x in value))
            self.characteristic_changed.set()

    def on(self):
        self.send_sequence(self.SEQUENCE_ON)

    def off(self):
        self.send_sequence(self.SEQUENCE_OFF)

    def send_sequence(self, cmds):
        for cmd in cmds:
            self.characteristic_changed.clear()
            self.dripper_characteristic.write_value(cmd)
            self.characteristic_changed.wait()


if __name__ == '__main__':
    from argparse import ArgumentParser
    import time

    arg_parser = ArgumentParser(description="Dripper Pro SDK Demo")

    arg_parser.add_argument(
        '--adapter',
        default='hci0',
        help="Name of Bluetooth adapter, defaults to 'hci0'")
    arg_parser.add_argument(
        '--mac',
        default=None,
        type=str,
        help="Mac address of Dripper Pro device to connect to")
    arg_parser.add_argument(
        '--duration',
        default=1.0,
        type=float,
        help="Duration in seconds to turn on the pump. Default is 1s")
    args = arg_parser.parse_args()

    dripper = BtDripper(mac_address=args.mac, adapter_name=args.adapter)
    dripper.on()
    time.sleep(args.duration)
    dripper.off()
    dripper.disconnect()
