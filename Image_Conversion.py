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
