''' chat.py consists of all chat related functions of vidia'''

import streamlit as st ###### Import Streamlit library
from streamlit_chat import message ###### Import message function from streamlit_chat library to render chat


### Initialisation function for the chat. Takes input for the first message.
### Also initialises the history and pastinp and pastresp variables
### history is used to store the chat history
### pastinp is used to store the past user inputs
### pastresp is used to store the past bot responses
### pastinp and pastresp are used to render the chat
### pastinp and pastresp are lists of strings
### history is a list of lists of strings because the chat history is stored as a list of lists of strings
def initialize_chat(bot_m=None):
        if 'history' not in st.session_state:
            st.session_state['history']=[]

        if 'pastinp' not in st.session_state:
            st.session_state['pastinp']=[]

        if 'pastresp' not in st.session_state:
            st.session_state['pastresp']=[bot_m]  

### Function for rendering chat
### Each list of strings is a conversation between the user and the bot
### The last element of the list is the latest conversation
### The first element of the list is the oldest conversation
### The function renders the chat in reverse order
### The latest conversation is rendered at the top
### The oldest conversation is rendered at the bottom
### The function uses the message function from the streamlit_chat library to render each message
def render_chat():
    for i in range(0,len(st.session_state['pastresp'])-1):
        if st.session_state['pastresp'][len(st.session_state['pastresp'])-1-i]:
            message(st.session_state['pastresp'][len(st.session_state['pastresp'])-1-i],key=i,avatar_style='avataaars')  
        if st.session_state['pastinp'][len(st.session_state['pastinp'])-1-i]:
            message(st.session_state['pastinp'][len(st.session_state['pastinp'])-1-i], is_user=True,key=i+100,avatar_style='initials', seed="U")
     

    if st.session_state['pastresp'][0]:
        message(st.session_state['pastresp'][0],key=-99, avatar_style='avataaars')

### Function for adding the latest query and VIDIA response
### to the session state variables pastinp and pastresp
def chatbot(query,response):

    st.session_state['pastinp'].append(query)
    st.session_state['pastresp'].append(response)
    render_chat()
