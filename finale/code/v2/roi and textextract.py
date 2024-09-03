import cv2
import pytesseract

# Path to Tesseract executable (change this path according to your installation)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Global variables to store coordinates
selected_roi = False
x, y, w, h = 0, 0, 0, 0

# Mouse callback function
def select_roi(event, ex, ey, flags, params):
    global x, y, w, h, selected_roi

    if event == cv2.EVENT_LBUTTONDOWN:
        x, y = ex, ey

    elif event == cv2.EVENT_LBUTTONUP:
        w, h = ex - x, ey - y
        selected_roi = True

# Load the image
image_path = "C:/Users/likith/Music/py/ac1.jpg"
image = cv2.imread(image_path)

# Resize image to fit the window
max_height = 600
max_width = 800
height, width, _ = image.shape
if height > max_height or width > max_width:
    scale = min(max_height / height, max_width / width)
    image = cv2.resize(image, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)

# Create a window and set mouse callback
cv2.namedWindow('Select ROI')
cv2.setMouseCallback('Select ROI', select_roi)

while True:
    clone = image.copy()
    if selected_roi:
        cv2.rectangle(clone, (x, y), (x + w, y + h), (0, 255, 0), 2)
    
    cv2.imshow('Select ROI', clone)
    key = cv2.waitKey(1) & 0xFF

    if key == ord('c') and selected_roi:
        roi = image[y:y + h, x:x + w]
        gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        extracted_text = pytesseract.image_to_string(gray_roi)
        print("Extracted Text:")
        print(extracted_text)

        # Save extracted text to a file
        with open('extracted_text.txt', 'w') as file:
            file.write(extracted_text)
        print("Extracted text saved to 'extracted_text.txt'")
        break

    elif key == ord('q'):
        break

cv2.destroyAllWindows()
