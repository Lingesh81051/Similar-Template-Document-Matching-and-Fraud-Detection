# Similar Template Document Matching and Fraud Detection
 An automated system for a health insurance company to streamline document processing, including template matching and fraud detection, resulting in reduction of processing time. 

-->Project Setup
This project uses several Python libraries for image processing, OCR, and GUI development. Below are the libraries used and a step-by-step guide on how to install them.

-->Required Libraries:
    1. opencv-python: Used for image processing tasks.
    2. numpy: A fundamental package for numerical computations in Python.
    3. Pillow: A Python Imaging Library used for opening, manipulating, and saving images.
    4. pytesseract: A Python wrapper for Google's Tesseract-OCR Engine, used for optical character recognition (OCR).
    5. pymupdf: A lightweight PDF and XPS viewer, renderer, and toolkit.
    6. tk: The Tkinter library, used for creating graphical user interfaces (GUIs).

Installation Guide:
To get started, you need Python installed on your system. If you haven't installed Python yet, you can download it from the official Python website: Python Download.

Step 1: Create a Virtual Environment (Optional but Recommended)
It's a good practice to create a virtual environment for your project to keep the dependencies isolated. You can create one using the following commands:
    a) Create a virtual environment named 'env'
    python -m venv env

    b) Activate the virtual environment
    # On Windows
    env\Scripts\activate

    c) On macOS/Linux
    source env/bin/activate

Step 2: Install Required Libraries
Once your environment is set up, you can install all the required libraries using pip. Run the following commands in your terminal:
    pip install opencv-python
    pip install numpy
    pip install pillow
    pip install pytesseract
    pip install pymupdf
    pip install tk

Alternative Installation Method
If you prefer to install all libraries at once, you can create a "requirements.txt" file with the following content:
    opencv-python
    numpy
    pillow
    pytesseract
    pymupdf
    tk

Then, run the command below:
pip install -r requirements.txt

-->Troubleshooting
    Tesseract Setup: For pytesseract to work, Tesseract-OCR must be installed on your system. You can download it from Tesseract GitHub. Make sure to add Tesseract to your system's PATH.

    Updating Libraries: If you face compatibility issues, try updating the libraries with pip install --upgrade <library_name>.
