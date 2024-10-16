# Import the required libraries
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from transformers import pipeline
import nest_asyncio
from pyngrok import ngrok
import uvicorn
import threading
import os
import signal
from PIL import Image
import cv2
import numpy as np
from paddleocr import PaddleOCR
import json
import aiofiles
from matplotlib import pyplot as plt

# Allow nested asyncio loops
nest_asyncio.apply()

# Load the Question Answering pipeline
qa_pipeline = pipeline('question-answering', model="distilbert-base-uncased-distilled-squad")

# Initialize the PaddleOCR model for English
ocr = PaddleOCR(use_angle_cls=True, lang='en')

# Initialize the FastAPI app
app = FastAPI()

# Enable CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Define the input model for the question and context (QA API)
class QARequest(BaseModel):
    question: str
    context: str

# Define the API route to handle question answering
@app.post("/qa/")
def answer_question(request: QARequest):
    result = qa_pipeline(question=request.question, context=request.context)
    return {"answer": result['answer']}

# Function to resize, denoise, process OCR, and return bounding boxes as JSON
def process_image_pipeline(img_path, output_image_path, resolution):
    def resize_to_resolution(img_path, output_image_path, resolution):
        with Image.open(img_path) as img:
            original_width, original_height = img.size
            target_width, target_height = resolution
            aspect_ratio = original_width / original_height
            if original_width > original_height:
                new_width = target_width
                new_height = int(target_width / aspect_ratio)
            else:
                new_height = target_height
                new_width = int(target_height * aspect_ratio)
            resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            resized_img.save(output_image_path)
        return output_image_path

    def denoise_image(image_path):
        image = cv2.imread(image_path)
        if image is None:
            return None
        denoised_image_nlmeans = cv2.fastNlMeansDenoisingColored(image, h=10, templateWindowSize=7, searchWindowSize=21)
        denoised_image_bilateral = cv2.bilateralFilter(denoised_image_nlmeans, d=9, sigmaColor=100, sigmaSpace=100)
        sharpening_kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        sharpened_image = cv2.filter2D(denoised_image_bilateral, -1, sharpening_kernel)
        gray_image = cv2.cvtColor(sharpened_image, cv2.COLOR_BGR2GRAY)
        equalized_image = cv2.equalizeHist(gray_image)
        final_image = cv2.cvtColor(equalized_image, cv2.COLOR_GRAY2BGR)
        enhanced_image_path = "enhanced_image_denoised.jpg"
        cv2.imwrite(enhanced_image_path, final_image)
        return enhanced_image_path

    def perform_ocr_and_get_json(image_path):
        result = ocr.ocr(image_path, cls=True)
        def is_same_row(box1, box2, row_threshold=10):
            _, y1, _, y2 = box1[0][1], box1[2][1], box2[0][1], box2[2][1]
            return abs(y1 - y2) < row_threshold
        rows = []
        current_row = []
        for line in result[0]:
            box = line[0]
            text = line[1][0]
            confidence = line[1][1]
            if current_row and not is_same_row(current_row[-1][0], box):
                rows.append(current_row)
                current_row = []
            current_row.append((box, text, confidence))
        if current_row:
            rows.append(current_row)
        for row in rows:
            row.sort(key=lambda x: x[0][0][0])
        column_headers = [item[1] for item in rows[0]]
        data = []
        for row in rows[1:]:
            row_data = {}
            for i, (box, text, confidence) in enumerate(row):
                if i < len(column_headers):
                    row_data[column_headers[i]] = {
                        "text": text,
                        "confidence": confidence,
                        "bounding_box": box
                    }
            data.append(row_data)
        json_file_path = './bounding_box_data_with_text.json'
        with open(json_file_path, 'w') as json_file:
            json.dump(data, json_file, indent=4)
        return json_file_path

    resized_image_path = resize_to_resolution(img_path, output_image_path, resolution)
    enhanced_image_path = denoise_image(resized_image_path)
    if enhanced_image_path:
        json_file_path = perform_ocr_and_get_json(enhanced_image_path)
        return json_file_path
    else:
        return {"error": "Image processing failed"}

# FastAPI endpoint to handle image upload and return OCR data as JSON
@app.post("/upload-image/")
async def upload_image(image: UploadFile = File(...)):
    try:
        # Save the uploaded image to a temporary file location
        file_location = f"temp_{image.filename}"
        async with aiofiles.open(file_location, "wb") as file_object:
            content = await image.read()
            await file_object.write(content)
        
        # Log image details for debugging
        print(f"Image saved at {file_location}")

        # Run the image processing pipeline (this returns the JSON file path)
        ocr_json_file = process_image_pipeline(file_location, "output_image.jpg", (3840, 2160))  # Example: 4K resolution
        
        # Log if the OCR pipeline is successful
        print(f"Processed OCR, result saved at {ocr_json_file}")

        # Read the JSON file and load its content
        with open(ocr_json_file, 'r') as json_file:
            ocr_json_content = json.load(json_file)  # Load the content of the JSON file
        
        # Clean up the uploaded file
        os.remove(file_location)
        
        # Return the JSON content as a response
        return JSONResponse(content=ocr_json_content)
    
    except Exception as e:
        # Print the error for debugging
        print(f"Error: {str(e)}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

# Function to run the server
def run_server():
    uvicorn.run(app, host="0.0.0.0", port=8000)

# Expose the app using ngrok
public_url = ngrok.connect(8000)
print(f"FastAPI server public URL: {public_url}")

# Start the API server in a separate thread
server_thread = threading.Thread(target=run_server)
server_thread.start()

# Wait for a KeyboardInterrupt to stop the server
try:
    while True:
        pass  # Keep the main thread alive
except KeyboardInterrupt:
    print("Server stopped.")
    ngrok.disconnect(public_url)  # Clean up ngrok tunnel
    os.kill(os.getpid(), signal.SIGINT)  # Stop the server thread