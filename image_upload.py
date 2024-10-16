# Function to process the image pipeline
from Image_Conversion import *
def process_image_pipeline(img_path, output_image_path, resolution):
    try:
        resized_image_path = resize_to_resolution(img_path, output_image_path, resolution)
        print(f"Resized image saved at: {resized_image_path}")  # Log resized image path

        enhanced_image_path = denoise_image(resized_image_path)
        if enhanced_image_path:
            print(f"Denoised image saved at: {enhanced_image_path}")  # Log denoised image path
            json_file_path = perform_ocr_and_get_json(enhanced_image_path)
            print(f"JSON file generated at: {json_file_path}")  # Log JSON file path
            return json_file_path
        else:
            print("Error: Denoising failed.")  # Log denoising failure
            return {"error": "Image processing failed"}
    except Exception as e:
        print(f"Error in process_image_pipeline: {str(e)}")  # Log error in processing pipeline
        return {"error": str(e)}