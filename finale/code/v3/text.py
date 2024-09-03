import cv2
import numpy as np
from tkinter import Tk, Label, Button, filedialog, Text
from PIL import Image, ImageTk
import pytesseract
import os
import shutil

class ImageComparator:
    def __init__(self, master):
        self.master = master
        self.master.title("DOC-U-MATCH-RIX")
        self.template = None
        self.claimed_document = []

        self.label_status = Label(master, text="")
        self.label_status.pack()

        self.label_image1 = Label(master)
        self.label_image1.pack(side="left", padx=5, pady=5)

        self.label_image2 = Label(master)
        self.label_image2.pack(side="right", padx=5, pady=5)

        self.text_area = Text(master, height=10, width=50)
        self.text_area.pack()

        self.clear_extracted_text()

        button_select_template = Button(master, text="Select Standard Template", command=self.select_template)
        button_select_template.pack(side="top", pady=10)

        button_select_document = Button(master, text="Select Claimed Document", command=self.select_claimed_document)
        button_select_document.pack(side="top", pady=10)

        button_clear_text = Button(master, text="Clear Extracted Text", command=self.clear_extracted_text)
        button_clear_text.pack(side="bottom", pady=10)

        button_compare_layout = Button(master, text="Compare Layout", command=self.visualize_layout_difference)
        button_compare_layout.pack(side="top", pady=10)

        button_fraud_detection = Button(master, text="Fraud Detection", command=self.detect_fraud)
        button_fraud_detection.pack(side="bottom", pady=10)

        button_compare_with_users = Button(master, text="Compare with Company Users", command=self.compare_with_company_users)
        button_compare_with_users.pack(side="bottom", pady=10)


    def clear_extracted_text(self):
        with open("extracted_text_difference.txt", "w") as f:
            f.write("")

    def resize_and_display_image(self, image, label):
        max_height = 500
        max_width = 700

        height, width = image.shape[:2]
        if height > max_height or width > max_width:
            scale = min(max_height / height, max_width / width)
            image = cv2.resize(image, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)

        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(image)
        image = ImageTk.PhotoImage(image)
        label.configure(image=image)
        label.image = image

    def select_template(self):
        filename = filedialog.askopenfilename()
        if filename:
            self.template = cv2.imread(filename)
            self.resize_and_display_image(self.template, self.label_image1)
            # Extract text from the standard template
            standard_text = self.extract_text_from_image(self.template)
            # Save extracted text to a file
            with open("standard_text.txt", "w") as f:
                f.write(standard_text)


    def select_claimed_document(self):
        filenames = filedialog.askopenfilenames()
        if filenames:
            self.claimed_document = list(filenames)
            self.resize_and_display_image(cv2.imread(self.claimed_document[0]), self.label_image2)

    def visualize_layout_difference(self):
        if self.template is None or not self.claimed_document:
            self.label_status.config(text="Please select template and claimed document first")
            return

        gray1 = cv2.cvtColor(self.template, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(cv2.imread(self.claimed_document[0]), cv2.COLOR_BGR2GRAY)
        difference = cv2.absdiff(gray1, gray2)
        self.resize_and_display_image(difference, self.label_image2)

        # Convert difference image to RGB
        difference_rgb = cv2.cvtColor(difference, cv2.COLOR_GRAY2RGB)

        # Extract text from the difference image
        extracted_text = self.extract_text_from_image(difference_rgb)
        with open("extracted_text_difference.txt", "w") as f:
            f.write(extracted_text)

        # Display extracted text from claimed document in the text box
        self.text_area.delete(1.0, "end")
        self.text_area.insert("end", extracted_text)

    def extract_text_from_image(self, image):
        # Preprocess the image
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        _, thresholded = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Perform OCR with language configuration and PSM
        extracted_text = pytesseract.image_to_string(
            thresholded,
            lang='eng',  # Specify language (e.g., 'eng' for English)
            config='--psm 6',  # Page Segmentation Mode (6 for a single uniform block of text)
            )
        return extracted_text

    def detect_fraud(self):
        if self.template is None or not self.claimed_document:
            self.label_status.config(text="Please compare layout first")
            return

        # Read standard text from file
        with open("standard_text.txt", "r") as f:
            standard_text = f.read().split()

        # Read extracted text difference from file
        with open("extracted_text_difference.txt", "r") as f:
            extracted_text_difference = f.read().split()

        # Compare each word from extracted text difference with standard text
        for word in extracted_text_difference:
            if word in standard_text:
                self.label_status.config(text="Fraud detected: The document do not Match the Standard Template")
                return

        self.label_status.config(text="No fraud detected")

    def compare_with_company_users(self):
        if not self.claimed_document:
            self.label_status.config(text="Please select a claimed document first")
            return

        # Iterate over selected documents
        for claimed_document_path in self.claimed_document:
            # Read extracted text difference from file
            with open("extracted_text_difference.txt", "r") as f:
                extracted_text_difference = f.read()

            # Read company users text from file
            with open("company_users.txt", "r") as f:
                company_users_text = f.read()

            # Check if there's any match with company users
            if extracted_text_difference in company_users_text:
                self.label_status.config(text=f"Match found with a company user in {claimed_document_path}")
                # Get the filename of the claimed document
                claimed_document_filename = os.path.basename(claimed_document_path)
                # Copy claimed document to 'genuine' folder
                if not os.path.exists("genuine"):
                    os.makedirs("genuine")
                shutil.copy(claimed_document_path, os.path.join("genuine", claimed_document_filename))
            else:
                self.label_status.config(text=f"No match found with company users in {claimed_document_path}")


def main():
    root = Tk()
    app = ImageComparator(root)
    root.mainloop()

if __name__ == "__main__":
    main()
