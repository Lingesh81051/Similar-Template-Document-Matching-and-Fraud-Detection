import cv2
from tkinter import Tk, Label, Button
from PIL import Image, ImageTk

class ImageComparator:
    def __init__(self, master, image1_path, image2_path):
        self.master = master
        self.image1 = cv2.imread(image1_path)
        self.image2 = cv2.imread(image2_path)
        self.clean_image2 = None
        self.diff_image = None

        self.create_gui()

    def create_gui(self):
        self.master.title("Image Comparator")

        # Define max height and width for the displayed images
        max_height = 500
        max_width = 350

        # Display original images
        self.label_image1 = Label(self.master)
        self.label_image1.pack(side="left", padx=5, pady=5)
        self.display_image(self.image1, self.label_image1, max_height, max_width)

        self.label_image2 = Label(self.master)
        self.label_image2.pack(side="left", padx=5, pady=5)
        self.display_image(self.image2, self.label_image2, max_height, max_width)

        # Add button for comparing layout and removing differences
        button_compare_layout = Button(self.master, text="Compare Layout", command=self.visualize_layout_difference)
        button_compare_layout.pack(side="bottom", pady=10)

    def display_image(self, image, label, max_height, max_width):
        # Resize the image to fit the window
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
        if self.image1 is not None and self.image2 is not None:
            # Convert images to grayscale
            gray1 = cv2.cvtColor(self.image1, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(self.image2, cv2.COLOR_BGR2GRAY)

            # Find absolute difference between the two images
            difference = cv2.absdiff(gray2, gray1)

            # Apply a threshold to identify the differences
            _, thresholded = cv2.threshold(difference, 30, 255, cv2.THRESH_BINARY)

            # Invert the thresholded image to create a mask of differences
            mask = cv2.bitwise_not(thresholded)

            # Use the mask to remove differences from the second image
            self.clean_image2 = cv2.bitwise_and(self.image2, self.image2, mask=mask)

            # Display the cleaned image (image 2 without removed data)
            self.display_image(self.clean_image2, self.label_image2, max_height=500, max_width=350)

# Example usage
if __name__ == "__main__":
    root = Tk()



    # Replace 'path_to_image1.jpg' and 'path_to_image2.jpg' with your image file paths
    comparator = ImageComparator(root, "C:/Users/likith/Music/py/ac.jpg", "C:/Users/likith/Music/py/ac-x.jpg")

    root.mainloop()
