import streamlit as st
from streamlit_chat import message
import pathlib
import pdfplumber
import openai
import requests
from bs4 import BeautifulSoup
from configparser import ConfigParser
import os
#import langchain
'''
#from langchain.document_loaders import YoutubeLoader
#from langchain.document_loaders import TextLoader


#from langchain.text_splitter import CharacterTextSplitter
#from langchain.chains import RetrievalQA
#from langchain.llms import OpenAI

#from langchain.indexes import VectorstoreIndexCreator
#from langchain.embeddings import OpenAIEmbeddings
#from langchain.vectorstores import FAISS


#def extract_YT(link):
#    address=link
#    loader = YoutubeLoader.from_youtube_url(address, add_video_info=True)
#    return loader.load()

#def query_response(documents):

#    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=5)
#    texts = text_splitter.split_documents(documents)

#    embeddings = OpenAIEmbeddings()
#    db = FAISS.from_documents(texts, embeddings)

#    retriever = db.as_retriever()
#    qa = RetrievalQA.from_chain_type(llm=OpenAI(openai_api_key="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"), chain_type="stuff", retriever=retriever)

#    resp=qa.run("what is this video about? Answer in detail and in an enthusiastic tone. End with a follow up question.")
'''

import pandas as pd
#import tiktoken
###
config_object = ConfigParser()
config_object.read("./vidia-config.ini")
models=config_object["MODEL"]["model"]
greeting=config_object["MSG"]["greeting"]
###




'''
Chat Rendering Functions
'''
### Initialisation function for the chat. Takes input for the first message.
def initialize_chat(bot_m=None):
        if 'history' not in st.session_state:
            st.session_state['history']=[]

        if 'pastinp' not in st.session_state:
            st.session_state['pastinp']=[]

        if 'pastresp' not in st.session_state:
            st.session_state['pastresp']=[bot_m]  

### Function for rendering chat
def render_chat():
    for i in range(0,len(st.session_state['pastresp'])-1):
        if st.session_state['pastresp'][len(st.session_state['pastresp'])-1-i]:
            message(st.session_state['pastresp'][len(st.session_state['pastresp'])-1-i],key=i,avatar_style='avataaars')  
        if st.session_state['pastinp'][len(st.session_state['pastinp'])-1-i]:
            message(st.session_state['pastinp'][len(st.session_state['pastinp'])-1-i], is_user=True,key=i+100,avatar_style='initials', seed="U")
     

    if st.session_state['pastresp'][0]:
        message(st.session_state['pastresp'][0],key=-99, avatar_style='avataaars')

### Function for adding the latest query and VIDIA response
def chatbot(query,response):

    st.session_state['pastinp'].append(query)
    st.session_state['pastresp'].append(response)
    render_chat()


'''
Input Data Extraction Functions
'''
### Extraction of text from inputs. Take the input object as parameter. Uses sub-functions for pdf and txt.
def extract_data(feed):
    if pathlib.Path(feed.name).suffix=='.txt':
        return extract_data_txt(feed)
    else:
        return extract_data_pdf(feed)

def extract_data_pdf(feed):
    text=""
    num=0
    words=0
    with pdfplumber.open(feed) as pdf:
        pages=pdf.pages
        for p in pages:
            text+=p.extract_text()
            num+=1
    words=len(text.split())
    return words, num, text

def extract_data_txt(feed):
    text=feed.read().decode("utf-8")
    words=len(text.split())
    num='NA'
    return words, num, text

def extract_page(link):
    address=link
    response=requests.get(address)
    soup = BeautifulSoup(response.content, 'html.parser')
    text=soup.get_text()
    lines = filter(lambda x: x.strip(), text.splitlines())
    website_text = "\n".join(lines)
    words=len(website_text.split())
    num=1
    return words, num, website_text

'''
#def extract_YT(link):
#    address=link
#    loader = YoutubeLoader.from_youtube_url(address, add_video_info=True)
#    text=str(loader.load()[0])
#    words=len(text.split())
#    num=1
#    return words, num, text
'''
#### Clear data upon new input




def create_dict_from_session():
    mdict=[]
    if (len(st.session_state['pastinp']))==0:
        mdict=[]
        return mdict
    elif (len(st.session_state['pastinp']))==1:
        mdict=  [
                    {"role":"user","content":st.session_state['pastinp'][0]},
                    {"role":"assistant","content":st.session_state['pastresp'][1]}
                ]
        return mdict
    elif (len(st.session_state['pastinp']))==2:
        mdict=  [
                    {"role":"user","content":st.session_state['pastinp'][0]},
                    {"role":"assistant","content":st.session_state['pastresp'][1]},
                    {"role":"user","content":st.session_state['pastinp'][1]},
                    {"role":"assistant","content":st.session_state['pastresp'][2]}
                ]
        return mdict
    else:
        for i in range(len(st.session_state['pastinp'])-3,len(st.session_state['pastinp'])):
            mdict.append({"role":"user","content":st.session_state['pastinp'][i]})
            mdict.append({"role":"assistant","content":st.session_state['pastresp'][i+1]})
        return mdict

