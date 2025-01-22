from langchain.prompts import PromptTemplate

# Define the prompt template with few-shot examples
RetrievedTextComponents = PromptTemplate(
    input_variables=["user_input"],
    template="""
    Analyze the following user input and extract the key summarized information components. 
    For each component, assign a weight (degree of importance or relevance) between 0 and 1, 
    where 1 is the most important and 0 is the least important. 

    Summarize each component into **one or two words maximum**. 

    Return the output strictly in JSON format with no additional remarks or explanations. 
    The JSON should contain a list of objects, where each object has two keys: 
    - "component": the summarized information component (string, one or two words maximum)
    - "weight": the corresponding weight (float)

    Examples:

    User Input: "I need to book a flight to New York for a business meeting next week. Also, I want to stay in a hotel near the airport."
    Output:
    [
        {{
            "component": "Flight Booking",
            "weight": 0.9
        }},
        {{
            "component": "Business Meeting",
            "weight": 0.8
        }},
        {{
            "component": "Airport Hotel",
            "weight": 0.7
        }}
    ]

    User Input: "I want to buy a new laptop with at least 16GB RAM and a dedicated GPU for gaming. My budget is around $1500."
    Output:
    [
        {{
            "component": "Laptop Purchase",
            "weight": 0.9
        }},
        {{
            "component": "16GB RAM",
            "weight": 0.8
        }},
        {{
            "component": "Dedicated GPU",
            "weight": 0.8
        }},
        {{
            "component": "$1500 Budget",
            "weight": 0.7
        }}
    ]

    User Input: "Plan a trip to Paris for 5 days. I want to visit the Eiffel Tower, Louvre Museum, and try French cuisine."
    Output:
    [
        {{
            "component": "Paris Trip",
            "weight": 0.9
        }},
        {{
            "component": "Eiffel Tower",
            "weight": 0.8
        }},
        {{
            "component": "Louvre Museum",
            "weight": 0.8
        }},
        {{
            "component": "French Cuisine",
            "weight": 0.7
        }}
    ]


    Analyze the input and provide the output strictly in JSON format. Do not include any additional remarks, explanations, or text outside the JSON structure. Output only the JSON.
    
    User Input: {user_input}
    Output:
    """
)

RetrievedFileComponents = PromptTemplate(
    input_variables=["context"],
    template="""
    Analyze the following document context and extract the key summarized information components. 
    For each component, assign a weight (degree of importance or relevance) between 0 and 1, 
    where 1 is the most important and 0 is the least important. 

    Summarize each component into **one or two words maximum**. 

    Return the output strictly in JSON format with no additional remarks or explanations. 
    The JSON should contain a list of objects, where each object has two keys: 
    - "component": the summarized information component (string, one or two words maximum)
    - "weight": the corresponding weight (float)

    Examples:

    Context: "The project report outlines the need for a new marketing strategy. Key points include increasing social media presence, launching a new product line, and improving customer engagement."
    Output:
    [
        {{
            "component": "Social Media",
            "weight": 0.9
        }},
        {{
            "component": "Product Launch",
            "weight": 0.8
        }},
        {{
            "component": "Customer Engagement",
            "weight": 0.7
        }}
    ]

    Context: "The meeting minutes highlight the following action components: finalize the budget by Friday, assign team leads for the new project, and schedule a follow-up meeting next week."
    Output:
    [
        {{
            "component": "Budget Finalization",
            "weight": 0.9
        }},
        {{
            "component": "Team Leads",
            "weight": 0.8
        }},
        {{
            "component": "Follow-up Meeting",
            "weight": 0.7
        }}
    ]

    Context: "The research paper discusses the impact of climate change on agriculture. Key findings include reduced crop yields, increased pest activity, and the need for adaptive farming techniques."
    Output:
    [
        {{
            "component": "Crop Yields",
            "weight": 0.9
        }},
        {{
            "component": "Pest Activity",
            "weight": 0.8
        }},
        {{
            "component": "Adaptive Farming",
            "weight": 0.7
        }}
    ]

    Analyze the input and provide the output strictly in JSON format. Do not include any additional remarks, explanations, or text outside the JSON structure. Output only the JSON.
    
    Context: {context}
    Output:
    """
)

