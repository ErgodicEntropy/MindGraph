import streamlit as st
import os
import sys 
from streamlit_webrtc import webrtc_streamer
import librosa
import numpy as np
import matplotlib.pyplot as plt
import json
import streamlit.components.v1 as components
import networkx as nx
from pyvis.network import Network

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import agents  # Now you can import agents.py

def home_page(): #action for the home route: #User Input Format and Content and Output Format    
    if "FilteredComponents" not in st.session_state:
        st.session_state.FilteredComponents = []

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



 
    st.title("Home Page")
    st.write("Welcome to the Home Page!")
    # Header and subheader (add text inside the parentheses)
    st.markdown("### Insert your information")
    InputFormat = st.selectbox("Choose the input format", ["Paragraph", "File", "Audio"])
    st.rerun()
    
    with st.sidebar.expander("Settings"):        
        Languages = ["English", "French", "Arabic", "Specify a language"]
        LangOption = st.selectbox("Choose the language",Languages, index=Languages.index("English"))
        Language = SpecLang(LangOption,Languages)
        ValueFilter = st.slider("Select Filtration Level:", min_value=0, max_value=100, value=80, step=1, format="%d%%") #how extreme the pareto filtration is e.g. 20%-80% (by default) , 15%-85%...etc 

    if InputFormat == "Paragraph":
        # Text input
        user_input = st.text_area("Type your information here:")
        if user_input:
            UserComponents = extract_json(agents.RetrieveTextComponents(user_input))
            ##Pareto Filtering
            for component in UserComponents:
                if 100*component["weight"] >= ValueFilter:
                    st.session_state.FilteredComponents.append(component)            
            
    # if InputFormat == "Audio":
        # VOCAL_DIR = 'vocal'
        # os.makedirs(VOCAL_DIR, exist_ok=True)   
    #     # Add the vocal recorder to the app
    #     webrtc_ctx = webrtc_streamer(
    #         key="audio-recorder",
    #         audio_frame_callback=lambda frame: frame,
    #         media_stream_constraints={"audio": True, "video": False},
    #     )

    #     audio_frames = []
    #     if webrtc_ctx.audio_receiver:
    #         st.write("Recording...")
    #         for frame in webrtc_ctx.audio_receiver.get_frames(timeout=10):  # Record for 10 seconds
    #             audio_frames.append(frame.to_ndarray())
            
    #         if audio_frames:
    #             audio = np.concatenate(audio_frames)
    #             librosa.output.write_wav(os.path.join(VOCAL_DIR,'recorded_audio.wav'), audio, sr=16000)
    #             st.write("Recording saved.")

    #     if audio_frames:            
    #         UserComponents = extract_json(agents.RetrieveAudioComponents(os.path.join(VOCAL_DIR,'recorded_audio.wav')))
    #         ##Pareto Filtering
    #         FilteredComponents = []
    #         for component in UserComponents:
    #             if 100*component["weight"] >= ValueFilter:
    #                 FilteredComponents.append(component)            

        
    if InputFormat == "File":
        # Directory to save uploaded files
        UPLOAD_DIR = 'uploads'
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        # File uploader
        user_input = st.file_uploader("Upload your information as a file!", type=["pdf","txt","csv","json"])
        if user_input is not None:
            filepath = os.path.join(UPLOAD_DIR, user_input.name)
            with open(filepath, "wb") as uploaded_file:
                uploaded_file.write(user_input.getvalue()) #converting the file into raw bytes for python file handling
            st.success(f"File saved to: {filepath}")
            agents.CreateVectorDB(filepath, user_input.type) #vector db creation
            
            UserComponents = extract_json(agents.RetrieveFileComponents())
            ##Pareto Filtering
            for component in UserComponents:
                if 100*component["weight"] >= ValueFilter:
                    st.session_state.FilteredComponents.append(component)            

    UserMetadata = extract_json(agents.Connect(st.session_state.FilteredComponents)) #dictionary of components, weights and their connections (dictonaries)
    
    #Graph Metadata:    
    ## Customization options
    if UserMetadata:
        Structures =  [
            "Hierarchical",  # Represents layered structures like a tree or hierarchy.
            "Network",       # Represents interconnected nodes without strict order.
            "Sequential",     # Represents linear, step-by-step flows.
            "Circular",
        ]
        st.sidebar.markdown("### Graph Customization")
        Structure = st.sidebar.selectbox("Choose a graph layout",Structures, index=Structures.index("Network"))

        ## Advanced settings
        with st.sidebar.expander("Advanced Settings"):
            NodeColors = [
                "lightblue", "lightgreen", "lightcoral", "lightpink", "lightsalmon",
                "blue", "green", "red", "yellow", "purple",
                "#FF5733", "#33FF57", "#3357FF", "#FF33A1", "#A133FF"
            ]

            EdgeColors = [
                "gray", "black", "blue", "green", "red",
                "#888888", "#444444", "#0000FF", "#00FF00", "#FF0000",
                "rgba(128, 128, 128, 0.5)", "rgba(255, 0, 0, 0.5)"
            ]
            enable_animations = st.checkbox("Enable animations", value=True)
            Size = st.slider("Node Font Size", min_value=10, max_value=30, value=12, step=1)
            Weight = st.slider("Edge Width", min_value=1, max_value=10, value=2, step=1)
            EdgeColor = st.selectbox("Choose edge color",EdgeColors,index=0)
            NodeColor = st.selectbox("Choose node color",NodeColors, index=1)

        
        #Graph Creation:   #Network, Hierarchical, Sequential, Circular    -> Barnes Hut is optimal for small graphs, ForceAtlas2Based is optimal for large graphs
        
        if Structure == "Hierarchical":
            # G = nx.tree_graph(name="Tree Map", description="Hierarchical representation of user info")
            options = {
                "nodes": {
                "color": {
                    "background": NodeColor,
                        },
                "font": {
                    "size": Size,
                    "color": "black",
                    "face": "Arial",
                    "strokeWidth": 1,
                    "strokeColor": "white"
                    },
                "shape": "circle",
                "size": 20,
                "borderWidth": 1,
                "shadow": True,
                "title": "Node Tooltip",
                "labelHighlightBold": True,
                "mass": 1
                },
                "edges": {
                "color": {
                    "color": EdgeColor,
                    "highlight": "red",
                    "hover": "orange",
                    "inherit": False
                    },
                "width": Weight,
                "arrows": {
                    "to": True,
                    "middle": False,
                    "from": False
                    },
                "dashes": False,
                "smooth": True,
                "title": "Edge Tooltip",
                "length": 100,
                "shadow": True,
                "selectionWidth": 2
                },
                "physics": {
                    "enabled": enable_animations,
                    "solver": "barnesHut",
                    "barnesHut": {
                        "gravitationalConstant": -8000,
                        "centralGravity": 0.3,
                        "springLength": 95,
                        "springConstant": 0.04,
                        "damping": 0.09,
                        "avoidOverlap": 0.1
                    },
                    "maxVelocity": 50,
                    "minVelocity": 0.1,
                    "stabilization": {
                        "enabled": True,
                        "iterations": 1000,
                        "updateInterval": 50,
                        "onlyDynamicEdges": False,
                        "fit": True
                    }                
                },
                "layout": {
                    "hierarchical": {
                        "enabled": True,
                        "levelSeparation": 100,
                        "nodeSpacing": 100
                    }
                },
                "interaction": {
                    "dragNodes": True,
                    "dragView": True,
                    "zoomView": True,
                    "hover": True,
                    "multiselect": True,
                    "navigationButtons": True,
                    "keyboard": True
                },
                "configure": {
                    "enabled": True,
                    "filter": "nodes,edges",
                    "showButton": True
                }
            }
        elif Structure == "Network":
            # G = nx.Graph(name="Mind Network", description="Decentralized representation of user info")
            options = {
                "nodes": {
                "color": {
                    "background": NodeColor,
                        },
                "font": {
                    "size": Size,
                    "color": "black",
                    "face": "Arial",
                    "strokeWidth": 1,
                    "strokeColor": "white"
                    },
                "shape": "circle",
                "size": 20,
                "borderWidth": 1,
                "shadow": True,
                "title": "Node Tooltip",
                "labelHighlightBold": True,
                "mass": 1
                },
                "edges": {
                "color": {
                    "color": EdgeColor,
                    "highlight": "red",
                    "hover": "orange",
                    "inherit": False
                    },
                "width": Weight,
                "arrows": {
                    "to": True,
                    "middle": False,
                    "from": False
                    },
                "dashes": False,
                "smooth": True,
                "title": "Edge Tooltip",
                "length": 100,
                "shadow": True,
                "selectionWidth": 2
                },
                "physics": {
                    "enabled": enable_animations,
                    "solver": "barnesHut",
                    "barnesHut": {
                        "gravitationalConstant": -8000,
                        "centralGravity": 0.3,
                        "springLength": 95,
                        "springConstant": 0.04,
                        "damping": 0.09,
                        "avoidOverlap": 0.1
                    },
                    "maxVelocity": 50,
                    "minVelocity": 0.1,
                    "stabilization": {
                        "enabled": True,
                        "iterations": 1000,
                        "updateInterval": 50,
                        "onlyDynamicEdges": False,
                        "fit": True
                    }                
                },
                "interaction": {
                    "dragNodes": True,
                    "dragView": True,
                    "zoomView": True,
                    "hover": True,
                    "multiselect": True,
                    "navigationButtons": True,
                    "keyboard": True
                },
                "configure": {
                    "enabled": True,
                    "filter": "nodes,edges",
                    "showButton": True
                }
            }
        elif Structure == "Sequential":
            # G = nx.path_graph(name="MindSequence", description="Sequential representation of user info")
            options = {
                "nodes": {
                "color": {
                    "background": NodeColor,
                        },
                "font": {
                    "size": Size,
                    "color": "black",
                    "face": "Arial",
                    "strokeWidth": 1,
                    "strokeColor": "white"
                    },
                "shape": "circle",
                "size": 20,
                "borderWidth": 1,
                "shadow": True,
                "title": "Node Tooltip",
                "labelHighlightBold": True,
                "mass": 1
                },
                "edges": {
                "color": {
                    "color": EdgeColor,
                    "highlight": "red",
                    "hover": "orange",
                    "inherit": False
                    },
                "width": Weight,
                "arrows": {
                    "to": True,
                    "middle": False,
                    "from": False
                    },
                "dashes": False,
                "smooth": True,
                "title": "Edge Tooltip",
                "length": 100,
                "shadow": True,
                "selectionWidth": 2
                },
                "physics": {
                    "enabled": enable_animations,
                    "solver": "barnesHut",
                    "barnesHut": {
                        "gravitationalConstant": -8000,
                        "centralGravity": 0.3,
                        "springLength": 95,
                        "springConstant": 0.04,
                        "damping": 0.09,
                        "avoidOverlap": 0.1
                    },
                    "maxVelocity": 50,
                    "minVelocity": 0.1,
                    "stabilization": {
                        "enabled": True,
                        "iterations": 1000,
                        "updateInterval": 50,
                        "onlyDynamicEdges": False,
                        "fit": True
                    }                
                },
                "interaction": {
                    "dragNodes": True,
                    "dragView": True,
                    "zoomView": True,
                    "hover": True,
                    "multiselect": True,
                    "navigationButtons": True,
                    "keyboard": True
                },
                "configure": {
                    "enabled": True,
                    "filter": "nodes,edges",
                    "showButton": True
                }
            }
        elif Structure == "Circular":
            # G = nx.cycle_graph(name="MindCycle", description="Cyclical representation of user info")
            options = {
                "nodes": {
                "color": {
                    "background": NodeColor,
                        },
                "font": {
                    "size": Size,
                    "color": "black",
                    "face": "Arial",
                    "strokeWidth": 1,
                    "strokeColor": "white"
                    },
                "shape": "circle",
                "size": 20,
                "borderWidth": 1,
                "shadow": True,
                "title": "Node Tooltip",
                "labelHighlightBold": True,
                "mass": 1
                },
                "edges": {
                "color": {
                    "color": EdgeColor,
                    "highlight": "red",
                    "hover": "orange",
                    "inherit": False
                    },
                "width": Weight,
                "arrows": {
                    "to": True,
                    "middle": False,
                    "from": False
                    },
                "dashes": False,
                "smooth": True,
                "title": "Edge Tooltip",
                "length": 100,
                "shadow": True,
                "selectionWidth": 2
                },
                "physics": {
                    "enabled": enable_animations,
                    "solver": "barnesHut",
                    "barnesHut": {
                        "gravitationalConstant": -8000,
                        "centralGravity": 0.3,
                        "springLength": 95,
                        "springConstant": 0.04,
                        "damping": 0.09,
                        "avoidOverlap": 0.1
                    },
                    "maxVelocity": 50,
                    "minVelocity": 0.1,
                    "stabilization": {
                        "enabled": True,
                        "iterations": 1000,
                        "updateInterval": 50,
                        "onlyDynamicEdges": False,
                        "fit": True
                    }                
                },
                "interaction": {
                    "dragNodes": True,
                    "dragView": True,
                    "zoomView": True,
                    "hover": True,
                    "multiselect": True,
                    "navigationButtons": True,
                    "keyboard": True
                },
                "configure": {
                    "enabled": True,
                    "filter": "nodes,edges",
                    "showButton": True
                }
            }

        
        net = Network(notebook=False, height="500px", width="100%")
        for data in UserMetadata:
            component = data["summary"]
            weight = data["weight"]
            net.add_node(component, label=component, size=weight*30)    
                    
        for data in UserMetadata:    
            source = data["summary"]
            connections = data["connections"]
            for target, label in connections.items():
                if target not in net.get_nodes():
                    print(f"Warning: Node '{target}' does not exist. Skipping edge creation.")
                    continue
                net.add_edge(source, target, title=label)
            
        jsonified_options = json.dumps(options)
        net.set_options(jsonified_options)

        if UserMetadata:            
            net.save_graph("graph.html")
            graph_html = open("graph.html", "r", encoding="utf-8").read()        
            components.html(graph_html, height=600)
            if st.button("Let's Chat"):
                st.session_state.page == "chat"
        
    