# OCR-Based Table Analysis and Question Answering System

## Project Overview

This project leverages Optical Character Recognition (OCR) technology to extract text from images, particularly from tables, and provides question-answering capabilities based on the extracted data. By combining image processing techniques and natural language processing (NLP) models, the system automates the extraction of valuable information from tabular data and enables users to query this information dynamically.

### Key Features:
- **Image Processing**: Used OpenCV for techniques like Image Gray Scaling, Image Downsizing, and Image Enhancement to improve accuracy and reduce computation costs.
- **JSON Extraction**: Used PaddlePaddle AI to extract data from images and convert the extracted data into a structured JSON format.
- ### OCR Combination:
  We combined EasyOCR and PaddleOCR to enhance the accuracy of text extraction. EasyOCR identifies the location of text more accurately, while PaddleOCR excels at reading the content. EasyOCR is specifically used to identify bounding boxes, and with the help of these boxes, we crop each section of the image and pass it to PaddleOCR for detailed content extraction.
- **Question Answering**: Implemented using the `distilbert-base` NLP model, which allows users to query the data extracted from the images.
- **Table Analysis**: The system is capable of understanding and analyzing tabular data from images, automating data extraction processes.

## Architecture

1. **Image Processing**: 
   - We preprocess the images using OpenCV to enhance the quality of the image and reduce computational overhead. This includes steps like gray scaling, downsizing, and enhancement.
   
2. **Data Extraction**:
   - PaddlePaddle AI is used to extract text from the image and convert it into a structured JSON format, allowing for easier data manipulation and query processing.

3. **Model Integration**:
   - The extracted JSON data is fed into a custom NLP model. This equips the model with the necessary context to analyze the contents of the image and extract meaningful information.
   
4. **Interactive Question Answering**:
   - We used the `distilbert-base` model to create an interactive chatbot that answers users' queries based on the uploaded image's contents.

## Project Structure

```bash
OCR-Parabola9/
├── nextjs-app/              # Next.js frontend app
│   └── pages/               # UI pages for image upload and chatbot interaction
│   └── components/          # React components for the UI
│   └── api/                 # API calls to interact with backend
├── chatbot/                 # Python backend for FastAPI and model processing
│   ├── main.py              # Main FastAPI file
│   ├── qa.py                # QA related functionality
│   ├── ocr_processing.py    # Image processing and OCR functions
│   └── utils.py             # Utility functions (like server-related functions)
├── input-images/            # Folder for storing input images for OCR processing
├── sample1-out/             # Folder for storing output from Sample 1 test cases
├── sample2-out/             # Folder for storing output from Sample 2 test cases
├── sample3-out/             # Folder for storing output from Sample 3 test cases
└── README.md                # Project documentation

```
## How to Run the Project
 **Clone the Repository**:
```bash
git clone https://github.com/sai-satish/OCR-Parabola9.git
cd OCR-Parabola9
```
## Running the Next.js Application
1. **Navigate to the nextjs-app folder**:
   ```bash
   cd nextjs-app
   ```
2. **Install dependencies**:
   ```bash
   npm install
   ```
3. **Run the Next.js app**:
   ```bash
   npm run dev
   ```
4. The app will be available at http://localhost:3000.
## Running the Python Backend
1. **Navigate to the chatbot folder**:
   ```bash
   cd chatbot
   ```
2. **Start the FastAPI server by running main.py**:
   ```bash
   python main.py
   ```
3. **Expose the server using ngrok**:
   ```bash
   !ngrok authtoken <your-ngrok-auth-token>
   ```
4. **Get the ngrok public URL and update the frontend to use this URL for API requests.**
## Managing Ports
If you need to stop a process running on a specific port (e.g., 8000), use the following commands:

## List all processes running on port 8000:
```bash
!lsof -i :8000
```
## kill the process
```bash
!kill -9 <process-id>
```
## Backend Files
1. Image_conversion.py: Handles image processing and conversion tasks.
2. Image_upload.py: Manages the image upload functionality.
3. integrated.py: Combines the image processing and model functionalities.
## Future Enhancements
1. Improve the model to handle more complex table structures.
2. Implement multi-language support for OCR and NLP processing.
3. Optimize the system for faster image processing and query handling.
