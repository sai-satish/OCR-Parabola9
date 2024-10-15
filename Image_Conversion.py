#image downscaling
from PIL import Image

# Increase the limit to handle large images
Image.MAX_IMAGE_PIXELS = None

def resize_to_resolution(img_path, output_image_path, resolution):
    # Open the image file
    with Image.open(img_path) as img:
        # Get original dimensions
        original_width, original_height = img.size
        print(f"Original size: {img.size}")
        
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
        print(f"Resized image to: {resized_img.size}")
        print(f"Image saved to {output_image_path}")
        
        # Show the resized image
        resized_img.show()

# Example usage:
# Resize the image to 2K or 4K resolution

# # For 2K (2560x1440) resolution
# resize_to_resolution(r"/home/ec2-user/Dataset/sample1.jpg", "output_image_2k.jpg", (2560, 1440))

# # For 4K (3840x2160) resolution
resize_to_resolution(r"./Dataset/sample1.jpg", "output_image_4k.jpg", (3840, 2160))


#denoising the image

import cv2
import numpy as np

# Define the image path
path = './sample1-out/output_image_2k.jpg'

# Load the compressed image
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

    # Save the enhanced image without increasing pixel dimensions
    cv2.imwrite("enhanced_image_denoised-2.jpg", final_image)
    print("Image processing complete. The enhanced image has been saved.")
