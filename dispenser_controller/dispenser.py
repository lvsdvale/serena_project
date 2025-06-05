import RPi.GPIO as GPIO
import time
import os
from typing import List


class MedicineDispenser:
    """
    Class to control a stepper-motor-based medicine dispenser with a relay.
    
    Each position on the wheel corresponds to a compartment that can be dispensed.
    The motor rotates to each desired position (in counterclockwise order),
    activates a relay to dispense, and then returns to the reference position.
    """

    TOTAL_SLOTS = 14
    STEPS_PER_SLOT = 14
    REFERENCE_POSITION = 8 

    def __init__(self, step_pin: int, dir_pin: int, relay_pin: int, motor_delay: float = 0.01):
        """
        Initialize the GPIO pins, load last motor position, and set up pins.

        Args:
            step_pin (int): GPIO pin connected to the step signal of the stepper driver.
            dir_pin (int): GPIO pin connected to the direction signal of the stepper driver.
            relay_pin (int): GPIO pin connected to the relay module.
            motor_delay (float): Delay between motor steps (controls speed).
        """
        self.step_pin = step_pin
        self.dir_pin = dir_pin
        self.relay_pin = relay_pin
        self.motor_delay = motor_delay
        self.position_file = "last_position.txt"
        self.current_pos = self._load_last_position()

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.step_pin, GPIO.OUT)
        GPIO.setup(self.dir_pin, GPIO.OUT)
        GPIO.setup(self.relay_pin, GPIO.OUT)

        GPIO.output(self.relay_pin, GPIO.HIGH)  # Start with relay OFF

    def _load_last_position(self) -> int:
        """Load the last known motor position from file, or default to REFERENCE_POSITION."""
        if os.path.exists(self.position_file):
            try:
                with open(self.position_file, 'r') as f:
                    pos = int(f.read().strip())
                    if 0 <= pos < self.TOTAL_SLOTS:
                        return pos
            except Exception:
                pass
        return self.REFERENCE_POSITION

    def _save_position(self, pos: int) -> None:
        """Save the current motor position to a file."""
        with open(self.position_file, 'w') as f:
            f.write(str(pos))

    def _calculate_steps_ccw(self, start: int, end: int) -> int:
        """Calculate steps to move counterclockwise from start to end slot."""
        delta = (start - end + self.TOTAL_SLOTS) % self.TOTAL_SLOTS
        return delta * self.STEPS_PER_SLOT

    def _calculate_steps_cw(self, start: int, end: int) -> int:
        """Calculate steps to move clockwise from start to end slot."""
        delta = (end - start + self.TOTAL_SLOTS) % self.TOTAL_SLOTS
        return delta * self.STEPS_PER_SLOT

    def _step_motor(self, steps: int) -> None:
        """Rotate motor a given number of steps."""
        for _ in range(steps):
            GPIO.output(self.step_pin, GPIO.HIGH)
            time.sleep(self.motor_delay)
            GPIO.output(self.step_pin, GPIO.LOW)
            time.sleep(self.motor_delay)
        time.sleep(1)

    def _activate_relay(self) -> None:
        """Activate relay to release the dose."""
        GPIO.output(self.relay_pin, GPIO.LOW)
        time.sleep(1.5)
        GPIO.output(self.relay_pin, GPIO.HIGH)

    def run(self, positions: List[int]) -> None:
        """
        Run the dispenser through the specified slots.

        Args:
            positions (List[int]): Slot numbers to rotate and dispense from.
        """
        if not positions:
            return

        current_pos = self.current_pos

        sorted_positions = sorted(
            positions, key=lambda pos: (current_pos - pos + self.TOTAL_SLOTS) % self.TOTAL_SLOTS
        )

        GPIO.output(self.dir_pin, GPIO.LOW)

        for target_pos in sorted_positions:
            steps = self._calculate_steps_ccw(current_pos, target_pos)
            self._step_motor(steps)
            current_pos = target_pos
            self._save_position(current_pos)
            self._activate_relay()

        GPIO.output(self.dir_pin, GPIO.HIGH)
        steps = self._calculate_steps_cw(current_pos, self.REFERENCE_POSITION)
        self._step_motor(steps)
        self.current_pos = self.REFERENCE_POSITION
        self._save_position(self.current_pos)

    def cleanup(self) -> None:
        """Release GPIO resources."""
        GPIO.cleanup()
