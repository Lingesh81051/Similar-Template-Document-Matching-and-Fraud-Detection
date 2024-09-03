import cv2
import numpy as np
from tkinter import Tk, Label, Button
from PIL import Image, ImageTk

class ImageComparator:
    def __init__(self, master, image1_path, image2_path):
        self.master = master
        self.image1 = cv2.imread(image1_path)
        self.image2 = cv2.imread(image2_path)

        self.create_gui()

    def create_gui(self):
        self.master.title("Image Comparator")

        # Display original images
        self.label_image1 = Label(self.master)
        self.label_image1.pack(side="left", padx=5, pady=5)
        self.display_image(self.image1, self.label_image1)

        self.label_image2 = Label(self.master)
        self.label_image2.pack(side="right", padx=5, pady=5)
        self.display_image(self.image2, self.label_image2)

        # Add buttons
        button_compare_layout = Button(self.master, text="Compare Layout", command=self.visualize_layout_difference)
        button_compare_layout.pack(side="bottom", pady=10)

        button_compare_ssim = Button(self.master, text="Compare SSIM", command=self.visualize_ssim)
        button_compare_ssim.pack(side="bottom", pady=10)

    def display_image(self, image, label):
        # Resize the image to fit the window
        max_height = 500
        max_width = 700

        if len(image.shape) == 2:
            height, width = image.shape
        elif len(image.shape) == 3:
            height, width, _ = image.shape
        else:
            raise ValueError("Unsupported image shape")

        if height > max_height or width > max_width:
            scale = min(max_height / height, max_width / width)
            image = cv2.resize(image, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)

        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(image)
        image = ImageTk.PhotoImage(image)
        label.configure(image=image)
        label.image = image

    def visualize_layout_difference(self):
        # Convert images to grayscale
        gray1 = cv2.cvtColor(self.image1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(self.image2, cv2.COLOR_BGR2GRAY)

        # Create a difference mask
        difference = cv2.absdiff(gray1, gray2)
        _, mask = cv2.threshold(difference, 30, 255, cv2.THRESH_BINARY)

        # Invert the mask
        mask = cv2.bitwise_not(mask)

        # Remove difference from image2
        self.image2_without_difference = cv2.bitwise_and(self.image2, self.image2, mask=mask)

        # Display the modified image2 without the difference in a new window
        self.display_in_new_window(self.image2_without_difference)

    def display_in_new_window(self, image):
        new_window = Tk()
        new_window.title("Removed Difference")

        label = Label(new_window)
        label.pack()

        self.display_image(image, label)

        new_window.mainloop()

    def visualize_ssim(self):
        print("Calculating SSIM...")
        # Your SSIM calculation code here

# Example usage
if __name__ == "__main__":
    root = Tk()

    # Replace 'path_to_image1.jpg' and 'path_to_image2.jpg' with your image file paths
    comparator = ImageComparator(root, "C:/Users/likith/Music/py/ac.jpg", "C:/Users/likith/Music/py/ac-x.jpg")

    root.mainloop()
