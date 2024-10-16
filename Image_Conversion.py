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


# Function to process image with EasyOCR and PaddleOCR
def perform_ocr_and_get_json(img_path):
    img = cv2.imread(img_path)
    easy_reader = easyocr.Reader(['en'])
    paddle_reader = PaddleOCR(use_angle_cls=True, lang='en')
    easyocr_result = easy_reader.readtext(img_path, detail=1)
    
    rows = []
    for line in easyocr_result:
        try:
            box = line[0]
            easyocr_text = line[1]
            confidence = line[2]

            # Crop and run PaddleOCR
            x_min = int(min(box[0][0], box[1][0], box[2][0], box[3][0]))
            y_min = int(min(box[0][1], box[1][1], box[2][1], box[3][1]))
            x_max = int(max(box[0][0], box[1][0], box[2][0], box[3][0]))
            y_max = int(max(box[0][1], box[1][1], box[2][1], box[3][1]))

            cropped_img = img[y_min:y_max, x_min:x_max]
            cropped_img_path = './temp_cropped_img.jpg'
            cv2.imwrite(cropped_img_path, cropped_img)

            paddle_result = paddle_reader.ocr(cropped_img_path, cls=True)

            if paddle_result[0]:
                refined_text = paddle_result[0][0][1][0]
                refined_confidence = paddle_result[0][0][1][1]
            else:
                refined_text = easyocr_text
                refined_confidence = confidence

            # Convert bounding box to native Python list of int (to avoid numpy types)
            box = [[int(point[0]), int(point[1])] for point in box]

            # Append the processed result
            rows.append({
                "bounding_box": box,
                "easyocr_text": easyocr_text,
                "paddleocr_text": refined_text,
                "confidence": refined_confidence
            })

        except TypeError as e:
            print(f"Skipping text due to TypeError: {e}")
            continue

    # Save JSON
    json_file_path = './combined_ocr_results.json'
    try:
        with open(json_file_path, 'w') as json_file:
            json.dump(rows, json_file, indent=4)
    except TypeError as e:
        print(f"Error saving JSON: {e}")

    return json_file_path