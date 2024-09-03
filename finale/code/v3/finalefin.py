import cv2
import numpy as np
from tkinter import Tk, Button, filedialog, Text, Label, Canvas, Entry,Frame
from tkinter import Tk, Canvas, Entry, Text, Button, PhotoImage
from PIL import Image, ImageTk
import pytesseract
import os
import fitz  # PyMuPDF
from tkinter import Menu, Toplevel
from company_window import*
import shutil
import threading
import csv  # Import CSV module for reading/writing CSV files
from pathlib import Path

OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path(r"C:\Users\likith\Music\finale\assets\frame0")

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

# Function to read company users from CSV file
def read_company_users_from_csv(filename):
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        company_users = [row[0] for row in reader]  # Assuming company users are in the first column
    return company_users

# Function to write company users to CSV file
def write_company_users_to_csv(filename, company_users):
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        for user in company_users:
            writer.writerow([user])

class ImageComparator:
    def __init__(self, master, canvas):
        self.master = master
        self.canvas = canvas
        self.master.title("DOC-U-MATCH-RIX")
        self.template = None
        self.claimed_documents = []
        self.extracted_text = None  # Store extracted text

        menubar = Menu(master)
        master.config(menu=menubar)
        company_menu = Menu(menubar, tearoff=0) 
        menubar.add_command(label="USERS", command=self.open_company_window)



        self.label_status = Label(master, text="", font=("Inter", 12))
        self.label_status.pack()

        self.label_image1 = Label(master)
        self.label_image1.pack(side="left", padx=5, pady=5)

        # Frame to hold the selected documents' images
        self.documents_frame = Frame(master)
        self.documents_frame.pack(side="right", padx=5, pady=5)














        
        

        self.label_status = Label(master, text="", font=("Inter", 12))  # Increase font size to 12
        self.label_status.pack()

        self.label_image1 = Label(master)
        self.label_image1.pack(side="left", padx=5, pady=5)

        self.label_image2 = Label(master)
        self.label_image2.pack(side="right", padx=5, pady=5)

        # Define text area
        self.text_area = Text(master, height=10, width=50)
        self.text_area.insert("end","\n\n\n\t\tDOC-U-MATCH-RIX\n")
        self.text_area.pack()  # Moved the packing of text_area here

        button_select_template = self.create_buttona("Select Standard Template", self.select_template)
        button_select_template.pack(side="top", pady=10)

        button_select_document = self.create_buttonb("Select Claimed Documents", self.select_claimed_documents)
        button_select_document.pack(side="top", pady=10)

        button_segregate_documents = self.create_buttonc("Segregate Documents", self.segregate_documents)
        button_segregate_documents.pack(side="bottom", pady=10)

        button_clear_all = self.create_buttond("Clear All", self.clear_all)
        button_clear_all.pack(side="bottom", pady=10)

        # File paths
        self.standard_text_file = "standard_text.txt"
        self.company_users_file = "company_users.csv"

    def create_buttona(self, text, command):

        button_image_normal = PhotoImage(file=relative_to_assets("button.png"))
        button_image_hover = PhotoImage(file=relative_to_assets("button_hover.png"))
        buttona = Button(
            image=button_image_normal,
            borderwidth=0,
            highlightthickness=0,
            command=command,
            relief="flat"
    )
        buttona.bind("<Enter>", lambda e: buttona.config(image=button_image_hover))
        buttona.bind("<Leave>", lambda e: buttona.config(image=button_image_normal))
        buttona.image = button_image_normal
        buttona.config(compound="center",  fg="#ffffff", font=("Inter", 10))
        return buttona

    def create_buttonb(self, text, command):

        button_image_normal = PhotoImage(file=relative_to_assets("button_2.png"))
        button_image_hover = PhotoImage(file=relative_to_assets("button_hover_2.png"))
        buttonb = Button(
            image=button_image_normal,
            borderwidth=0,
            highlightthickness=0,
            command=command,
            relief="flat"
    )
        buttonb.bind("<Enter>", lambda e: buttonb.config(image=button_image_hover))
        buttonb.bind("<Leave>", lambda e: buttonb.config(image=button_image_normal))
        buttonb.image = button_image_normal
        buttonb.config(compound="center",  fg="#ffffff", font=("Inter", 10))
        return buttonb

    def create_buttonc(self, text, command):

        button_image_normal = PhotoImage(file=relative_to_assets("button_3.png"))
        button_image_hover = PhotoImage(file=relative_to_assets("button_hover_3.png"))
        buttonc = Button(
            image=button_image_normal,
            borderwidth=0,
            highlightthickness=0,
            command=command,
            relief="flat"
    )
        buttonc.bind("<Enter>", lambda e: buttonc.config(image=button_image_hover))
        buttonc.bind("<Leave>", lambda e: buttonc.config(image=button_image_normal))
        buttonc.image = button_image_normal
        buttonc.config(compound="center",  fg="#ffffff", font=("Inter", 10))
        return buttonc

    def create_buttond(self, text, command):

        button_image_normal = PhotoImage(file=relative_to_assets("button_4.png"))
        button_image_hover = PhotoImage(file=relative_to_assets("button_hover_4.png"))
        buttond = Button(
            image=button_image_normal,
            borderwidth=0,
            highlightthickness=0,
            command=command,
            relief="flat"
    )
        buttond.bind("<Enter>", lambda e: buttond.config(image=button_image_hover))
        buttond.bind("<Leave>", lambda e: buttond.config(image=button_image_normal))
        buttond.image = button_image_normal
        buttond.config(compound="center", fg="#ffffff", font=("Inter", 10))
        return buttond



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
            with open(self.standard_text_file, "w") as f:
                f.write(standard_text)

    def write_company_users_to_csv(file_path, data):
        with open(file_path, 'w', newline='') as csvfile:
            fieldnames = [ 'name', 'other_info']  # Define the column names
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()  # Write the header row

            for user in data:
                writer.writerow(user)

