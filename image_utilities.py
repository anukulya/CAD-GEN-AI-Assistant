# Converts Images into String, Fetch stored images

import os
from PIL import Image 
import io
import base64
from langchain_core.messages import HumanMessage

def get_str(uploaded_file):
    image_obj = Image.open(uploaded_file)
    buffered = io.BytesIO()
    image_obj.save(buffered, format= image_obj.format)
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return img_str

def generate_imgs_msgs_list(imgs_list):
    image_msgs_list = list()
    for i, img_url in enumerate(imgs_list):
        img_msg = HumanMessage(
            content=[
                {"type": "text", "text": f"Image {i+1}"},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{img_url}"},
                },
            ],
        )
        image_msgs_list.append(img_msg)

    return image_msgs_list

def fetch_stored_images(directory, session_id):
    """
    Fetches stored images from the specified directory based on the session ID,
    converts them into base64 strings, and returns them as HumanMessage objects.

    Args:
        directory (str): The directory to search for images.
        session_id (str): The session ID to filter the images.

    Returns:
        list: A list of HumanMessage objects containing the image data.
    """
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', ".PNG"]
    image_files = []

    # Collect image files based on session ID
    for root, dirs, files in os.walk(directory):
        for file in files:
            if any(file.lower().endswith(ext) for ext in image_extensions):
                # Check if the file belongs to the given session ID
                if file.split("_")[0] == session_id:
                    image_files.append(os.path.join(root, file))

    # Convert image files to base64 strings
    base64_images = [get_str(image_file) for image_file in image_files]

    # Generate HumanMessage objects from base64 strings
    image_msgs_list = generate_imgs_msgs_list(base64_images)

    return image_msgs_list