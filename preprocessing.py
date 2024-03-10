
import dotenv, requests, uuid, time, re, os
from datetime import datetime, timedelta
import pytz, dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate
from langchain.chains import LLMChain
from langchain.prompts.few_shot import FewShotPromptTemplate
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferWindowMemory

dotenv.load_dotenv()
openai = ChatOpenAI(model_name='gpt-3.5-turbo')
WEATHER_API = os.environ.get('WEATHER_API')
CITY = os.environ.get('CITY')

class PreProcessingRemainder:

    def __init__(self):
        pass

    def find_output_frok_fewshot_template(self, examples):
        example_template = '\n User:{sentence}\nAI: {title},/n/n/n/n,{datetime}\n'
        example_prompt = PromptTemplate(input_variables=['query', 'answer'],template=example_template)
        prefix = 'The following are excerpts from conversations with an AI assistant. The assistant is known for cutting the sentence into title and datetime.Make sure to remove the timezone always .Here are some\n        examples:\n        '
        suffix = '\n User: {sentence}\nAI:'
        few_shot_prompt_template = FewShotPromptTemplate(examples=examples,
          example_prompt=example_prompt,
          prefix=prefix,
          suffix=suffix,
          input_variables=['sentence'],example_separator=',/n/n/n/n,')
        chain = LLMChain(llm=openai, prompt=few_shot_prompt_template)
        return chain

    def find_title_datetime(self, text):
        examples = [
         {'sentence':'Set a reminder for a meeting at 2 AM tommorow', 
          'title':'Meeting reminder',  'datetime':'2023-09-12T02:00:00'},
         {'sentence':'Remind me of a 3 PM conference call', 
          'title':'Conference call reminder',  'datetime':'2023-09-11T15:00:00'},
         {'sentence':'Create an reminder for lunch at 12:30 PM', 
          'title':'Lunch reminder',  'datetime':'2023-09-11T12:30:00'},
         {'sentence':"Schedule a doctor's appointment for tomorrow at 10:30 AM", 
          'title':'Doctors appointment reminder',  'datetime':'2023-09-12T10:30:00'},
         {'sentence':'Create a reminder for a project review at 3:00 PM on Friday', 
          'title':'Project review reminder',  'datetime':'2023-09-15T10:30:00'},
         {'sentence':'Set up a meeting with John for next Monday at 9 AM', 
          'title':'Meeting with John reminder',  'datetime':'2023-09-15T10:30:00'},
         {'sentence':'Remind me to call the client at 4:45 PM on Wednesday', 
          'title':'Meeting with client reminder',  'datetime':'2023-09-13T14:45:00'},
         {'sentence':'Plan a conference call with the team for 2:30 PM on the 20th of this month', 
          'title':'Conference call reminder',  'datetime':'2023-09-20T14:30:00'}]
        # text = 'Schedule a meeting at 4:20pm on 10th March'
        chain = self.find_output_from_fewshot_template(examples)
        result = chain.invoke(text)
        print(result)
        title_date_time = result['text'].split(',/n/n/n/n,')
        title = title_date_time[0]
        date_time = title_date_time[1]
        date_time = datetime.strptime(date_time, '%Y-%m-%dT%H:%M:%S')
        time_zone = pytz.timezone('Asia/Kolkata')
        date_time = time_zone.localize(date_time)
        end_time = date_time + timedelta(minutes=30)
        date_time = date_time.strftime('%Y-%m-%dT%H:%M:%S%Z')
        end_time = end_time.strftime('%Y-%m-%dT%H:%M:%S%Z')
        return (
         title, date_time, end_time)


class PreProcessingWeather:

    def __init__(self):
        pass

    def fetch_weather():
        url = f"http://api.weatherapi.com/v1/current.json?key={WEATHER_API}&q={CITY}"
        response = requests.get(url)
        if response.status_code == 200:
            res = response.json()
            temp_c = res['current']['temp_c']
            temp_f = res['current']['temp_f']
            condition = res['current']['condition']['text']
            return f"The temperature in Celsius and Fahrenheit of {CITY} are {temp_c} and {temp_f}. It is {condition} currently in {CITY}."
        print('Error:', response.status_code)


class FinalOutput:   #to customize each of the output as per the input

    def __init__(self):
        pass

    def remove_last_user(text):
        words = text.split()
        if words and words[-1] == "User":
            words.pop()
        result = ' '.join(words)

        return result

    def final_output(self, text, category):
        if category in ('therapist', 'depressed', 'hurt', 'stress', 'addiction', 'anxious','therapy', 'mental'):
            output =text
            print(text)
            return output

    
        elif category in ('weather'):
            print(text)
            output =text
            return output
        
        elif category in ['general knowledge question','Tell a joke']:
            print(text)
            output = text
            return output

        else:
            print('None')
            output = None
            return output
