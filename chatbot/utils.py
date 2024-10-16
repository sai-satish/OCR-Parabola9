import uvicorn
from pyngrok import ngrok

# Function to run the FastAPI server
def run_server(app):
    uvicorn.run(app, host="0.0.0.0", port=8000)

# Function to expose app via ngrok
def expose_via_ngrok():
    public_url = ngrok.connect(8000)
    print(f"FastAPI server public URL: {public_url}")
    return public_url