'''
Functions for API Key Input
'''

def check_key():

    if openai.api_key:
        st.sidebar.info("OpenAI API key detected")
        return True
    elif os.path.exists(".env") and os.environ.get("OPENAI_API_KEY") is not None:
        openai.api_key=os.environ["OPENAI_API_KEY"]
        st.sidebar.success("OpenAI API key loaded from .env", icon="🚀")
        return True
    else:
        input_key()
        if openai.api_key:
            return True
        else:
            return False
    
def validate_key():
    try:
        r=openai.Completion.create(model=models, prompt="t.",max_tokens=5)
        st.sidebar.success("API key validated")
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

        temp=check_key()

        #st.sidebar.caption("Don't have a key?") 
    #st.sidebar.write("Don't have a key?")
    #st.sidebar.markdown('[Get OpenAI API Key here](https://platform.openai.com/account/api-keys)',unsafe_allow_html=True)



'''
Functions for LLM response
'''

#### OpenAI call

def moderation(text):
        response = openai.Moderation.create(input=text)
        if response["results"][0]["flagged"]:
            return 'Moderated : The generated text is of violent, sexual or hateful in nature. Try generating another piece of text or change your story topic. Contact us for more information'
        else:
            return text

def open_ai_call(models="", prompt="", temperature=0.7, max_tokens=256,top_p=0.5,frequency_penalty=1,presence_penalty=1,user_id="test-user"):
        response=openai.Completion.create(model=models, prompt=prompt,temperature=temperature,max_tokens=max_tokens,top_p=top_p,frequency_penalty=frequency_penalty,presence_penalty=presence_penalty,user=user_id)
        text=moderation(response['choices'][0]['text'])
        tokens=response['usage']['total_tokens']
        words=len(text.split())
        reason=response['choices'][0]['finish_reason']
        return text, tokens, words, reason

def q_response(query,doc,models):
    prompt=f"Answer the question below only from the context provided. Answer in detail and in a friendly, enthusiastic tone. If not in the context, respond with '100'\n context:{doc}.\nquestion:{query}.\nanswer:"
    text, t1, t2, t3=open_ai_call(models,prompt)
    try:
        if int(text)==100:
            text2,tx,ty,tz=open_ai_call(models, query)
            text_final="I am sorry, I couldn't find the information in the documents provided.\nHere's the information I have from the data I was pre-trained on-\n"+text2
    except: 
        text_final=text
    return text_final

def chat_gpt_call(message_dict=[{"role":"user","content":"Hello!"}], model="gpt-3.5-turbo", max_tokens=120,temperature=0.5):
    response=openai.ChatCompletion.create(model=model, messages=message_dict,max_tokens=max_tokens,temperature=temperature)
    response_dict=response.choices[0].message
    response_text=response_dict.content
    words=len(response_text.split())
    total_tokens=response.usage.total_tokens
    response_tokens=response.usage.completion_tokens
    return response_text, response_dict, words, total_tokens, response_tokens

def create_dict_from_session():
    mdict=[]
    if (len(st.session_state['pastinp']))==0:
        mdict=[]
        return mdict
    elif (len(st.session_state['pastinp']))==1:
        mdict=  [
                    {"role":"user","content":st.session_state['pastinp'][0]},
                    {"role":"assistant","content":st.session_state['pastresp'][1]}
                ]
        return mdict
    elif (len(st.session_state['pastinp']))==2:
        mdict=  [
                    {"role":"user","content":st.session_state['pastinp'][0]},
                    {"role":"assistant","content":st.session_state['pastresp'][1]},
                    {"role":"user","content":st.session_state['pastinp'][1]},
                    {"role":"assistant","content":st.session_state['pastresp'][2]}
                ]
        return mdict
    else:
        for i in range(len(st.session_state['pastinp'])-3,len(st.session_state['pastinp'])):
            mdict.append({"role":"user","content":st.session_state['pastinp'][i]})
            mdict.append({"role":"assistant","content":st.session_state['pastresp'][i+1]})
        return mdict

