# Conversational_chatbot

Methods used

1. Text is classified using OpenAI Chain(create_tagging_chain) into  "mental","therapy" ,"anxious","depressed","hurt","stress",'addiction', "weather related","Remainder","Play a video","Play a game","Play a music","Tell a joke", "general knowledge question"

2. If classified into "doctor","mental","therapy" ,"anxious","depressed","hurt","stress",'addiction', using the LLMChain and Huggingface API

3. If weather related then weather API(Free is used)

4. If remainder, the date is segmented into start and end datetime then added to Google Calender


How to use it?
Step 1: Setup the env file with the required keys
Step 2: Create and environment and install the requirements.txt packages
Step 3: Run the streamlit using: streamlit run server.py
