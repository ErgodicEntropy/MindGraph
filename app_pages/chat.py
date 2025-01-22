import base64
import streamlit as st
import agents

def chat_page():
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
