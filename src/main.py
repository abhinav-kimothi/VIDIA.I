import streamlit as st
from configparser import ConfigParser
from PIL import Image
import openai
import os
from utils import *



#### Create config object and read the config file ####
config_object = ConfigParser()
config_object.read("vidia-config.ini")

#### Initialize variables and reading configuration ####
logo=Image.open(config_object["IMAGES"]["logo_address"]) #### Logo for the sidebar
favicon=Image.open(config_object["IMAGES"]["favicon_address"]) #### Favicon

models=config_object["MODEL"]["model"] ##### model for GPT call
greeting=config_object["MSG"]["greeting"] ###### initial chat message
hline=Image.open(config_object["IMAGES"]["hline"]) ###### image for formatting landing screen
uploaded=None ##### initialize input document to None



#### Set Page Config ####
st.set_page_config(layout="wide", page_icon=favicon, page_title="VIDIA.I")

#### Set Logo on top sidebar ####
st.sidebar.image(hline)
c1,c2,c3=st.sidebar.columns([1,3,1])
c2.image(logo)
st.sidebar.image(hline)

#### First Condition - Check if OpenAI Key is present, otherwise open the key input form ####
if check_key():

    #### If Key is present, check if Key is valid. If valid, open input radio buttons, else show 'Change API' button ####
    if validate_key():
        st.sidebar.image(hline)
        input_choice, uploaded=input_selector()
        st.sidebar.image(hline)
    else:
        if st.sidebar.button("Change API Key",key="Uno"):
            input_key()

#### If input mode has been chosen and link/doc provided, convert the input to text ####
if uploaded is not None and uploaded !="":
    with st.spinner("#### Parsing data"):
        words, pages, string_data,succeed,token=check_upload(uploaded=uploaded,input_choice=input_choice)
    #db=create_embeddings(string_data)
        #### Count number of words and pages read ####
    if token>2500:

        db,pages=create_embeddings(string_data)

    col1, col2, col3=st.sidebar.columns(3)
    col1.markdown("###### :violet[Tokens Read:] :blue["+str(token)+"]")
    col2.write("###### :violet[Words Read:] :blue["+str(words)+"]")
    col3.markdown("###### :violet[Embeddings Created:] :blue["+str(pages)+"]")



    #### If large document, cut down since GPT takes only 4000 tokens as input ####
    #### This will be addressed when indexing is introduced                    ####


    #### Splitting page into tabs ####
    tab1, tab2, tab3=st.tabs(["|__QnA__ 🔍|","|__Document Summary__ 📜|","|__About VIDIA__ 🎭|"])

    with tab1: #### The QnA Tab
        if succeed=="Failure":
            st.error("#### The input document might be corrupted or the extraction of information from the input link failed. Try uploading a new document or entering a different link")
        else:
            initialize_chat("👋")  #### Initialize session state variables for the chat ####

            #### Put user question input on top ####
            with st.form('input form',clear_on_submit=True):
                inp=st.text_input("Please enter your question below and hit Submit. Please note that this is not a chat, yet 😉", key="current")
                submitted = st.form_submit_button("Submit")

            if not submitted: #### This will render the initial state message by VIDIA when no user question has been asked ####
                with st.container(): #### Define container for the chat
                    render_chat() #### Function renders chat messages based on recorded chat history
            if submitted:
                #### This commented code block uses chatgpt model turbo-3.5 ####
                #### mdict=create_dict_from_session()
                #### if mdict !=[]:
                ####     response_text=q_response_chat(inp,info,mdict)
                ################################################################
                if token>2500:
                    with st.spinner("Finding most relevant section of the document..."):
                        info=search_context(db,inp)
                    with st.spinner("Preparing response..."):
                        final_text=q_response(inp,info,models)
                else:
                    info=string_data
                    with st.spinner("Scanning document for response..."): #### Wait while openai response is awaited ####
                        final_text=q_response(inp,info,models) #### Gets response to user question. In case the question is out of context, gets general response calling out 'out of context' ####
                
                    #### This section creates columns for two buttons, to clear chat and to download the chat as history ####
                col1,col2,col3,col4=st.columns(4)
                col1.button("Clear History",on_click=clear,type='secondary') #### clear function clears all session history for messages #####
                f=write_history_to_a_file() #### combines the session messages into a string ####
                col4.download_button("Download History",data=f,file_name='history.txt')

                with st.container():
                        chatbot(inp,final_text) #### adds the latest question and response to the session messages and renders the chat ####

    with tab2: #### Document Summary Tab ####
        col1, col2, col3=st.columns(3)
        if token>2500:
            with st.spinner("Finding most relevant section of the document..."):
                    info=search_context(db,"What is this about?")
        else:
            info=string_data
        if st.button("Document Summary"):

                    st.markdown("#### Summary")
                    st.write(summary(info,models))

                    st.markdown("#### Talking Points")
                    st.write(talking(info,models))

                    st.markdown("#### Sample Questions")
                    st.write(questions(info,models))

    with tab3:  #### About Tab #####
        st.image(hline)
        col1, col2, col3,col5,col4=st.columns([10,1,10,1,10])

        with col1:
            first_column()
        with col2:
            st.write(" ")
        with col3:
             second_column()
        with col5:
            st.write(" ")
        with col4:
             third_column()
        st.image(hline)
else: #### Default Main Page without Chat ####
    st.image(hline)
    heads()
    st.image(hline)
    col1, col2, col3,col5,col4=st.columns([10,1,10,1,10])
    with col1:
        first_column()
    with col2:
        st.write("")
        #st.image(vline,width=4)
    with col3:
        second_column()
    with col5:
        st.write("")
        #st.image(vline,width=4)
    with col4:
        third_column()
    st.image(hline)

#### Contact Information ####
with st.sidebar.expander("📮 __Contact__"):
    st.image(hline)
    contact()
    st.image(hline)
st.sidebar.image(hline)

#### Reset Button ####
if st.sidebar.button("🆘 Reset Application",key="Duo",use_container_width=True):
    openai.api_key=None
    del os.environ["OPENAI_API_KEY"]
    st.experimental_rerun()
st.sidebar.image(hline)
 






