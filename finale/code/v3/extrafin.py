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
        self.claimed_documents = []
        self.extracted_text = None  # Store extracted text

        self.label_status = Label(master, text="")
        self.label_status.pack()

        self.label_image1 = Label(master)
        self.label_image1.pack(side="left", padx=5, pady=5)

        self.label_image2 = Label(master)
        self.label_image2.pack(side="right", padx=5, pady=5)

        self.text_area = Text(master, height=10, width=50)
        self.text_area.pack()

        button_select_template = Button(master, text="Select Standard Template", command=self.select_template)
        button_select_template.pack(side="top", pady=10)

        button_select_document = Button(master, text="Select Claimed Documents", command=self.select_claimed_documents)
        button_select_document.pack(side="top", pady=10)

        button_segregate_documents = Button(master, text="Segregate Documents", command=self.segregate_documents)
        button_segregate_documents.pack(side="bottom", pady=10)

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

    def select_claimed_documents(self):
        filenames = filedialog.askopenfilenames()
        if filenames:
            self.claimed_documents = list(filenames)
            self.label_status.config(text=f"Selected {len(self.claimed_documents)} documents")

    def visualize_layout_difference(self, claimed_document):
        if self.template is None or claimed_document is None:
            return None

        gray1 = cv2.cvtColor(self.template, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(claimed_document, cv2.COLOR_BGR2GRAY)
        difference = cv2.absdiff(gray1, gray2)
        self.resize_and_display_image(difference, self.label_image2)

        # Convert difference image to RGB
        difference_rgb = cv2.cvtColor(difference, cv2.COLOR_GRAY2RGB)

        # Extract text from the difference image
        extracted_text = self.extract_text_from_image(difference_rgb)
        return extracted_text

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
        self.extracted_text = extracted_text  # Store extracted text
        return extracted_text

    def detect_fraud(self, extracted_text):
        if self.template is None or not extracted_text:
            return False

        # Read standard text from file
        with open("standard_text.txt", "r") as f:
            standard_text = f.read().split()

        # Compare each word from extracted text difference with standard text
        for word in extracted_text.split():
            if word in standard_text:
                return True

        return False

    def compare_with_company_users(self):
        if not self.extracted_text:
            return False

        # Read company users text from file
        with open("company_users.txt", "r") as f:
            company_users_text = f.read()

        # Check if there's any match with company users
        return self.extracted_text in company_users_text

    def segregate_documents(self):
        if not self.claimed_documents:
            self.label_status.config(text="Please select claimed documents first")
            return

        genuine_folder = "genuine"
        fraud_folder = "fraud"
        if not os.path.exists(genuine_folder):
            os.makedirs(genuine_folder)
        if not os.path.exists(fraud_folder):
            os.makedirs(fraud_folder)

        fraud_count = 0
        genuine_count = 0

        for claimed_document_path in self.claimed_documents:
            claimed_document = cv2.imread(claimed_document_path)
            extracted_text = self.visualize_layout_difference(claimed_document)
            is_fraud = self.detect_fraud(extracted_text)
            if is_fraud:
                fraud_count += 1
                # Save image with marked difference in red box
                self.save_marked_image(claimed_document, claimed_document_path, fraud_folder)
            else:
                is_genuine = self.compare_with_company_users()
                if is_genuine:
                    genuine_count += 1
                    shutil.copy(claimed_document_path, genuine_folder)
                else:
                    fraud_count += 1
                    # Save image with marked difference in red box
                    self.save_marked_image(claimed_document, claimed_document_path, fraud_folder)

        self.label_status.config(text=f"{genuine_count} documents found genuine. {fraud_count} documents found fraudulent.")

    def save_marked_image(self, image, claimed_document_path, folder):
        # Make a copy of the original image to mark the fraud parts
        marked_image = image.copy()

        # Convert the image to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Compute the absolute difference between the template and claimed document
        difference = cv2.absdiff(self.template, image)

        # Threshold the difference image to binarize it
        _, thresholded = cv2.threshold(difference, 30, 255, cv2.THRESH_BINARY)       #RESH_BINARY)

        # Convert the thresholded image to grayscale
        thresholded_gray = cv2.cvtColor(thresholded, cv2.COLOR_BGR2GRAY)

        # Find contours in the thresholded grayscale image
        contours, _ = cv2.findContours(thresholded_gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Draw red rectangles around the contours
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(marked_image, (x, y), (x + w, y + h), (0, 0, 255), 2)  # Red color

        # Save the marked image in the fraud folder
        filename = os.path.basename(claimed_document_path)
        marked_image_path = os.path.join(folder, filename)
        cv2.imwrite(marked_image_path, marked_image)


def main():
    root = Tk()
    app = ImageComparator(root)
    root.mainloop()


if __name__ == "__main__":
    main()
#final code working 