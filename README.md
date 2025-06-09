# CAD GEN AI Assistant

A Flask-based RESTful API for a multi-modal chatbot that processes user queries, images, and XML/JSON files. The assistant leverages AI to answer questions based on user input and uploaded files.

## Features

- Accepts user queries via REST API.
- Supports uploading multiple images and XML/JSON files.
- Processes and stores uploaded files.
- Integrates with an AI model to generate responses.
- Maintains conversation history by session ID.

## Requirements

- Python 3.8+
- Flask
- Flask-RESTful
- Werkzeug
- langchain_core
- Other dependencies as required by your environment

## Setup

1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure the following folders in your environment or `app.config`:
   - `UPLOAD_FOLDER`: Directory for uploaded images.
   - `XML_or_JSON_FOLDER`: Directory for uploaded XML/JSON files.

## Running the Application

```bash
python main.py
```

The server will start on `http://127.0.0.1:5000/` by default.

## API Usage

### POST `/upload`

Upload images, XML/JSON files, and a user query.

#### Form Data

- `Input_Image_Files`: (optional) One or more image files.
- `XML_or_JSON_Files`: (optional) One or more XML or JSON files.
- `User_Query`: (required) The user's question.
- `User_Session_Id`: (required) Session identifier.

#### Example using `curl`

```bash
curl -X POST http://127.0.0.1:5000/upload \
  -F "Input_Image_Files=@path/to/image1.png" \
  -F "XML_or_JSON_Files=@path/to/file1.xml" \
  -F "User_Query=What is shown in the image?" \
  -F "User_Session_Id=session123"
```

#### Response

```json
{
  "user question": "What is shown in the image?",
  "message": "AI-generated response here"
}
```

## Project Structure

- `main.py` - Main Flask application and API logic.
- `db_config.py` - Database and Flask app configuration.
- `chatbot.py` - AI and conversation logic.
- `image_utilities.py` - Image processing utilities.

## License

This project is for educational purposes.
