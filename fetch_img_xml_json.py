######### Fetching
import os
import json
import xml.etree.ElementTree as ET


from langchain_core.messages import HumanMessage

# def fetch_stored_images(directory, session_id):
#     """
#     Fetches stored images from the specified directory based on the session ID.
#     """
#     image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', ".PNG"]
#     image_files = []

#     for root, dirs, files in os.walk(directory):
#         for file in files:
#             if any(file.lower().endswith(ext) for ext in image_extensions):
#                 # Check if the file belongs to the given session ID
#                 if file.split("_")[0] == session_id:
#                     image_files.append(os.path.join(root, file))
#     return image_files



def fetch_stored_xml_json(directory, session_id):
    """
    Fetches and processes stored XML/JSON files from the specified directory based on the session ID.
    """
    combined_text = "XML or JSON files for Reference:\n"
    point_number = 1

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.startswith(session_id):
                filepath = os.path.join(root, file)

                # Process JSON files
                if file.endswith('.json'):
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                        text = json.dumps(data, indent=2)

                # Process XML files
                elif file.endswith('.xml'):
                    tree = ET.parse(filepath)
                    root = tree.getroot()
                    text = ET.tostring(root, encoding='unicode')

                else:
                    text = "Not Found"

                # Append to combined text
                combined_text += f"{point_number}. {text}\n"
                point_number += 1
    
    return [HumanMessage(content= combined_text)]
