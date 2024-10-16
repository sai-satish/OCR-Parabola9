#image downscaling
from PIL import Image
import cv2
import numpy as np
import json
import cv2
from paddleocr import PaddleOCR
import numpy as np
from matplotlib import pyplot as plt

# Increase the limit to handle large images
Image.MAX_IMAGE_PIXELS = None

def resize_to_resolution(img_path, output_image_path, resolution):
    # Open the image file
    with Image.open(img_path) as img:
        # Get original dimensions
        original_width, original_height = img.size
        # print(f"Original size: {img.size}")
        
        # Get target resolution dimensions
        target_width, target_height = resolution
        
        # Calculate aspect ratio
        aspect_ratio = original_width / original_height
        
        # Adjust resolution to maintain aspect ratio
        if original_width > original_height:
            # Fit width to target and adjust height
            new_width = target_width
            new_height = int(target_width / aspect_ratio)
        else:
            # Fit height to target and adjust width
            new_height = target_height
            new_width = int(target_height * aspect_ratio)
        
        # Resize the image
        resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Save the resized image
        resized_img.save(output_image_path)
        # print(f"Resized image to: {resized_img.size}")
        # print(f"Image saved to {output_image_path}")
        
        # Show the resized image
        # resized_img.show()
    return output_image_path



#denoising the image

# Define the image path
path = './sample1-out/output_image_2k.jpg'

# Load the compressed image
def denoise_image(path):
    image = cv2.imread(path)

    # Check if the image was successfully loaded
    if image is None:
        print("Error: Unable to open/read image file. Check the file path and integrity.")
    else:
        # Apply Non-Local Means Denoising (correct parameters)
        # Parameters: (source, h strength, template window size, search window size)
        denoised_image_nlmeans = cv2.fastNlMeansDenoisingColored(image, h=10, templateWindowSize=7, searchWindowSize=21)

        # Apply bilateral filter for stronger noise reduction without blurring the edges
        # Parameters: (source, filter size, sigma for color space, sigma for coordinate space)
        denoised_image_bilateral = cv2.bilateralFilter(denoised_image_nlmeans, d=9, sigmaColor=100, sigmaSpace=100)

        # Apply sharpening kernel to bring back some clarity after denoising
        sharpening_kernel = np.array([[0, -1, 0],
                                    [-1, 5, -1],
                                    [0, -1, 0]])

        # Sharpen the image after denoising
        sharpened_image = cv2.filter2D(denoised_image_bilateral, -1, sharpening_kernel)

        # Convert the image to grayscale for contrast enhancement
        gray_image = cv2.cvtColor(sharpened_image, cv2.COLOR_BGR2GRAY)

        # Use histogram equalization to improve contrast
        equalized_image = cv2.equalizeHist(gray_image)

        # Convert back to BGR to save as color image
        final_image = cv2.cvtColor(equalized_image, cv2.COLOR_GRAY2BGR)
        enhanced_image_path = "enhanced_image_denoised.jpg"
        # Save the enhanced image without increasing pixel dimensions
        cv2.imwrite(enhanced_image_path, final_image)
        # print("Image processing complete. The enhanced image has been saved.")
        return enhanced_image_path


def perform_ocr_and_get_json(img_path):

    # Initialize the PaddleOCR model for English
    ocr = PaddleOCR(use_angle_cls=True, lang='en')

    # Load the image
    img_path = './sample1-out/output_image_2k.jpg'
    img = cv2.imread(img_path)

    # Perform OCR on the image
    result = ocr.ocr(img_path, cls=True)

    # Function to group text boxes into rows based on y-coordinates
    def is_same_row(box1, box2, row_threshold=10):
        _, y1, _, y2 = box1[0][1], box1[2][1], box2[0][1], box2[2][1]
        return abs(y1 - y2) < row_threshold

    # Group the detected text into rows
    rows = []
    current_row = []
    for line in result[0]:
        box = line[0]      # Bounding box coordinates
        text = line[1][0]  # Detected text
        confidence = line[1][1]

        if current_row and not is_same_row(current_row[-1][0], box):
            rows.append(current_row)
            current_row = []

        current_row.append((box, text, confidence))

    if current_row:
        rows.append(current_row)

    # Sort each row by the x-coordinate for left-to-right reading
    for row in rows:
        row.sort(key=lambda x: x[0][0][0])

    # Dynamically extract column headers from the first row
    column_headers = [item[1] for item in rows[0]]  # Extract text values from the first row

    # Convert subsequent rows into structured data
    data = []
    for row in rows[1:]:  # Skip the first row, as it's the header
        row_data = {}
        for i, (box, text, confidence) in enumerate(row):
            if i < len(column_headers):  # Ensure we don't exceed column count
                row_data[column_headers[i]] = {
                    "text": text,
                    "confidence": confidence,
                    "bounding_box": box  # Store the bounding box information
                }
        data.append(row_data)
    

    # Save the structured data with bounding box info as JSON
    json_file_path = './bounding_box_data_with_text.json'
    with open(json_file_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)

    # print(f"Bounding box data saved as JSON: {json_file_path}")

    # (Optional) Visualize the detected text and bounding boxes
    boxes = [res[0] for res in result[0]]  # Bounding boxes for the detected text
    txts = [res[1][0] for res in result[0]]  # The recognized text
    scores = [res[1][1] for res in result[0]]  # Confidence scores

    # Draw results on the image and visualize
    image_with_boxes = cv2.polylines(img.copy(), [np.array(box).astype(int) for box in boxes], True, (0, 255, 0), 2)

    # Convert BGR to RGB for displaying with matplotlib
    # image_with_boxes_rgb = cv2.cvtColor(image_with_boxes, cv2.COLOR_BGR2RGB)
    return json_file_path