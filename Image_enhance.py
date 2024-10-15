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