# Example data (replace this with your actual company user data)
    company_users_data = [
        { 'name': 'chris', 'other_info': 'Some information'},
        { 'name': 'likith Kumar S', 'other_info': 'More information'},
    # Add more user data as needed
    ]

# File path for the CSV file
    company_users_file = 'company_users.csv'

# Write company user data to the CSV file
    write_company_users_to_csv(company_users_file, company_users_data)

    def select_claimed_documents(self):
        filenames = filedialog.askopenfilenames()
        if filenames:
            self.claimed_documents = []
            for filename in filenames:
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                    self.claimed_documents.append(filename)
                    self.display_claimed_document(filename)
            self.label_status.config(text=f"Selected {len(self.claimed_documents)} documents")

    def display_claimed_document(self, filename):
        image = Image.open(filename)
        image.thumbnail((200, 200))  # Resize the image to fit in the frame
        photo = ImageTk.PhotoImage(image)
        label = Label(self.documents_frame, image=photo)
        label.image = photo  # Keep a reference to prevent garbage collection
        label.pack(pady=5)

    def extract_images_from_pdf(self, pdf_path):
        images = []
        doc = fitz.open(pdf_path)
        for i in range(doc.page_count):
            page = doc.load_page(i)
            pix = page.get_pixmap()
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            img_path = f"{pdf_path}_page_{i + 1}.png"
            img.save(img_path)
            images.append(img_path)
        doc.close()
        return images

    def visualize_layout_difference(self, claimed_document):
        if self.template is None or claimed_document is None:
            return None

        gray1 = cv2.cvtColor(self.template, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(claimed_document, cv2.COLOR_BGR2GRAY)

        # Resize gray2 to match the dimensions of gray1
        gray2_resized = cv2.resize(gray2, (gray1.shape[1], gray1.shape[0]))

        # Calculate the absolute difference
        difference = cv2.absdiff(gray1, gray2_resized)

        # Display the difference image
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
        with open(self.standard_text_file, "r") as f:
            standard_text = f.read().split()

        # Compare each word from extracted text difference with standard text
        for word in extracted_text.split():
            if word in standard_text:
                return True

        return False
    
    def update_files_list(self):
        genuine_files = self.get_files_list("genuine")
        fraud_files = self.get_files_list("fraud")

        genuine_text = "\n".join(genuine_files)
        fraud_text = "\n".join(fraud_files)

        self.text_area.delete("1.0", "end")
        self.text_area.insert("end", "Genuine Files:\n" + genuine_text + "\n")
        self.text_area.insert("end", "Fraud Files:\n" + fraud_text + "\n")

        # Schedule the next update after 5 seconds (adjust as needed)
        self.master.after(2000, self.update_files_list)

    def get_files_list(self, folder):
        if os.path.exists(folder):
            return os.listdir(folder)
        else:
            return []

    def compare_with_company_users(self):
        if not self.extracted_text:
            return False

    # Read company users from CSV file
        company_users = read_company_users_from_csv(self.company_users_file)

    # Convert extracted text to lowercase for case-insensitive comparison
        extracted_text_lower = self.extracted_text.lower()

    # Check if there's any match with company users
        for user in company_users:
            if isinstance(user, str) and user.lower() in extracted_text_lower:
                return True

        return False


    def segregate_documents(self):
        if not self.claimed_documents:
            self.label_status.config(text="Please select claimed documents first")
            return

    # Remove displayed claimed documents
        for widget in self.documents_frame.winfo_children():
            widget.destroy()

    # Show processing message
        self.label_status.config(text="Processing documents...")

    # Create directories for genuine and fraud documents if they don't exist
        genuine_folder = "genuine"
        fraud_folder = "fraud"
        if not os.path.exists(genuine_folder):
            os.makedirs(genuine_folder)
        if not os.path.exists(fraud_folder):
            os.makedirs(fraud_folder)

    # Counters for genuine and fraud documents
        genuine_count = 0
        fraud_count = 0

    # Process each claimed document
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
                    self.save_marked_image(claimed_document, claimed_document_path, fraud_folder)

    # Update status label with results
        self.label_status.config(text=f"{genuine_count} documents found genuine. {fraud_count} documents found fraudulent.")

    def process_documents(self):
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
                    self.save_marked_image(claimed_document, claimed_document_path, fraud_folder)

        self.label_status.config(text=f"{genuine_count} documents found genuine. {fraud_count} documents found fraudulent.")

    def save_marked_image(self, image, claimed_document_path, folder):
        # Make a copy of the original image to mark the fraud parts
        marked_image = image.copy()

        # Resize the image to match the dimensions of self.template
        image_resized = cv2.resize(image, (self.template.shape[1], self.template.shape[0]))

        # Compute the absolute difference between the template and resized image
        difference = cv2.absdiff(self.template, image_resized)

        # Threshold the difference image to binarize it
        _, thresholded = cv2.threshold(difference, 30, 255, cv2.THRESH_BINARY)

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

    def clear_all(self):
        self.template = None
        self.claimed_documents = []
        self.extracted_text = None
        self.label_status.config(text="")
        self.label_image1.config(image=None)
        self.label_image2.config(image=None)
        self.text_area.delete("1.0", "end")

    def open_company_window(self):
        company_window = Toplevel(self.master)
        company_window.title("Company Window")
        company_window.geometry("750x550")
        company_window.configure(bg="#69A8D4")

        # Call methods to create the company window interface
        CompanyWindowInterface(company_window)


def main():
    root = Tk()
    
    root.title("DOC-U-MATCH-RIX")
    root.geometry("700x550")
    root.configure(bg="#69A8D4")

    # Load the background image
    background_image = PhotoImage(file=relative_to_assets("image_1.png"))

    # Create a label to hold the background image
    background_label = Label(root, image=background_image)
    background_label.place(x=0, y=0, relwidth=1, relheight=1)

    # Set the image as the background
    root.image = background_image

    canvas = Canvas(
        root,
        bg="#FFFFFF",
        bd=0,
        highlightthickness=0,
        relief="ridge"
    )
    canvas.place(relx=0.5, rely=0.5, anchor="center")

    image_image_2 = PhotoImage(file=relative_to_assets("image_1.png"))
    image_2 = canvas.create_image(
        -18,
        200,
        anchor="nw",
        image=image_image_2
    )

    app = ImageComparator(root, canvas)
    root.mainloop()

if __name__ == "__main__":
    main()
#likith Kumar S