def q_response_chat(query,doc,mdict):
    prompt=f"Answer the question below only and only from the context provided. Answer in detail and in a friendly, enthusiastic tone. If not in the context, respond in no other words except '100', only and only with the number '100'. Do not add any words to '100'.\n context:{doc}.\nquestion:{query}.\nanswer:"
    mdict.append({"role":"user","content":prompt})
    response_text, response_dict, words, total_tokens, response_tokens=chat_gpt_call(message_dict=mdict)
    try:
        if int(response_text)==100:
            text2,tx,ty,tz=open_ai_call(models, query)
            text_final="I am sorry, I couldn't find the information in the documents provided.\nHere's the information I have from the data I was pre-trained on-\n"+text2
    except: 
        text_final=response_text
    return text_final


'''
Document Details Functions
'''

#### Summarize, TP, Sample Qs

def summary(info,models):

    prompt="In a 100 words, explain the purpose of the text below:\n"+info+".\n Do not add any pretext or context."
    with st.spinner('Summarizing your uploaded document'):
        text, t1, t2, t3=open_ai_call(models,prompt)
    return text

def talking(info,models):

    prompt="In short bullet points, extract all the main talking points of the text below:\n"+info+".\nDo not add any pretext or context. Write each bullet in a new line."
    with st.spinner('Extracting the key points'):
        text, t1, t2, t3=open_ai_call(models,prompt)

    return text

def questions(info,models):

    prompt="Extract ten questions that can be asked of the text below:\n"+info+".\nDo not add any pretext or context."
    with st.spinner('Generating a few sample questions'):
        text, t1, t2, t3=open_ai_call(models,prompt)

    return text


'''
Layout, Information and Selection Functions
'''

def input_selector():

        input_choice=st.sidebar.radio("#### :blue[Choose the Input Method]",('Document','Weblink','YouTube','Audio (Coming Soon)'))

        if input_choice=="Document":
            with st.sidebar.expander("📁 __Documents__"):
                uploaded=st.file_uploader(label="Select File",type=['pdf','txt'],on_change=clear)
        elif input_choice=="Weblink":
            with st.sidebar.expander("🌐 __Webpage__"):
                uploaded=st.text_input('Enter a weblink',on_change=clear)
        elif input_choice=="YouTube":
            with st.sidebar.expander("🎥 __YouTube__"):
                uploaded=st.text_input('Enter a YT link',on_change=clear)
        elif input_choice=="Audio (Coming Soon)":
            with st.sidebar.expander("🎙 __Audio__ (Coming Soon)"):
                uploaded=st.text_input('Enter an Audio link',on_change=clear,disabled=True)
        
        return input_choice, uploaded

def first_column():
            st.markdown("<p style='text-align:center; color:blue;'><u><b>About Me</b></u></p>",unsafe_allow_html=True)
            st.markdown("<p style='color:#5A5A5A;'>🖖 I am a QnA agent that answers questions by reading assets (like documents, spreadsheets, videos, audios) provided by you.</p>",unsafe_allow_html=True)
            st.write(" ")
            st.write(" ")
            st.write(" ")            
            st.markdown("<span style='color:#5A5A5A;'>🖖 I am built on [Streamlit](https://streamlit.io/) using large language models built by good fellows at [OpenAI](https://openai.com). A huge shout-out to [Stremlit Chat](https://github.com/AI-Yash/st-chat) and [pdfplumber](https://github.com/jsvine/pdfplumber).</span>", unsafe_allow_html=True)
            st.write(" ")
            st.write(" ")
            st.markdown("<p style='color:#5A5A5A;'>🖖 Presently, Documents(.pdf and .txt) and web ulrs(single page) are enabled. Websites, Videos and Audios are next in pipeline.</p>", unsafe_allow_html=True)
            st.write(" ")        
            st.write(" ")        
            st.markdown("<span style='color:#5A5A5A;'>🖖 I am under regular development. You can also view my source code and contribute [here](https://github.com/abhinav-kimothi/VIDIA.I/tree/main).</span>", unsafe_allow_html=True)

