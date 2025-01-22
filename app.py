from streamlit_option_menu import option_menu
import streamlit_authenticator as stauth
import streamlit as st
import streamlit.components.v1 as components
from streamlit.components.v1 import html
from streamlit_webrtc import webrtc_streamer
import librosa
from pyvis.network import Network
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import base64
import agents
import os
import json
import sqlite3

def extract_json(data_str:str): # LLM Response
    try:
        n = data_str.index('[')
        m = data_str.index(']')
        return json.loads(data_str[n:m+1].strip())
    except (ValueError, json.JSONDecodeError) as e:
        print(f"Error extracting JSON: {e}")
        return {}

def extract_JSON(data_str:str): # LLM Response
    if data_str.startswith("```json"):
        data_str = data_str[7:]
    if data_str.endswith("```"):
        data_str = data_str[:-3]
    if data_str.startswith("```"):
        data_str = data_str[3:]

    data_str = data_str.strip()
    try:
        return json.loads(data_str)
    except (ValueError, json.JSONDecodeError) as e:
        print(f"Error extracting JSON: {e}")
        return {}
        

custom_css = f"""
        <style>
            .stApp {{
                background-color: {"#1E1E1E" if st.session_state.theme == "dark" else "#FFFFFF"};
                color: {"#FFFFFF" if st.session_state.theme == "dark" else "#000000"};
            }}
            .stButton>button {{
                color: {"#FFFFFF" if st.session_state.theme == "dark" else "#000000"};
                background-color: {"#2E2E2E" if st.session_state.theme == "dark" else "#F0F2F6"};
            }}
            .stTextInput>div>div>input, .stTextArea>div>div>textarea {{
                color: {"#FFFFFF" if st.session_state.theme == "dark" else "#000000"};
                background-color: {"#2E2E2E" if st.session_state.theme == "dark" else "#FFFFFF"};
            }}
        </style>
    """
Languages = ["English", "French", "Arabic", "Specify a language"]
Colors = [
    "Blue", "Red", "Green", "Yellow", "Orange", "Purple", "Pink", 
    "Brown", "Black", "White", "Gray", "Cyan", "Magenta", 
    "Lime", "Teal", "Navy", "Gold", "Silver", "Beige", "Maroon"
]

Structures =  [
    "Hierarchical",  # Represents layered structures like a tree or hierarchy.
    "Network",       # Represents interconnected nodes without strict order.
    "Sequential",     # Represents linear, step-by-step flows.
    "Circular",
   ]

# Directory to save uploaded files
UPLOAD_DIR = 'uploads'
os.makedirs(UPLOAD_DIR, exist_ok=True)

VOCAL_DIR = 'vocal'
os.makedirs(VOCAL_DIR, exist_ok=True)

#Session Storage Variables:


#page tracker (using session states)
if "theme" not in st.session_state:
    st.session_state.theme = "light"
if "user_action" not in st.session_state:
    st.session_state.user_action = None #Login or SignUp
if "messages" not in st.session_state: # Initialize chat history in session state
    st.session_state.messages = [] #list of dictionaries {"role": {role: user/human , ai/assistant}, "content":{content}}


