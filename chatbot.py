# Loading Local Vector DB and Initiating LLM
import os
from dotenv import load_dotenv
load_dotenv()   # Load environment variables from .env file                     
AZURE_DEPLOYMENT_NAME = os.getenv("AZURE_DEPLOYMENT_NAME")
AZURE_API_VERSION = os.getenv("AZURE_API_VERSION")

# ----------------------------------------------------------------------------------------

from langchain_core.messages import HumanMessage, AIMessage
from system_prompt_usecase4 import sys_prompt 

from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import AzureChatOpenAI


#------------------------------------------------------------------------------
llm_2 = AzureChatOpenAI(
    azure_deployment= AZURE_DEPLOYMENT_NAME,  # or your deployment
    api_version= AZURE_API_VERSION,  # or your api version
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    # other params...
)

#===========================================================================================

from db_config import app, db
from datetime import datetime

# Database Column Architecture
class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_input = db.Column(db.String, nullable=False)
    response = db.Column(db.String, nullable=False)
    session_id = db.Column(db.String, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Function to fetch previous messages by session ID
def fetch_previous_messages(session_id):
    previous_messages = Conversation.query.filter_by(session_id=session_id).all()
    previous_msgs_list = list()

    for conv in previous_messages:
        if conv.session_id == session_id:
            previous_msgs_list.append(HumanMessage(content= conv.user_input))
            previous_msgs_list.append(AIMessage(content= conv.response))
    return previous_msgs_list

    # return previous_messages

# Function to add a new conversation to the database
def add_new_conversation(user_input, response, session_id):
    new_conversation = Conversation(
        user_input=user_input,
        response=response,
        session_id=session_id
    )
    db.session.add(new_conversation)
    db.session.commit()

# ==========================================================================================


from image_utilities import generate_imgs_msgs_list, fetch_stored_images
from fetch_img_xml_json import fetch_stored_xml_json

class State(TypedDict):
    messages: Annotated[list, add_messages] 
    input_images : list[str]
    xml_json_text : str
    new_imgs_added : bool
    new_xml_json_added : bool
    sess_id : str 

def main_chatbot(state):
    # print(f"\n{state = }\n\n")
    print(f"{len(state['messages']) = }\n")
    # print(f"{state['messages'] = }\n{state['new_imgs_added'] = }\n{state['new_xml_json_added'] = }\n\n")
    # print(f"{state['xml_json_text'] = }\n\n")
    # state will always have first message as user's first query hence will not go in new session
    # Hence comparing it with 1

    if len(state['messages']) > 1:
        print("CONTINUED SESSION: ")

        messages_list = [("system", sys_prompt)]

        if state.get('new_imgs_added'):
            print("NEW IMAGES ADDED")
            messages_list.extend(generate_imgs_msgs_list(state['input_images']))
            state['new_imgs_added'] = False

        if state.get('new_xml_json_added'):
            print("NEW EXTRACTED TEXT ADDED")
            messages_list.extend([HumanMessage(content= state["xml_json_text"])])
            state['new_xml_json_added'] = False

    else:
        previous_messages_list = fetch_previous_messages(state["sess_id"]) 
        previous_imgs_msgs_list = [HumanMessage(content="Previously uploaded images for context:")] + fetch_stored_images(app.config['UPLOAD_FOLDER'], state["sess_id"])
        previous_xml_json_msgs_list = [HumanMessage(content="Previously uploaded xml/json files for context:")] + fetch_stored_xml_json(app.config["XML_or_JSON_FOLDER"], state["sess_id"])
      
        print("STARTING NEW SESSION:")
        print("FETCHED PREVIOUS MESSAGES\nFETCHED PREVIOUS IMAGES\nFETCHED PREVIOUS EXTRACTED TEXT")
        messages_list = [("system", sys_prompt)] + previous_imgs_msgs_list + previous_xml_json_msgs_list + previous_messages_list

        if state.get('new_imgs_added'):
            print("NEW IMAGES ADDED")
            image_msgs_list = generate_imgs_msgs_list(imgs_list=state['input_images'])
            messages_list += image_msgs_list 
            state['new_imgs_added'] = False
        
        if state.get('new_xml_json_added'):
            print("NEW EXTRACTED TEXT ADDED")
            xml_msgs_list = [HumanMessage(content= state["xml_json_text"])]
            messages_list += xml_msgs_list 
            state['new_xml_json_added'] = False

    messages_list += state["messages"]

    # print();print();print()
    # for msgs in messages_list:
    #     print(type(msgs), msgs); print()
    # print();print();print()

    response = llm_2.invoke(messages_list)
    print(f"RESPONSE GENERATED:\n{response = }")
    print("=x="*15);print()

    # Store the conversation
    new_conversation = Conversation(user_input=state['messages'][-1].content, response=response.content, session_id = state['sess_id'])
    db.session.add(new_conversation)
    db.session.commit()
    
    print(f"In the end STATE:\n{state['new_imgs_added'] = }\n{state['new_xml_json_added'] = }\n\n")
    return {"messages" : response}

graph_builder = StateGraph(State)
graph_builder.add_node("CHATBOT", main_chatbot)

graph_builder.add_edge(START, "CHATBOT")
graph_builder.add_edge("CHATBOT", END)

memory = MemorySaver()
graph = graph_builder.compile(checkpointer=memory)