def second_column():
            st.markdown("<p style='text-align:center; color:blue;'><u><b>How to Use</u><a href='https://youtu.be/UuTmUxBzE_w'>[Watch Demo🎥]</a></b></p>",unsafe_allow_html=True)
            st.markdown("<span style='color:#5A5A5A;'>👉🏽 Firstly, you need to enter your OpenAI api key🔧 in the input box on the sidebar. You can get it [here](https://platform.openai.com/account/api-keyshttps://platform.openai.com/account/api-keys)</span>",unsafe_allow_html=True)
            with st.expander("Why do I need an API key?"):
                st.markdown("<span style='color:#5A5A5A;'>🌟 VIDIA uses OpenAI's GPT APIs. A [cost is incurred for every API call](https://openai.com/pricing)💰. OpenAI offers free credits when you sign up. So you can try out VIDIA without incurring any cost. If you'd like to fund this app to take away this requirement 😬 Please drop a note [here](mailto:abhinav.kimothi.ds@gmail.com)</span>",unsafe_allow_html=True)

            st.markdown("<span style='color:#5A5A5A;'>👉🏽 You can then choose the asset you want to chat on. From the radio buttons on the sidebar. Presently you can select 📜 documents or 🔗 links to webpages basis your choice.",unsafe_allow_html=True)
            st.write(" ")
            st.markdown("<span style='color:#5A5A5A;'>👉🏽 VIDIA is ready ✌. You can ask your question. Also, explore summary tab to generate document summary, extract talking points and look at sample questions.",unsafe_allow_html=True)
            st.markdown("<span style='color:#5A5A5A;'>👉🏽 Also note, the app wouldn't work without an active internet connection🌐",unsafe_allow_html=True)

def third_column():
            st.markdown("<p style='text-align:center;color:blue;'><u><b>Roadmap & Suggestions</b></u></p>",unsafe_allow_html=True)
            st.markdown("<p style='color:#5A5A5A;'>🎯 Video transcripts🎥, Audio transcripts♬, Spreadsheets and Codes as inputs. Ability to handle multiple inputs, complete websites, content repositories etc.</p>",unsafe_allow_html=True)
            st.write(" ")
            st.markdown("<p style='color:#5A5A5A;'>🎯 Analysis of spreadsheets with charts📊 and insights✍. Analysis of other forms of dataframes/datasets.",unsafe_allow_html=True)
            st.write(" ")
            st.write(" ")
            st.write(" ")
            st.markdown("<p style='color:#5A5A5A;'>🎯 Address larger documents using embeddings.",unsafe_allow_html=True)
            st.markdown("<p style='color:#5A5A5A;'>🎯 Use models and embeddings that are free of cost.",unsafe_allow_html=True)
            st.write(" ")
            st.write(" ")
            st.markdown("<span style='color:#5A5A5A;'>🎯 Please leave your suggestions, issues, features requests, etc. by filling out [this form](https://forms.gle/uxfHYVhUNtGus8J97). <b>You may be surprised with a ☕🍔🍺reward💸!! 😀😀😀</b><span>",unsafe_allow_html=True)

def heads():
    st.markdown("<h3 style='text-align:center;'>👋🏽 Welcome! I am <span style='color:#4B91F1'>VIDIA.I</span>!👩🏽‍💻</h3>",unsafe_allow_html=True)
    st.markdown("""
    <p style='text-align:center;'>I answer questions after reading documents, webpages<span style='color:#D3D3D3; text-align:center;'>, spreadsheets^, youtube videos^ and audio files^ (^coming soon)</span></p>
    """,unsafe_allow_html=True)
    st.markdown("<h6 style='text-align:center;'> 💕 You can ask me anything 💕</h6>",unsafe_allow_html=True)

def contact():
    st.markdown("Github : [abhinav-kimothi](https://github.com/abhinav-kimothi)")
    st.markdown("LinkedIn :[abhinav-kimothi](https://www.linkedin.com/in/abhinav-kimothi/)")
    st.markdown("Twitter : [@abhinav-kimothi](https://twitter.com/abhinav_kimothi)")
    st.markdown("Email : [abhinav.kimothi.ds@gmail.com](mailto:abhinav.kimothi.ds@gmail.com)")


'''
Other Utilities
'''

#### This function clears session history data

def clear(greeting=greeting):
    st.cache_data.clear()
    if 'history' in st.session_state:
        del st.session_state['history']
    if 'pastinp' in st.session_state:
        del st.session_state['pastinp']
    if 'pastresp' in st.session_state:
        del st.session_state['pastresp']
    initialize_chat(greeting)

### This function for writing chat history into a string variable called hst
def write_history_to_a_file():
    hst=""
    st.session_state['history']=[]
    st.session_state['history'].append("VIDIA says -")
    st.session_state['history'].append(st.session_state['pastresp'][0])
    for i in range(1,len(st.session_state['pastresp'])):
        st.session_state['history'].append("Your Query - ")
        st.session_state['history'].append(st.session_state['pastinp'][i-1])
        st.session_state['history'].append("VIDIA's response - ")
        st.session_state['history'].append(st.session_state['pastresp'][i])

    for item in st.session_state['history']:
        hst+="\n"+str(item)
    
    return hst




