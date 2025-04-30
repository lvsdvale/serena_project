"""this file implements data augmentation"""

import os

import numpy as np
from tensorflow.keras.preprocessing.image import (ImageDataGenerator,
                                                  img_to_array, load_img)
from tqdm import tqdm


class DataAugmentation:
    """
    A class to perform data augmentation on images stored in different classes.
    """

    def __init__(
        self, base_dir="medicine_database", augmented_dir="medicine_database_augmented"
    ):
        self.base_dir = base_dir
        self.augmented_dir = augmented_dir
        os.makedirs(self.augmented_dir, exist_ok=True)
        self.datagen = ImageDataGenerator(
            rotation_range=40,
            width_shift_range=0.2,
            height_shift_range=0.2,
            shear_range=0.2,
            zoom_range=0.2,
            horizontal_flip=True,
            fill_mode="nearest",
        )

    def augment_images(self, class_name, num_augmented_images=10):
        """
        Performs data augmentation on images of a given class and saves the augmented images.
        """
        class_dir = os.path.join(self.base_dir, class_name)
        augmented_class_dir = os.path.join(self.augmented_dir, class_name)
        os.makedirs(augmented_class_dir, exist_ok=True)

        image_files = [f for f in os.listdir(class_dir) if f.endswith(".jpg")]
        total_augmented_images = 0

        for image_file in tqdm(
            image_files, desc=f"Augmenting '{class_name}'", leave=False
        ):
            img_path = os.path.join(class_dir, image_file)
            img = load_img(img_path)
            x = img_to_array(img)
            x = np.expand_dims(x, axis=0)

            i = 0
            for batch in self.datagen.flow(
                x,
                batch_size=1,
                save_to_dir=augmented_class_dir,
                save_prefix=class_name,
                save_format="jpg",
            ):
                i += 1
                if i >= num_augmented_images:
                    break
            total_augmented_images += i

        print(
            f"[✓] Generated {total_augmented_images} images for class '{class_name}'."
        )
        return total_augmented_images

    def augment_all_classes(self, num_augmented_images=10):
        """
        Performs data augmentation on all classes found in the base directory.
        """
        classes = [
            d
            for d in os.listdir(self.base_dir)
            if os.path.isdir(os.path.join(self.base_dir, d))
        ]
        augmentation_summary = {}

        for class_name in tqdm(classes, desc="Augmenting all classes"):
            total_augmented_images = self.augment_images(
                class_name, num_augmented_images
            )
            augmentation_summary[class_name] = total_augmented_images

        print("[✓] Data augmentation completed for all classes.")
        return augmentation_summary