# Session Storage Functions:
def get_image_as_base64(path):
    """
    Encodes a local image file as a base64 data URL.
    
    Args:
        path (str): Path to the local image file.
    
    Returns:
        str: Base64-encoded data URL.
    """
    with open(path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    return f"data:image/png;base64,{encoded_string}"

def toggle_theme():
    if st.session_state.theme == "light":
        st.session_state.theme = "dark"
    else:
        st.session_state.theme = "light"

def user_action_reset():
    st.session_state.user_action = None


def SpecLang(Option, LangList): #mostly a one time recursion
    if Option == "Specify a language":    
        LangList.remove("Specify a language")
        user_lang = st.text_input("Add a language")
        LangList.append(user_lang)
        LangList.append("Specify a language")
        Option = st.selectbox("Choose the langauge",LangList) #Language settings of the output
        return SpecLang(Option, LangList)
    else:
        FinalOption = Option
        return FinalOption
    


#Multi-Page Simulation in SPA using Mutli-Level Function Calling: Route Url - Action/Request Handler pairs (1-n)

### MAIN RUN

def login_page(): #User Registration, Profile Creation and Login
    #User Settings    
    if st.session_state.user_action == None:
        st.write("# Welcome to MindGraph 🧠")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Sign Up"):    
                st.session_state.user_action = "Sign Up"
        with col2:
            if st.button("Login"):    
                st.session_state.user_action = "Login"

    conn = sqlite3.connect("users.db")

    c = conn.cursor()

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT
        )
        """
    )

    conn.commit()

    if st.session_state.user_action == "Sign Up":
        ##User Authentification and Profile Creation
        st.write("## Create Account")
        new_username = st.text_input("Enter a username")
        new_password = st.text_input("Enter a password", type="password")    
        if st.button("Create Profile"):
            if new_username and new_password:
                try:
                    hashed_password = stauth.Hasher([new_password]).generate()[0]
                    c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (new_username, hashed_password))
                    conn.commit()
                    st.success("Profile Created Successfully!")
                except sqlite3.IntegrityError:
                    st.error(f"Username {new_username} already exists. Please choose another!")
            else:
                st.warning("Please fill in the requried forms")
        if st.button("Back"):
            user_action_reset()
            st.experimental_rerun() 

    if st.session_state.user_action == "Login":
        c.execute("SELECT username, password FROM users")
        results = c.fetchall()

        users = {}
        for username, password in results:
            users[username] = {'username':username, 'password':password}

        authenticator = stauth.Authenticate(
            users,
            "app_cookie_name",  # Cookie name for session management
            "signature_key",    # Secret key for cookie signing
            cookie_expiry_days=30    
        )
        
        name, authentication_status, username = authenticator.login("Login", "main")
        
        if authentication_status:
            st.write("Welcome to your dashboard!")
            st.write("You are now logged in.")
            ####THE WHOLE REST OF APP LOGIC HERE

            # Title and welcome message
            st.title("MindGraph 🧠")
            st.write("Welcome to MindGraph! Make your experience visualized!")

            #Mode Settings
            st.sidebar.button("Toggle Dark/Light Mode", on_click=toggle_theme)    
            st.markdown(custom_css, unsafe_allow_html=True)


            if st.button("Input Information"):
                st.experimental_rerun()
                home_page()

        elif authentication_status is False:
            st.error("Invalid Username/Password")
        elif authentication_status is None:
            st.warning("Please fill in the form")
        
        if st.button("Back"):
            user_action_reset()  # Reset user_action to None
            st.experimental_rerun()  # Refresh the app to show the main menu

        if authentication_status:         
            if st.button("Logout"):
                authenticator.logout("Logout","main")
                st.session_state.clear()
                st.experimental_rerun()
        
        conn.close()


                
def home_page(): #action for the home route: #User Input Format and Content and Output Format
    st.title("Home Page")
    st.write("Welcome to the Home Page!")
    # Header and subheader (add text inside the parentheses)
    st.sidebar.header("Settings")
    st.sidebar.markdown("### Insert your information")
    LangOption = st.sidebar.selectbox("Choose the language",Languages, index=Languages.index("English"))
    Language = SpecLang(LangOption,Languages)
    ValueFilter = st.sidebar.slider("Select Filtration Level:", min_value=0, max_value=100, value=80, step=1, format="%d%%") #how extreme the pareto filtration is e.g. 20%-80% (by default) , 15%-85%...etc 

    InputFormat = st.selectbox("Choose the input format", ["File", "Paragraph", "Audio"])

    if InputFormat == "Paragraph":
        # Text input
        user_input = st.text_area("Type your information here:")
        if user_input is not None:
            UserComponents = extract_json(agents.RetrieveTextComponents(user_input))
            ##Pareto Filtering
            FilteredComponents = []
            for component in UserComponents:
                if 100*component["weight"] >= ValueFilter:
                    FilteredComponents.append(component)            
            
    if InputFormat == "Audio":
        # Add the vocal recorder to the app
        webrtc_ctx = webrtc_streamer(
            key="audio-recorder",
            audio_frame_callback=lambda frame: frame,
            media_stream_constraints={"audio": True, "video": False},
        )

        audio_frames = []
        if webrtc_ctx.audio_receiver:
            st.write("Recording...")
            for frame in webrtc_ctx.audio_receiver.get_frames(timeout=10):  # Record for 10 seconds
                audio_frames.append(frame.to_ndarray())
            
            if audio_frames:
                audio = np.concatenate(audio_frames)
                librosa.output.write_wav(os.path.join(VOCAL_DIR,'recorded_audio.wav'), audio, sr=16000)
                st.write("Recording saved.")

        if audio_frames:            
            UserComponents = extract_json(agents.RetrieveAudioComponents(os.path.join(VOCAL_DIR,'recorded_audio.wav')))
            ##Pareto Filtering
            FilteredComponents = []
            for component in UserComponents:
                if 100*component["weight"] >= ValueFilter:
                    FilteredComponents.append(component)            

        
    if InputFormat == "File":
        # File uploader
        user_input = st.file_uploader("Upload your information as a file!", type=["pdf","txt","csv","json"])
        if user_input is not None:
            filepath = os.path.join(UPLOAD_DIR, user_input.name)
            with open(filepath, "w", encoding="utf-8") as uploaded_file:
                uploaded_file.write(user_input.getvalue()) #converting the file into raw bytes for python file handling
            st.success(f"File saved to: {filepath}")
            agents.CreateVectorDB(filepath, user_input.type) #vector db creation
            
            UserComponents = extract_json(agents.RetrieveFileComponents(user_input))
            ##Pareto Filtering
            FilteredComponents = []
            for component in UserComponents:
                if 100*component["weight"] >= ValueFilter:
                    FilteredComponents.append(component)

    UserMetadata = extract_json(agents.Connect(FilteredComponents)) #dictionary of components, weights and their connections (dictonaries)
    
    #### FILTER COMPONENTS: GLOBAL LIST OR SESSION STATE SOLUTION
    #Graph Metadata:    
    ## Customization options
    st.sidebar.markdown("### Graph Customization")
    Structure = st.sidebar.selectbox("Choose a graph layout",Structures, index=Structures.index("Network"))

    ## Advanced settings
    with st.sidebar.expander("Advanced Settings"):
        show_labels = st.checkbox("Show labels", value=True)
        enable_animations = st.checkbox("Enable animations", value=True)
        Size = st.sidebar.slider("Select Size:", min_value=0, max_value=100, value=50, step=1, format="%d%%")
        Weight = st.sidebar.slider("Select Weight:", min_value=0, max_value=100, value=50, step=1, format="%d%%")
        EdgeColor = st.sidebar.selectbox("Choose edge color",Colors,index=0)
        NodeColor = st.sidebar.selectbox("Choose node color",Colors, index=1)

    ## Save settings button
    if st.sidebar.button("Save Settings"):
        st.sidebar.success("Settings saved successfully!")

    
    #Graph Creation:   #Network, Hierarchical, Sequential, Circular    
    
    if Structure == "Hierarchical":
        G = nx.tree_graph(name="Tree Map", description="Hierarchical representation of user info")
        options = {
            "physics": {
                "enabled": True,
                "solver": "hierarchical",
                "hierarchical": {
                    "enabled": True,
                    "direction": "UD"  # Up-Down
                }
            }
        }
    elif Structure == "Network":
        G = nx.Graph(name="Mind Network", description="Decentralized representation of user info")
        options = {
            "physics": {
            "enabled": True,
            "barnesHut": {
                "gravitationalConstant": -8000,
                "centralGravity": 0.3,
                "springLength": 95,
                "springConstant": 0.04,
                "damping": 0.09,
                "avoidOverlap": 0.1
            }
            },
            "layout": {
                "hierarchical": {
                    "enabled": False
                }
            },
            "stabilization": {
                "enabled": True,
                "iterations": 100
            },
            "interaction": {
                "hover": True,
                "zoomView": True
            }
        }
    elif Structure == "Sequential":
        G = nx.path_graph(name="MindSequence", description="Sequential representation of user info")
        options = {
            "physics": {
                "enabled": True,
                "solver": "hierarchical",
                "hierarchical": {
                    "enabled": True,
                    "direction": "LR"  # Left-Right
                }
            }
        }
    elif Structure == "Circular":
        G = nx.cycle_graph(name="MindCycle", description="Cyclical representation of user info")
        options = {
            "physics": {
                "enabled": True,
                "solver": "circular"
            }
        }


    options = {
        "physics": {
            "enabled": True,
            "barnesHut": {
                "gravitationalConstant": -8000,
                "centralGravity": 0.3,
                "springLength": 95,
                "springConstant": 0.04,
                "damping": 0.09,
                "avoidOverlap": 0.1
            }
        },
        "layout": {
            "hierarchical": {
                "enabled": False
            }
        },
        "stabilization": {
            "enabled": True,
            "iterations": 100
        },
        "interaction": {
            "hover": True,
            "zoomView": True
        }
    }
    

    net = Network(notebook=True, height="500px", width="100%")
    net.from_nx(G)

    net.set_options(options)
    net.save_graph("graph.html")



    if st.button("Display Results"):
        st.experimental_rerun()
        display_page()




def display_page():
    graph_html = open("graph.html", "r", encoding="utf-8").read()        
    components.html(graph_html, height=600)
    if st.button("Go Chat"):
        st.session_state.page = "chat"

#CRUD THE GRAPH: Insert, Search, Update, Delete
def crud_graph(): 
    pass

def suggest_components(): #suggest nodes and edges
    pass

def version_control(): #session storage: a list of graphs
    pass

def summarize_text():
    pass

def summarize_graph():
    pass

def expand_edge(): #explanation, summarization and QA chat
    pass

def expand_node(): #explanation, summarization and QA chat
    pass 

def memory_techniques():
    pass

def anki_logic():
    pass

def Export_Save():
    pass

def Share(): #Real-Time Collaboration, Documentation and Comments (Users in same session -> Network Effects)
    pass


def chat_page():
    ## CHATBOT: GraphQA + FileQA
    if st.button("Let's Chat!"):
        logo_path = "./images/MindMap.png"  
        logo = get_image_as_base64(logo_path)
        with st.spinner("Loading..."):
            for message in st.session_state.messages:
                with st.chat_message(message["role"], avatar=logo):
                    st.write(message["content"])
        st.success("You're good to go ✅")
        while not st.button("Done"):
            with st.chat_message("assistant", avatar=logo):
                st.write("Hello! I'm your assistant. How can I help you today?")
            # Chat input
            user_input = st.chat_input(placeholder="Any questions ?")

            # Display user input in a chat message
            if user_input:
                st.session_state.messages.append({"role":"user", "content":user_input})
                
                with st.chat_message("user"):
                    st.write(user_input)
                # Display assistant response in a chat message
                system_resp = agents.Chat(user_input)
                st.session_state.messages.append({"role":"assistant", "content": system_resp})
                
                with st.chat_message("assistant", avatar=logo):
                    st.write(system_resp)


    if st.button(""):
        st.session_state.page = "review"
        
def return_home():
    pass
    if st.button("Go Home"):
        st.session_state.page = "home"
        
        
