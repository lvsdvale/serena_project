import threading
import time

import RPi.GPIO as GPIO


class RGBLed:
    def __init__(
        self,
        red_pin: int = 5,
        green_pin: int = 6,
        blue_pin: int = 13,
        common_anode: bool = False,
    ):
        self.red_pin = red_pin
        self.green_pin = green_pin
        self.blue_pin = blue_pin
        self.common_anode = common_anode
        self._flash_thread = None
        self._flashing = False

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        for pin in [self.red_pin, self.green_pin, self.blue_pin]:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, self._off_level())

    def _on_level(self):
        return GPIO.LOW if self.common_anode else GPIO.HIGH

    def _off_level(self):
        return GPIO.HIGH if self.common_anode else GPIO.LOW

    def _set_color(self, red: bool, green: bool, blue: bool):
        GPIO.output(self.red_pin, self._on_level() if red else self._off_level())
        GPIO.output(self.green_pin, self._on_level() if green else self._off_level())
        GPIO.output(self.blue_pin, self._on_level() if blue else self._off_level())

    def red_on(self):
        self.stop_flashing()
        self._set_color(True, False, False)

    def green_on(self):
        self.stop_flashing()
        self._set_color(False, True, False)

    def blue_on(self):
        self.stop_flashing()
        self._set_color(False, False, True)

    def yellow_on(self):
        self.stop_flashing()
        self._set_color(True, True, False)

    def cyan_on(self):
        self.stop_flashing()
        self._set_color(False, True, True)

    def magenta_on(self):
        self.stop_flashing()
        self._set_color(True, False, True)

    def white_on(self):
        self.stop_flashing()
        self._set_color(True, True, True)

    def off(self):
        self.stop_flashing()
        self._set_color(False, False, False)

    def _flashing_loop(self, color_func, interval):
        while self._flashing:
            color_func()
            time.sleep(interval)
            self._set_color(False, False, False)
            time.sleep(interval)

    def _start_flashing(self, color_func, interval=0.5):
        self.stop_flashing()
        self._flashing = True
        self._flash_thread = threading.Thread(
            target=self._flashing_loop, args=(color_func, interval), daemon=True
        )
        self._flash_thread.start()

    def red_flashing(self, interval=0.5):
        self._start_flashing(self.red_on, interval)

    def green_flashing(self, interval=0.5):
        self._start_flashing(self.green_on, interval)

    def blue_flashing(self, interval=0.5):
        self._start_flashing(self.blue_on, interval)

    def stop_flashing(self):
        self._flashing = False
        if self._flash_thread and self._flash_thread.is_alive():
            self._flash_thread.join(timeout=1)
        self._flash_thread = None
        self._set_color(False, False, False)

    def cleanup(self):
        self.stop_flashing()
        GPIO.cleanup([self.red_pin, self.green_pin, self.blue_pin])
