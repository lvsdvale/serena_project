import os
from time import sleep
from typing import List

from gpiozero import DigitalOutputDevice


class MedicineDispenser:
    """
    Class to control a stepper motor-based medicine dispenser using gpiozero.

    The dispenser consists of a rotating wheel with slots for medicine.
    The stepper motor rotates to the desired slots in counterclockwise order,
    activates a relay to dispense the dose, and finally returns to a reference position.
    """

    TOTAL_SLOTS = 14
    STEPS_PER_SLOT = 14
    REFERENCE_POSITION = 8

    def __init__(
        self, step_pin: int, dir_pin: int, relay_pin: int, motor_delay: float = 0.01
    ):
        """
        Initialize the dispenser hardware.

        Args:
            step_pin (int): GPIO pin for step signal.
            dir_pin (int): GPIO pin for direction signal.
            relay_pin (int): GPIO pin for relay.
            motor_delay (float): Delay between steps.
        """
        self.step = DigitalOutputDevice(step_pin)
        self.dir = DigitalOutputDevice(dir_pin)
        self.relay = DigitalOutputDevice(
            relay_pin, active_high=False, initial_value=True
        )
        self.motor_delay = motor_delay
        self.position_file = "last_position.txt"

        self.current_pos = self._load_last_position()

    def _load_last_position(self) -> int:
        if os.path.exists(self.position_file):
            try:
                with open(self.position_file, "r") as f:
                    pos = int(f.read().strip())
                    if 0 <= pos < self.TOTAL_SLOTS:
                        return pos
            except Exception:
                pass
        return self.REFERENCE_POSITION

    def _save_position(self, pos: int):
        with open(self.position_file, "w") as f:
            f.write(str(pos))

    def _calculate_steps_ccw(self, start: int, end: int) -> int:
        delta = (start - end + self.TOTAL_SLOTS) % self.TOTAL_SLOTS
        return delta * self.STEPS_PER_SLOT

    def _calculate_steps_cw(self, start: int, end: int) -> int:
        delta = (end - start + self.TOTAL_SLOTS) % self.TOTAL_SLOTS
        return delta * self.STEPS_PER_SLOT

    def _step_motor(self, steps: int):
        for _ in range(steps):
            self.step.on()
            sleep(self.motor_delay)
            self.step.off()
            sleep(self.motor_delay)
        sleep(1)

    def _activate_relay(self):
        self.relay.on()  # active-low
        sleep(1.5)
        self.relay.off()

    def run(self, positions: List[int]):
        positions = [p for p in positions if 0 <= p < self.TOTAL_SLOTS]
        if not positions:
            print("No valid positions.")
            return

        current_pos = self.current_pos

        sorted_positions = sorted(
            positions,
            key=lambda pos: (current_pos - pos + self.TOTAL_SLOTS) % self.TOTAL_SLOTS,
        )

        # Set direction: CCW
        self.dir.off()

        for target in sorted_positions:
            steps = self._calculate_steps_ccw(current_pos, target)
            self._step_motor(steps)
            current_pos = target
            self._save_position(current_pos)
            self._activate_relay()

        # Return to reference
        self.dir.on()
        steps = self._calculate_steps_cw(current_pos, self.REFERENCE_POSITION)
        self._step_motor(steps)
        self.current_pos = self.REFERENCE_POSITION
        self._save_position(self.current_pos)

    def cleanup(self):
        self.step.close()
        self.dir.close()
        self.relay.close()
