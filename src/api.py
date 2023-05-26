'''
api.py contains all functions related to reading the OpenAI API key and checking if it is valid
'''


import openai ###### Import OpenAI library
import streamlit as st ###### Import Streamlit library
import os ###### Import os library for environment variables
from configparser import ConfigParser ###### Import ConfigParser library for reading config file to get model


#### Create config object and read the config file ####
config_object = ConfigParser() ###### Create config object
config_object.read("./vidia-config.ini") ###### Read config file
models=config_object["MODEL"]["model"] ##### model for GPT call

#### Check if OpenAI API key is present ####
#### this function checks if the key is present in the environment variables or in the .env file ####
#### if not present, it asks the user to input the key ####
#### if present, it checks if the key is valid ####
#### if not valid, it asks the user to input the key ####
#### if valid, it returns True ####
#### if not present, it returns False ####
#### if present but not valid, it returns False ####
def check_key(): ###### Check if OpenAI API key is present

    if openai.api_key: 
        #st.sidebar.info("OpenAI API key detected")
        return True ###### If key is present, return True
    elif os.path.exists(".venv") and os.environ.get("OPENAI_API_KEY") is not None:
        openai.api_key=os.environ["OPENAI_API_KEY"] 
        if validate_key(): 
            st.sidebar.success("OpenAI API key loaded from .env", icon="🚀")
            return True ###### If key is present, return True
        else:
            del os.environ['OPENAI_API_KEY']
            openai.api_key=None
            input_key()
            if openai.api_key:
                return True
            else:
                return False
    else:
        input_key()
        if openai.api_key:
            return True
        else:
            return False
    
def validate_key():
    try:
        r=openai.Completion.create(model=models, prompt="t.",max_tokens=5)
        #st.sidebar.success("API key validated")
        return True
    except:
        st.sidebar.error("API key invalid, please change the key")
        return False
    
def clear_key():
    openai.api_key=None

def input_key():

    openai.api_key=None
    with st.sidebar.form("API",clear_on_submit=True):
            api_key=st.text_input("Please enter your OpenAI API key",type='default')
            submit = st.form_submit_button("Enter")
    if submit:
        openai.api_key=api_key
        os.environ["OPENAI_API_KEY"]=api_key
        check_key()