UserFileQA = PromptTemplate(
    input_variables=["message", "history", "context"],  
    template="""
    You are a helpful and knowledgeable assistant tasked with answering questions about the user's file. Use the conversation history to provide accurate and relevant responses.
    **File Information (Context)**:
    {context}

    **Conversation History**:
    {history}

    **User Question**:
    {message}

    Instructions:
    1. Carefully read the conversation history to understand the context.
    2. Answer the user's question based on the file information retrieved by the system. If the answer is not explicitly available, infer a reasonable response based on the context.
    3. If the question is unrelated to the file, politely inform the user that you can only answer questions about the information in their file.
    4. Keep your responses clear, concise, and professional.

    Examples:
    ---
    Example 1:
    Conversation History: []
    User Question: "What are the key points in my file?"
    Response: "Based on your file, the key points include increasing social media presence, launching a new product line, and improving customer engagement."

    Example 2:
    Conversation History: ["User: What are the main tasks mentioned in my file?", "AI: The main tasks include finalizing the budget and assigning team leads."]
    User Question: "Can you tell me more about the budget details?"
    Response: "Your file indicates that the budget needs to be finalized by Friday. It also mentions that the budget should prioritize marketing and product development."

    Example 3:
    Conversation History: []
    User Question: "What is the capital of France?"
    Response: "I can only answer questions related to the information in your file. Please ask me something about the content of your file."

    ---
    Now, answer the following question based on the conversation history:

    User Question:
    {message}

    Response:
    """
)

TranslationPrompt = PromptTemplate(
    input_variables=["input_text", "language"],
    template="""
    Translate the following text into {language}. Ensure the translation is accurate, natural, and contextually appropriate.

    **Text to Translate**:
    {input_text}

    **Translation**:
    """
)

SummarizationPrompt = PromptTemplate(
    input_variables=["input_text"],
    template="""
    Summarize the following text in a clear and concise manner. Focus on the key points and main ideas, and ensure the summary is accurate and contextually appropriate.

    **Text to Summarize**:
    {input_text}

    **Summary**:
    """
)


Connector = PromptTemplate(
    input_variables=["components"],
    template="""
You are an intelligent assistant that analyzes a list of components and identifies meaningful connections between them. Each component has a description and a weight indicating its importance. Your task is to:

1. **Summarize each input component into one or two words if it is not already summarized**. If the component is already summarized, leave it as is.
2. Analyze the components and, if meaningful, identify connections between them. **Summarize each connection in one or two words maximum**.
3. If no meaningful connection exists, leave the "connections" attribute empty.
4. **Preserve the weights in the output** as provided in the input.

### Input Format:
The input is a JSON list of components, where each component is a dictionary with the following structure:
{{
    "component": "Description of the component",
    "weight": "A numerical weight indicating importance"
}}

### Output Format:
The output should be a JSON list of components, where each component is a dictionary with the following structure:
{{
    "summary": "One or two words summarizing the component (summarize if necessary)",
    "weight": "The original weight from the input",
    "connections": {{
                        "the connections to other components" 
                   }}  // A dictionary of meaningful connections (if any), using summarized component names and summarized connection descriptions (one or two words maximum)
}}

### Few-Shot Example:

#### Input:
[
    {{
        "component": "Finalize the budget by Friday",
        "weight": 0.9
    }},
    {{
        "component": "Assign team leads for the new project",
        "weight": 0.8
    }},
    {{
        "component": "Schedule a follow-up meeting next week",
        "weight": 0.7
    }}
]

#### Output:
[
    {{
        "summary": "Budget Finalization",
        "weight": 0.9,
        "connections": {{
            "Team Leads": "Resource Allocation"
        }}
    }},
    {{
        "summary": "Team Leads",
        "weight": 0.8,
        "connections": {{
            "Budget Finalization": "Resource Dependency",
            "Follow-up Meeting": "Progress Discussion"
        }}
    }},
    {{
        "summary": "Follow-up Meeting",
        "weight": 0.7,
        "connections": {{
            "Team Leads": "Project Updates"
        }}
    }}
]

### Task:
Now, analyze the following components and provide the output in the specified format:

1. If any input component is not summarized into one or two words, summarize it.
2. Ensure all connection descriptions in the output are **one or two words maximum**.
3. **Preserve the weights** in the output as provided in the input.

Analyze the input and provide the output strictly in JSON format. Do not include any additional remarks, explanations, or text outside the JSON structure. Output only the JSON.

#### Input:
{components}

#### Output:
"""
)