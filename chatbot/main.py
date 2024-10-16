from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import aiofiles
import threading
import signal

# Import functions from other files
from chatbot.qa import answer_question, QARequest
from image_upload import process_image_pipeline
from chatbot.utils import run_server, expose_via_ngrok

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

# Define the API route to handle question answering
@app.post("/qa/")
def qa_endpoint(request: QARequest):
    return answer_question(request)

# FastAPI endpoint to handle image upload and return OCR data as JSON
@app.post("/upload-image/")
async def upload_image(image: UploadFile = File(...)):
    try:
        # Save the uploaded image to a temporary file location
        file_location = f"temp_{image.filename}"
        async with aiofiles.open(file_location, "wb") as file_object:
            content = await image.read()
            await file_object.write(content)
        
        # Run the image processing pipeline (returns the JSON file path)
        ocr_json_file = process_image_pipeline(file_location, "output_image.jpg", (3840, 2160))  # Example: 4K resolution
        
        # Read the JSON file and load its content
        with open(ocr_json_file, 'r') as json_file:
            ocr_json_content = json.load(json_file)
        
        # Clean up the uploaded file
        os.remove(file_location)
        
        return JSONResponse(content=ocr_json_content)
    
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

# Expose the app via ngrok
public_url = expose_via_ngrok()

# Start the API server in a separate thread
server_thread = threading.Thread(target=run_server, args=(app,))
server_thread.start()

# Wait for a KeyboardInterrupt to stop the server
try:
    while True:
        pass  # Keep the main thread alive
except KeyboardInterrupt:
    print("Server stopped.")
    ngrok.disconnect(public_url)
    os.kill(os.getpid(), signal.SIGINT)
    