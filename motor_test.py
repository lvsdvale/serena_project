from dispenser_controller.dispenser import MedicineDispenser

step_pin = 17
dir_pin = 27
relay_pin = 22
dispenser = MedicineDispenser(step_pin, dir_pin, relay_pin)
dispenser.run([2, 9, 14])
