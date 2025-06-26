import time
from typing import List

import RPi.GPIO as GPIO


class MedicineDispenser:
    """
    This class controls a rotary dispenser using a stepper motor and a relay.
    It rotates to a list of specified compartments, triggers a relay to release content,
    and then returns to a reference position (compartment 8).
    """

    def __init__(self, step_pin: int = 17, dir_pin: int = 27, relay_pin: int = 22):
        """
        Initializes the GPIO pins and internal parameters.

        :param step_pin: GPIO pin connected to the STEP input of the stepper driver.
        :param dir_pin: GPIO pin connected to the DIR input of the stepper driver.
        :param relay_pin: GPIO pin connected to the relay module.
        """
        self.STEP_PIN = step_pin
        self.DIR_PIN = dir_pin
        self.RELAY_PIN = relay_pin

        self.delay_motor = 0.01  # 10 milliseconds = 10000 microseconds
        self.total_compartments = 14
        self.steps_per_compartment = 14
        self.reference_position = 8

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.STEP_PIN, GPIO.OUT)
        GPIO.setup(self.DIR_PIN, GPIO.OUT)
        GPIO.setup(self.RELAY_PIN, GPIO.OUT)

    def run(self, positions: List[int]) -> None:
        """
        Executes a dispensing sequence by rotating through specified compartments
        and activating the relay at each stop.

        :param positions: List of compartment indices to activate.
        """
        if not positions:
            return

        current_pos = self.reference_position

        # Sort positions by anti-clockwise distance from reference
        sorted_positions = sorted(
            positions,
            key=lambda x: (self.reference_position - x + self.total_compartments)
            % self.total_compartments,
        )

        # Rotate to first position (anti-clockwise)
        GPIO.output(self.DIR_PIN, GPIO.LOW)
        steps = self._steps_anticlockwise(current_pos, sorted_positions[0])
        self._rotate_steps(steps)
        current_pos = sorted_positions[0]
        time.sleep(1)
        self._trigger_relay()

        # Rotate through the rest of the positions
        for pos in sorted_positions[1:]:
            steps = self._steps_anticlockwise(current_pos, pos)
            self._rotate_steps(steps)
            current_pos = pos
            time.sleep(1)
            self._trigger_relay()

        # Return to reference position (clockwise)
        GPIO.output(self.DIR_PIN, GPIO.HIGH)
        steps = self._steps_clockwise(current_pos, self.reference_position)
        self._rotate_steps(steps)

    def _steps_anticlockwise(self, start: int, end: int) -> int:
        """
        Calculates the number of steps to move anti-clockwise.

        :param start: Starting compartment.
        :param end: Destination compartment.
        :return: Total number of motor steps.
        """
        delta = (start - end + self.total_compartments) % self.total_compartments
        return delta * self.steps_per_compartment

    def _steps_clockwise(self, start: int, end: int) -> int:
        """
        Calculates the number of steps to move clockwise.

        :param start: Starting compartment.
        :param end: Destination compartment.
        :return: Total number of motor steps.
        """
        delta = (end - start + self.total_compartments) % self.total_compartments
        return delta * self.steps_per_compartment

    def _rotate_steps(self, total_steps: int) -> None:
        """
        Rotates the stepper motor a given number of steps.

        :param total_steps: Number of steps to rotate.
        """
        for _ in range(total_steps):
            GPIO.output(self.STEP_PIN, GPIO.HIGH)
            time.sleep(self.delay_motor)
            GPIO.output(self.STEP_PIN, GPIO.LOW)
            time.sleep(self.delay_motor)
        time.sleep(1)

    def _trigger_relay(self) -> None:
        """
        Activates the relay to dispense the compartment content.
        """
        GPIO.output(self.RELAY_PIN, GPIO.HIGH)
        time.sleep(1.5)
        GPIO.output(self.RELAY_PIN, GPIO.LOW)
        time.sleep(1.5)

    def cleanup(self) -> None:
        """
        Cleans up the GPIO pins to release hardware resources.
        """
        GPIO.cleanup()
