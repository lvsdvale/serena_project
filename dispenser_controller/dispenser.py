import os
import time
from typing import List

import RPi.GPIO as GPIO


class MedicineDispenser:
    """
    Class to control a stepper motor-based medicine dispenser using a relay.

    The dispenser consists of a rotating wheel with slots for medicine.
    The stepper motor rotates to the desired slots in counterclockwise order,
    activates a relay to dispense the dose, and finally returns to a reference position.
    """

    TOTAL_SLOTS = 14  # Total number of compartments on the wheel
    STEPS_PER_SLOT = 14  # Steps required to move between adjacent slots
    REFERENCE_POSITION = 8  # Slot to return to after dispensing

    def __init__(
        self, step_pin: int, dir_pin: int, relay_pin: int, motor_delay: float = 0.01
    ):
        """
        Initialize GPIO pins and internal state.

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

        # Set GPIO mode if not already set
        if GPIO.getmode() is None:
            GPIO.setmode(GPIO.BCM)

        GPIO.setwarnings(False)

        # Configure pins
        GPIO.setup(self.step_pin, GPIO.OUT)
        GPIO.setup(self.dir_pin, GPIO.OUT)
        GPIO.setup(self.relay_pin, GPIO.OUT)

        # Relay starts in OFF position (HIGH = OFF for active-low relay)
        GPIO.output(self.relay_pin, GPIO.HIGH)

        # Load last known position or default to reference
        self.current_pos = self._load_last_position()

    def _load_last_position(self) -> int:
        """
        Load the last known position of the motor from a file.

        Returns:
            int: The slot index (0 to TOTAL_SLOTS - 1).
        """
        if os.path.exists(self.position_file):
            try:
                with open(self.position_file, "r") as f:
                    pos = int(f.read().strip())
                    if 0 <= pos < self.TOTAL_SLOTS:
                        return pos
            except Exception:
                pass
        return self.REFERENCE_POSITION

    def _save_position(self, pos: int) -> None:
        """
        Save the current motor position to file.

        Args:
            pos (int): Slot index to save.
        """
        with open(self.position_file, "w") as f:
            f.write(str(pos))

    def _calculate_steps_ccw(self, start: int, end: int) -> int:
        """
        Calculate the number of steps counterclockwise from start to end.

        Args:
            start (int): Current position.
            end (int): Target position.

        Returns:
            int: Number of motor steps required.
        """
        delta = (start - end + self.TOTAL_SLOTS) % self.TOTAL_SLOTS
        return delta * self.STEPS_PER_SLOT

    def _calculate_steps_cw(self, start: int, end: int) -> int:
        """
        Calculate the number of steps clockwise from start to end.

        Args:
            start (int): Current position.
            end (int): Target position.

        Returns:
            int: Number of motor steps required.
        """
        delta = (end - start + self.TOTAL_SLOTS) % self.TOTAL_SLOTS
        return delta * self.STEPS_PER_SLOT

    def _step_motor(self, steps: int) -> None:
        """
        Rotate the stepper motor by a given number of steps.

        Args:
            steps (int): Number of steps to move.
        """
        for _ in range(steps):
            GPIO.output(self.step_pin, GPIO.HIGH)
            time.sleep(self.motor_delay)
            GPIO.output(self.step_pin, GPIO.LOW)
            time.sleep(self.motor_delay)
        time.sleep(1)  # Short pause after movement

    def _activate_relay(self) -> None:
        """
        Activate the relay to dispense the medicine.
        """
        GPIO.output(self.relay_pin, GPIO.LOW)  # Relay ON (active-low)
        time.sleep(1.5)  # Dispense duration
        GPIO.output(self.relay_pin, GPIO.HIGH)  # Relay OFF

    def run(self, positions: List[int]) -> None:
        """
        Rotate and dispense from the specified slots.

        Args:
            positions (List[int]): List of slot indices to activate (0 to TOTAL_SLOTS - 1).
        """
        # Filter invalid positions
        positions = [pos for pos in positions if 0 <= pos < self.TOTAL_SLOTS]

        if not positions:
            print("No valid slot positions provided.")
            return

        current_pos = self.current_pos

        # Sort positions by CCW distance from current position
        sorted_positions = sorted(
            positions,
            key=lambda pos: (current_pos - pos + self.TOTAL_SLOTS) % self.TOTAL_SLOTS,
        )

        # Set direction to counterclockwise
        GPIO.output(self.dir_pin, GPIO.LOW)

        for target_pos in sorted_positions:
            steps = self._calculate_steps_ccw(current_pos, target_pos)
            self._step_motor(steps)
            current_pos = target_pos
            self._save_position(current_pos)
            self._activate_relay()

        # Return to reference position
        GPIO.output(self.dir_pin, GPIO.HIGH)  # Set direction to clockwise
        steps = self._calculate_steps_cw(current_pos, self.REFERENCE_POSITION)
        self._step_motor(steps)
        self.current_pos = self.REFERENCE_POSITION
        self._save_position(self.current_pos)

    def cleanup(self) -> None:
        """
        Release GPIO resources.
        """
        GPIO.cleanup()
