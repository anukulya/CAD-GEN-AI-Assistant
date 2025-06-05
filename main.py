from chatbot import graph, fetch_previous_messages, add_new_conversation
print("\n\n------------------------>  GRAPH IMPORTED  <-----------------------\n\n")

# ====================================================================================

from db_config import app, db
from flask_restful import Resource, Api, reqparse
import werkzeug
from langchain_core.messages import HumanMessage, AIMessage
import os
import json
import xml.etree.ElementTree as ET

# Initialize Flask-RESTful API
api = Api(app)

# Fetch Previous messages from session ID
def get_previous_messages(sess_id):
    previous_msgs_list = []
    previous_messages = fetch_previous_messages(sess_id)
    for conv in previous_messages:
        previous_msgs_list.append(HumanMessage(content=conv.user_input))
        previous_msgs_list.append(AIMessage(content=conv.response))
    return previous_msgs_list

# Collecting Uploaded images from Directory
def list_image_files(directory):
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', ".PNG"]
    image_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if any(file.lower().endswith(ext) for ext in image_extensions):
                image_files.append(os.path.join(root, file))
    return image_files


def save_and_process_files(xml_json_files_list, session_id):
    combined_text = "XML or JSON files for Reference:\n"
    point_number = 1

    for file in xml_json_files_list:
        filename = f"{session_id}_{file.filename}"
        filepath = os.path.join(app.config["XML_or_JSON_FOLDER"], filename)
        
        # Save the file
        file.save(filepath)
        
        # Process the file
        if filename.endswith('.json') or filename.endswith('.Json'):
            with open(filepath, 'r') as f:
                data = json.load(f)
                text = json.dumps(data, indent=2)
        elif filename.endswith('.xml'):
            tree = ET.parse(filepath)
            root = tree.getroot()
            text = ET.tostring(root, encoding='unicode')
        else:
            text = "File Not Supported"
        
        # Append to combined text
        combined_text += f"{point_number}. {text}\n"
        point_number += 1

    return combined_text


from image_utilities import get_str

# Https Request Handler
class UploadImageAndText(Resource):
    def post(self):
        
        # Parser and it's architecture
        parser = reqparse.RequestParser()
        parser.add_argument('Input_Image_Files', type=werkzeug.datastructures.FileStorage, location='files', required = False,action="append")
        parser.add_argument('XML_or_JSON_Files', type = werkzeug.datastructures.FileStorage, location='files', required=False, action = "append", help='XML file to be uploaded')
        parser.add_argument('User_Query', type=str, location='form', required=True, help="Text input is required")
        parser.add_argument("User_Session_Id", type=str, location="form", required=True, help= "User Session id Needed to keep track")
        args = parser.parse_args()
        
        # Getting Usee's Input
        image_file_list = args['Input_Image_Files']
        xml_json_files_list = args['XML_or_JSON_Files']
        user_query = args['User_Query']
        sess_id = args['User_Session_Id']

        msg1 = [HumanMessage(content= f"User's question: {user_query}")]
        
        # Storing of Images in a list based on if it's provided or needed to be fetched
        image_strs_list = list()
        if image_file_list:
            # If images are Provided in Request
            for i, image in enumerate(image_file_list):             
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{sess_id}_{image.filename}")
                image.save(image_path)
                image_strs_list.append(get_str(image))
                
        
        
        if xml_json_files_list:
            XML_or_JSON_Text = save_and_process_files(xml_json_files_list, sess_id)

        # AI response to User's query
        if image_file_list and xml_json_files_list:
            # print("\nMAIN 1\n")
            response_state = graph.invoke({"messages":msg1,
                                 "input_images": image_strs_list,
                                 "xml_json_text" : XML_or_JSON_Text,
                                 "sess_id" : sess_id,
                                 "new_imgs_added":True,
                                 "new_xml_json_added":True,
                                 },
                                 config={"configurable": {"thread_id" : f"{sess_id}"}})

        elif image_file_list:
            # print("\nMAIN 2\n")
            response_state = graph.invoke({"messages":msg1,
                                    "input_images": image_strs_list,
                                    "sess_id" : sess_id,
                                    "new_imgs_added":True,
                                    "new_xml_json_added":False},
                                    config={"configurable": {"thread_id" : f"{sess_id}"}}) 

        elif xml_json_files_list:
            # print("\nMAIN 3\n")
            response_state = graph.invoke({"messages":msg1,
                                 "xml_json_text" : XML_or_JSON_Text,
                                 "sess_id" : sess_id,
                                 "new_imgs_added":False,
                                 "new_xml_json_added":True},
                                 config={"configurable": {"thread_id" : f"{sess_id}"}}) 

        else:
            # print("\nMAIN 4\n")
            response_state = graph.invoke({"messages":msg1,
                                "sess_id" : sess_id,
                                "new_imgs_added":False,
                                "new_xml_json_added":False,},
                                 config={"configurable": {"thread_id" : f"{sess_id}"}})

        
        
        response = response_state['messages'][-1].content
        # response = "temp OK"
        
        # # Store the conversation
        # new_conversation = Conversation(user_input=user_query, response=response, session_id = sess_id)
        # db.session.add(new_conversation)
        # db.session.commit()

        # show_database()
        return {"user question": user_query, "message": response}, 200

# Adding route to call the Post Request
api.add_resource(UploadImageAndText, '/upload')

@app.route("/")
def home():
    return "<h1>HOME PAGE</h1>"

if __name__ == "__main__":
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'],exist_ok=True)
    if not os.path.exists(app.config['XML_or_JSON_FOLDER']):
        os.makedirs(app.config['XML_or_JSON_FOLDER'],exist_ok=True)
    app.run(debug= True)


