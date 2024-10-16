"use client";
import "./globals.css";
import ChatBot from './components/ChatBot';
import { useState } from 'react';

export default function Page() {
  const [uploadedFile, setUploadedFile] = useState(null);  // Store the file for preview
  const [jsonData, setJsonData] = useState(null);  // To store JSON data from OCR

  const handleImageUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) {
      console.error('No file selected');
      return;
    }

    console.log('File selected:', file);  // Debugging: Log file info
    const formData = new FormData();
    formData.append("image", file);

    // Log environment variable value
    console.log('Ngrok URL:', process.env.NEXT_PUBLIC_NGROK_URL);  // Ensure env variable is correct
    const ngrokUrl = `${process.env.NEXT_PUBLIC_NGROK_URL}/upload-image/`;

    try {
      console.log('Sending POST request to:', ngrokUrl);
      const response = await fetch(ngrokUrl, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorMsg = await response.text(); // Capture the error message
        console.error('Network response was not ok:', errorMsg);
        throw new Error(`Error: ${response.status} - ${errorMsg}`);
      }

      console.log('Image uploaded successfully:', response);
      const data = await response.json();  // Get JSON response
      console.log('OCR response data:', data);  // Log the OCR data
      setJsonData(data);  // Store the JSON data from OCR

      // Store the uploaded file URL for preview
      const fileURL = URL.createObjectURL(file);
      setUploadedFile(fileURL);

    } catch (error) {
      console.error('Error uploading image:', error);
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-between bg-gradient-to-r from-blue-50 to-indigo-100 p-4">
      {/* Header Section */}
      <header className="w-full text-center py-5 bg-white shadow-lg mb-4">
        <h1 className="text-3xl font-bold text-indigo-600">Welcome to the AI Bot</h1>
      </header>

      {/* Main Section */}
      <main className="w-full max-w-7xl flex-grow flex flex-col lg:flex-row justify-between items-start lg:space-x-8">
        {/* Image Upload Section */}
        <section className="w-full lg:w-2/3 bg-white rounded-lg p-6 shadow-md">
          <h2 className="text-xl font-semibold text-gray-700 mb-4">Upload an Image for Analysis</h2>
          <input
            type="file"
            accept="image/*"
            onChange={handleImageUpload}
            className="block w-full text-sm text-gray-500
            file:mr-4 file:py-2 file:px-4
            file:rounded-full file:border-0
            file:text-sm file:font-semibold
            file:bg-indigo-50 file:text-indigo-700
            hover:file:bg-indigo-100"
          />
          {uploadedFile && (
            <div className="mt-4">
              <img src={uploadedFile} alt="Uploaded preview" className="max-w-full rounded-md shadow-lg" />
            </div>
          )}
        </section>

        {/* Chatbot Section */}
        <aside className="w-full lg:w-1/3 mt-8 lg:mt-0 bg-white rounded-lg p-6 shadow-md">
          <h2 className="text-xl font-semibold text-gray-700 mb-4">ChatBot Assistant</h2>
          <ChatBot jsonData={jsonData} />  {/* Pass the JSON data to the chatbot */}
        </aside>
      </main>

      {/* Footer Section */}
      <footer className="w-full text-center py-4 mt-8 bg-white shadow-lg">
        <p className="text-sm text-gray-500">© 2024 AI Bot. All rights reserved.</p>
      </footer>
    </div>
  );
}
