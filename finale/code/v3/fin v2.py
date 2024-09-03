import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim
import matplotlib.pyplot as plt
from tkinter import Tk, Canvas, PhotoImage, Label, Button, filedialog, Text
from PIL import Image, ImageTk
import pytesseract
from difflib import SequenceMatcher

class ImageComparator:
    def __init__(self, master):
        self.master = master
        self.master.title("DOC-U-MATCH-RIX")
        self.selected_roi = None
        self.template = None
        self.claimed_document = None
        self.extracted_text = None

        self.label_status = Label(master, text="")
        self.label_status.pack()

        self.label_image1 = Label(master)
        self.label_image1.pack(side="left", padx=5, pady=5)

        self.label_image2 = Label(master)
        self.label_image2.pack(side="right", padx=5, pady=5)

        self.text_area = Text(master, height=10, width=50)
        self.text_area.pack()

        button_select_template = Button(master, text="Select Template", command=self.select_template)
        button_select_template.pack(side="top", pady=10)

        button_select_document = Button(master, text="Select Claimed Document", command=self.select_claimed_document)
        button_select_document.pack(side="top", pady=10)

        button_select_roi = Button(master, text="Select ROI (press C after selection)", command=self.select_roi)
        button_select_roi.pack(side="top", pady=10)

        button_compare_layout = Button(master, text="Compare Layout", command=self.visualize_layout_difference)
        button_compare_layout.pack(side="top", pady=10)

        button_compare_ssim = Button(master, text="Compare SSIM", command=self.visualize_ssim)
        button_compare_ssim.pack(side="top", pady=10)

        button_extract_text = Button(master, text="Extract Text", command=self.extract_text)
        button_extract_text.pack(side="bottom", pady=10)

        button_match_template = Button(master, text="Match Template", command=self.match_template)
        button_match_template.pack(side="bottom", pady=10)

        button_fraud_detection = Button(master, text="Fraud Detection", command=self.detect_fraud)
        button_fraud_detection.pack(side="bottom", pady=10)

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

    def select_claimed_document(self):
        filename = filedialog.askopenfilename()
        if filename:
            self.claimed_document = cv2.imread(filename)
            self.resize_and_display_image(self.claimed_document, self.label_image2)

    def select_roi(self):
        if self.claimed_document is None:
            self.label_status.config(text="Please select a claimed document first")
            return

        def select_roi_callback(event, x, y, flags, param):
            if event == cv2.EVENT_LBUTTONDOWN:
                self.selected_roi = (x, y, 0, 0)
            elif event == cv2.EVENT_MOUSEMOVE and flags == cv2.EVENT_FLAG_LBUTTON:
                self.selected_roi = (self.selected_roi[0], self.selected_roi[1], x - self.selected_roi[0], y - self.selected_roi[1])
            elif event == cv2.EVENT_LBUTTONUP:
                self.selected_roi = (self.selected_roi[0], self.selected_roi[1], x - self.selected_roi[0], y - self.selected_roi[1])

        cv2.namedWindow("Select ROI")
        cv2.setMouseCallback("Select ROI", select_roi_callback)

        while True:
            document_display = self.claimed_document.copy()
            if self.selected_roi is not None:
                x, y, w, h = self.selected_roi
                cv2.rectangle(document_display, (x, y), (x + w, y + h), (0, 255, 0), 2)
            self.resize_and_display_image(document_display, self.label_image1)
            cv2.imshow("Select ROI", document_display)
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            elif key == ord("c") and self.selected_roi is not None:
                break
        cv2.destroyAllWindows()

    def visualize_layout_difference(self):
        if self.template is None or self.claimed_document is None:
            self.label_status.config(text="Please select template and claimed document first")
            return

        gray1 = cv2.cvtColor(self.template, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(self.claimed_document, cv2.COLOR_BGR2GRAY)
        difference = cv2.absdiff(gray1, gray2)
        self.resize_and_display_image(difference, self.label_image2)

    def visualize_ssim(self):
        if self.template is None or self.claimed_document is None:
            self.label_status.config(text="Please select template and claimed document first")
            return

        gray1 = cv2.cvtColor(self.template, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(self.claimed_document, cv2.COLOR_BGR2GRAY)
        ssi_index, _ = ssim(gray1, gray2, full=True)
        self.label_status.config(text=f'SSIM: {ssi_index:.4f}')

    def extract_text(self):
        if self.selected_roi is None:
            self.label_status.config(text="Please select a region of interest first")
            return

        if self.claimed_document is None:
            self.label_status.config(text="Please select a claimed document first")
            return

        x, y, w, h = self.selected_roi
        roi = self.claimed_document[y:y+h, x:x+w]  # Adjust region size as needed

        # Preprocess the ROI
        gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        blurred_roi = cv2.GaussianBlur(gray_roi, (5, 5), 0)
        _, thresholded_roi = cv2.threshold(blurred_roi, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Perform OCR with language configuration and PSM
        extracted_text = pytesseract.image_to_string(
            thresholded_roi,
            lang='eng',  # Specify language (e.g., 'eng' for English)
            config='--psm 6',  # Page Segmentation Mode (6 for a single uniform block of text)
            )

        # Display extracted text in text area
        self.text_area.delete(1.0, "end")
        self.text_area.insert("end", extracted_text)

    def match_template(self):
        if self.template is None or self.claimed_document is None:
            self.label_status.config(text="Please select template and claimed document first")
            return

        # Convert images to grayscale
        template_gray = cv2.cvtColor(self.template, cv2.COLOR_BGR2GRAY)
        document_gray = cv2.cvtColor(self.claimed_document, cv2.COLOR_BGR2GRAY)

        # Match template
        result = cv2.matchTemplate(document_gray, template_gray, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        if max_val > 0.8:
            self.label_status.config(text="Template found in the claimed document")
        else:
            self.label_status.config(text="Template not found in the claimed document")

    def detect_fraud(self):
        if self.template is None or self.claimed_document is None:
            self.label_status.config(text="Please select template and claimed document first")
            return

        # Example fraud detection logic
        template_hash = hash(str(self.template))
        document_hash = hash(str(self.claimed_document))

        if template_hash == document_hash:
            self.label_status.config(text="Fraud detected: Same template used in claimed document")
        else:
            self.label_status.config(text="No fraud detected")

def main():
    root = Tk()
    app = ImageComparator(root)
    root.mainloop()

if __name__ == "__main__":
    main()
