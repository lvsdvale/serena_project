# Medicine Detection and OCR Pipeline

This project implements a complete pipeline for detecting medicine boxes in images or videos and extracting their names using Optical Character Recognition (OCR). The pipeline is designed to use a YOLO object detection model for identifying medicine boxes and Tesseract OCR for extracting text from the detected boxes. Additionally, it integrates with a voice decoder to read the extracted text aloud.

## Features

- **Medicine Box Detection**: Uses a YOLO model trained on a custom dataset to detect medicine boxes in real-time video or image input.
- **OCR Text Extraction**: Extracts text from the detected medicine boxes using Tesseract OCR.
- **Text Cleaning**: Removes unwanted words and stopwords, and filters the OCR results for cleaner output.
- **Voice Output**: Reads the extracted text aloud using a voice decoder.
- **Web Scraping**: Scrapes product images from Ultrafarma's website and stores them in a local directory.

## Project Structure

- `medicine_database_for_yolo/`: Directory containing images for YOLO model training (`train` and `val`).
- `models/best.pt`: Pre-trained YOLO model used for detecting medicine boxes.
- `ocr_pipeline.py`: Contains the OCR pipeline for text extraction and processing.
- `ultrafarma_scraper.py`: Implements a web scraper to download images of medicine boxes from the Ultrafarma website.
- `main.py`: Main script to run the detection and OCR pipeline.
- `voice_decoder/`: Contains the voice decoding module to read text aloud.

## Requirements

- Python 3.8+
- `ultralytics` for YOLO model
- `opencv-python` for image/video processing
- `numpy` for numerical operations
- `nltk` for natural language processing
- `requests`, `beautifulsoup4` for web scraping
- `pytesseract` for OCR text extraction
- `matplotlib` for displaying images
- `mps` (for Apple M1/M2 support)

### Install Dependencies

To install the necessary dependencies, run:

```bash
pip install -r requirements.txt
```

You'll need to have Tesseract installed on your system for OCR functionality. Instructions for installation can be found here.

For web scraping, the beautifulsoup4 and requests packages are used.

```bash
Model Setup

    YOLO Model: The YOLO model is pre-trained using the yolo-config.yaml dataset and can be found under the models directory as best.pt.

    Training the YOLO Model: To retrain the YOLO model with a custom dataset, use the following command:

    yolo detect train model=yolo11n.pt epochs=100 imgsz=640 device=mps

```

## Usage

To run the full pipeline for detecting medicine boxes and extracting text via OCR:

```bash
python main.py
```
### How it works:

- `Capture Video`: The system starts capturing video from the default webcam.
- `YOLO Detection`: The YOLO model detects any medicine boxes in the video feed.

- `OCR Text Extraction`: Once a box is stable for a specified number of frames, the image of the box is cropped, preprocessed, and sent through the OCR pipeline.

- `Text Cleaning`: The extracted text is processed by removing stopwords and unnecessary characters.

### Web Scraping

You can use the UltrafarmaScraper to download images of medicine boxes:

```python
scraper = UltrafarmaScraper()
scraper.fetch_images("search term")
```

Using the Classes

## MedicineBoxImageCrawler

Use this class to fetch images of medicine boxes from Google Images.

```python
crawler = MedicineBoxImageCrawler(base_dir="medicine_images")
crawler.fetch_data(keyword="caixa remédio", max_num=50)

    base_dir: Directory to save images.

    fetch_data(): Downloads images based on the search keyword.
```

### OCRPipeline

Use this class to process images and extract text using OCR.
```python
ocr = OCRPipeline()
ocr.image_path_to_string('path/to/medicine_box_image.jpg')

    image_path_to_string(): Reads an image, processes it through OCR, and prints the cleaned text.

    processed_text_output: The cleaned OCR output after processing.
```