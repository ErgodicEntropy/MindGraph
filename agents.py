from langchain.llms import Cohere, HuggingFacePipeline
from transformers import AutoTokenizer, AutoModelForCausalLM, AutoModelForSeq2SeqLM, pipeline, AutoProcessor, AutoModelForSpeechSeq2Seq
import torch
from langchain.chains import LLMChain, ConversationChain, RetrievalQA, ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory, ConversationSummaryMemory, ChatMessageHistory
from langchain.agents import initialize_agent, Tool, load_tools
from langchain.document_loaders import DirectoryLoader, PyPDFLoader, TextLoader, CSVLoader, JSONLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings, CohereEmbeddings
from langchain.vectorstores import FAISS, Chroma
import os
import prompts
import librosa

DB_FAISS_PATH = os.path.abspath(os.path.join('vectorstore', 'db_faiss'))

#WhisperAI: Speech Recognition Model
processor = AutoProcessor.from_pretrained("openai/whisper-small")
model = AutoModelForSpeechSeq2Seq.from_pretrained("openai/whisper-small")


tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-large")
model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-large")

tokenizer.pad_token = tokenizer.eos_token

hf_pipeline = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    device="cpu",  # Use GPU/cuda if available
    max_length=100,
    truncation = True, 
    temperature=0.7,
    do_sample = True
)

llm = HuggingFacePipeline(pipeline=hf_pipeline)

# cohere_api_token = os.environ.get("COHERE_API_KEY")
# llm = Cohere(cohere_api_key=cohere_api_token)

RTC = prompts.RetrievedTextComponents
RFC = prompts.RetrievedFileComponents
UFQA = prompts.UserFileQA
TP = prompts.TranslationPrompt
SP = prompts.SummarizationPrompt
C = prompts.Connector


message_history = ChatMessageHistory()

memory = ConversationBufferMemory(
    memory_key="chat_history",
    input_key = "message",
    output_key="answer",
    chat_memory=message_history,
    return_messages=True,
)

def Chat(message: str):
    Conv_Agent = ConversationChain(llm=llm,memory=memory)
    resp = Conv_Agent.run({"message": message})
    memory.chat_memory.add_ai_message(resp)
    memory.chat_memory.add_user_message(message)
    return resp

def Translate(user_text: str, language: str):
    agent = LLMChain(llm=llm, prompt = TP)
    resp = agent.run({"user_text": user_text, "language": language})
    memory.chat_memory.add_ai_message(resp)
    memory.chat_memory.add_message(user_text)
    return resp 

def Summarize(user_text: str):
    agent = LLMChain(llm=llm, prompt = SP)
    resp = agent.run({"user_text": user_text})
    memory.chat_memory.add_ai_message(resp)
    memory.chat_memory.add_message(user_text)
    return resp 

def Transform(user_text: str):
    agent = LLMChain(llm=llm, prompt = SP)
    resp = agent.run({"user_text": user_text})
    memory.chat_memory.add_ai_message(resp)
    memory.chat_memory.add_message(user_text)
    return resp 

def Suggest(user_text: str):
    agent = LLMChain(llm=llm, prompt = SP)
    resp = agent.run({"user_text": user_text})
    memory.chat_memory.add_ai_message(resp)
    memory.chat_memory.add_message(user_text)
    return resp 

def RetrieveTextComponents(user_input: str):
    agent = LLMChain(llm=llm, prompt = RTC)
    resp = agent.run({"user_input": user_input})
    memory.chat_memory.add_ai_message(resp)
    memory.chat_memory.add_message(user_input)
    return resp 


def RetrieveAudioComponents(audio_path):    
    # Load an audio file (replace with your audio file path)
    audio, sr = librosa.load(audio_path, sr=16000)

    # Process the audio
    input_features = processor(audio, sampling_rate=sr, return_tensors="pt").input_features

    # Generate text
    with torch.no_grad():
        predicted_ids = model.generate(input_features)
    transcription = processor.batch_decode(predicted_ids, skip_special_tokens=True)[0]
    return RetrieveTextComponents(transcription)


# Create vector database
def CreateVectorDB(DATA_PATH, filetype):
    os.makedirs(os.path.dirname(DB_FAISS_PATH), exist_ok=True)
    # Load documents from PDF files
    if filetype == "text/plain":
        loader = DirectoryLoader(DATA_PATH, glob='*.txt', loader_cls=TextLoader)
    if filetype == "application/pdf":
        loader = DirectoryLoader(DATA_PATH, glob='*.pdf', loader_cls=PyPDFLoader)
    if filetype == "text/csv":
        loader = DirectoryLoader(DATA_PATH, glob='*.csv', loader_cls=CSVLoader)        
    if filetype == "application/json":
        loader = DirectoryLoader(DATA_PATH, glob='*json', loader_cls=JSONLoader)
    
    documents = loader.load()
    
    # Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    texts = text_splitter.split_documents(documents)
        
    embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/multi-qa-mpnet-base-dot-v1',
                                       model_kwargs={'device': 'cpu'})

    db = FAISS.from_documents(texts, embeddings)
    db.save_local(DB_FAISS_PATH)
    
##Local Document RAG system

def RetrieveFileComponents():
    # Retrieve vector database
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/multi-qa-mpnet-base-dot-v1",
                                       model_kwargs={'device': 'cpu'})
    db = FAISS.load_local(DB_FAISS_PATH, embeddings)
    #Retrieval QA Chain
    qa = RetrievalQA.from_chain_type(llm=llm,
                                       chain_type='stuff',
                                       retriever=db.as_retriever(search_kwargs={'k': 2}),
                                       chain_type_kwargs={'prompt':RFC},
                                       return_source_documents=True,
                                       )
    query = """
    Analyze the user file and extract the key summarized information items. 
    For each item, assign a weight (degree of importance or relevance) between 0 and 1, 
    where 1 is the most important and 0 is the least important. 

    Return the output strictly in JSON format with no additional remarks or explanations. 
    The JSON should contain a list of objects, where each object has two keys: 
    - "item": the summarized information item (string)
    - "weight": the corresponding weight (float)
    """
    response = qa(query)
    result = response["result"]  # Access the result
    return result



def Connect(components: str):
    agent = LLMChain(llm=llm, prompt = C)
    resp = agent.run({"componentss": components})
    memory.chat_memory.add_ai_message(resp)
    memory.chat_memory.add_message(components)
    return resp 


#Conversation with File (QA)
def FileChat(message: str):
    # Retrieve vector database
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/multi-qa-mpnet-base-dot-v1",
                                       model_kwargs={'device': 'cpu'})
    db = FAISS.load_local(DB_FAISS_PATH, embeddings)
    convret = ConversationalRetrievalChain.from_llm(llm=llm,
                                                  chain_type = "stuff", 
                                                  retriever=db.as_retriever(search_kwargs={'k': 2}),
                                                  memory=memory,
                                                  combine_docs_chain_kwargs={'prompt': UFQA},
                                                  return_source_documents=True,verbose=False)
    
    response = convret({"message": message})
    result = response["result"]  # Access the result
    return result


