import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
import streamlit as st
from langchain.prompts import ChatPromptTemplate
from langchain.chains import create_tagging_chain,create_tagging_chain_pydantic

from langchain_openai import ChatOpenAI
import datetime
import os.path
import uuid
import time
import re
from datetime import datetime, timedelta
import os 
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from langchain_community.llms import HuggingFaceEndpoint
from langchain_community.llms import HuggingFaceHub


import openai
from langchain.prompts import (
    PromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate,
)

from langchain.chains import LLMChain

import dotenv
from server.Conversational_chatbot.preprocessing import PreProcessingRemainder,PreProcessingWeather,FinalOutput


remainder=PreProcessingRemainder()
weather=PreProcessingWeather()
finaloutput=FinalOutput()


dotenv.load_dotenv()

HUGGINGFACEHUB_API_TOKEN = os.environ.get('HUGGINGFACEHUB_API_TOKEN')

llm=ChatOpenAI(temperature=0,model='gpt-3.5-turbo-0613')

SCOPES = ['https://www.googleapis.com/auth/calendar']


#########################################################################################


def create_unique_request_id():
        unique_id = str(uuid.uuid4())
        timestamp_ms = int(time.time() * 1000)
        request_id = f'{unique_id}-{timestamp_ms}'
        return request_id

def remainder_pushing_to_google_calendar(title,text,start_time,end_time):

    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            flow.redirect_uri = 'http://localhost:8080' 
            creds = flow.run_local_server(port=8080)  
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

  
    calendar_id="primary"

    try:
        service = build('calendar', 'v3', credentials=creds)
       
        event = {
            'summary': title,
            'description': text,
            'start': {
                'dateTime': start_time,
                'timeZone': 'Asia/Kolkata', 
            },
            'end': {
                'dateTime': end_time,
                'timeZone': 'Asia/Kolkata',
            },
            'reminders': {'useDefault': False,'overrides': [{'method': 'popup', 'minutes': 30}]}}
        calendar_id = 'primary'
        event = service.events().insert(calendarId=calendar_id, body=event).execute()
        print(f"Event created:{event.get('htmlLink')}")
        #database.push_reminder_to_database(request_id,title,text,start_time,end_time,action_taken)
        return event
    
    except HttpError as error:
        print(error)



from langchain.chains import LLMChain
from langchain.schema import (
    SystemMessage,
    HumanMessage,
    AIMessage)


def question_to_a_therapist_only_once(text,mood): #no storage in vector database

    llm = HuggingFaceHub(repo_id='tiiuae/falcon-7b-instruct', huggingfacehub_api_token=HUGGINGFACEHUB_API_TOKEN)
    question ="As a therapist respond empathetically and effectively to this statment: "+text+"I am right now feeling "+mood+'Please dont give explanation of the output you give'
    template = """Question: {question}
    Answer: Let's go through this togethere."""

    prompt = PromptTemplate(template=template, input_variables=["question"])    
    llm_chain = LLMChain(prompt=prompt, llm=llm)
    
    result=llm_chain.invoke(question)
    print(result)
    output=result['text']
    return output


def question_to_a_therapist_multiple_chat(text,mood): #not done-store in vector database and memory
    question = +text+"I am right now feeling "+mood

    messages = [
        SystemMessage(content="You are an excellent therapist who responds empathetically and effectively.Please dont give explanation of the output you give"),
        HumanMessage(content=question)
    ]

    return messages


def generalknowledge_only_once(text,mood):
    llm = HuggingFaceHub(repo_id='tiiuae/falcon-7b-instruct', huggingfacehub_api_token=HUGGINGFACEHUB_API_TOKEN)
    question ="As a knowledge hub give answer to the question: "+text
    template = """Question: {question}
    Answer: Let's go through this togethere."""

    prompt = PromptTemplate(template=template, input_variables=["question"])    
    llm_chain = LLMChain(prompt=prompt, llm=llm)
    
    result=llm_chain.invoke(question)
    print(result)
    output=result['text']
    output=finaloutput.remove_last_user(output)
    return output


############classify################################################################

def classify_using_sentence_embedding(): #use sentence emdedding and nearest neighbor
    pass


def classify_using_lanchain(input):
    schema = {
    "properties": {
        "mood": {
            "type": "string",
            "enum": ['happy','sad','angry','anxious','scared','hurt'],
            "description": "describes what is the mood as per the linguistic pattern",
        },
        "language": {
            "type": "string",
            "enum": ["spanish", "english", "french", "german", "italian"],
        },
        "Task": {
            "type": "string",
            "enum": [ "mental","therapy" ,"anxious","depressed","hurt","stress",'addiction', "weather related","Remainder","Play a video","Play a game","Play a music","Tell a joke", "general knowledge question"],
            "description": "describes what is the task asked to do in the text",
        },

    },
    "required": ["mood", "language", "Task"],}
    chain = create_tagging_chain(schema, llm)
    result=chain.invoke(input)
    print(result)
    return result['input'],result['text']['mood'],result['text']['language'],result['text']['Task']


####################send the the api ##########################################

def send_to_respective_API(text,category,mood):

    if category=='Remainder':
        title,date_time,end_time=remainder.find_title_datetime(text)
        if end_time is not None:
            remainder_pushing_to_google_calendar(title,text,date_time,end_time)
            return 'Success'
        else:
            return None



    elif category in ['therapist', 'depressed', 'hurt', 'stress', 'addiction', 'anxious','therapy','mental']:
        print("category",category)
        output=question_to_a_therapist_only_once(text,mood)
        if output is not None:
            return output


    elif category=='weather related':
        output=weather.fetch_weather()
        return output


    elif category=='Play a video': #yet to build
        print("category",category)
        return category
    

    elif category=='Play a game': #yet to build
        print("category",category)
        return category

    elif category=='Play a music':
        print("category",category)
        return category
    
    elif category in ['general knowledge question','Tell a joke']:
        output=generalknowledge_only_once(text,mood)
        print(output)
        return output

#######################Streamlit home page##############################
if 'result_of_task' not in  st.session_state:
        st.session_state.result_of_task=''

st.write("Secret Key", st.secrets["openai_secret_key"])

def main():
    st.title("Aneesha's Chatbot App")
    st.text("Welcome to Aneesha's Chatbot. I want to help you with your questions, so ask away!")
    text = st.text_area("Enter your text here:")
    
    if st.button("Submit"):
        _,mood,_,category=classify_using_lanchain(text)
        st.session_state.result_of_task=send_to_respective_API(text,category,mood)
        if st.session_state.result_of_task!='':
            result = finaloutput.final_output(st.session_state.result_of_task,category)
            st.write(result)
        else:
            st.warning("Please enter some text.")

if __name__ == "__main__":
    main()

#streamlit run server.py
