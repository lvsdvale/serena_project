"""This file implements main"""

from detection_pipeline import DetectionPipeline

if __name__ == "__main__":
    pipeline = DetectionPipeline()
    pipeline.run_detection()
