# agent.py

from llm import llm
from graph import graph
from utils import get_session_id
from tools.vector import get_medic_docs
from tools.table import generate_dynamic_table
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain.schema import BaseOutputParser
from langchain.tools import Tool
from langchain_community.chat_message_histories import Neo4jChatMessageHistory
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.runnables.history import RunnableWithMessageHistory



class LenientOutputParser(BaseOutputParser):
    def parse(self, text: str):
        # Simply return the raw text, without trying to enforce any specific format
        return text.strip()

# Create a movie chat chain
chat_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a medical expert in understanding medical regulations provided in the context. Read through the documents provided to give a clear and concise answer to the given query. If information is not in the provided documents simply inform the user that you do not know the answer to their query. You only answer according to what is provided in the documents."),
        ("human", "{input}"),
    ]
)

medic_chat = chat_prompt | llm | LenientOutputParser()

# Create a set of tools
tools = [
    # Tool.from_function(
    #     name="General Chat",
    #     description="For general medical inquiries not covered by other tools",
    #     func=medic_chat.invoke,
    # ), 
    Tool.from_function(
        name="Query Regulation Documents",
        description="For when a user needs information about Medical practices as strictly described in the documents and it uses vector search",
        func=get_medic_docs,
    ),
]

# Create chat history callback
def get_memory(session_id):
    return Neo4jChatMessageHistory(session_id=session_id, graph=graph)

# Create the agent
agent_prompt_text =  """
Role and Objective:
You are an agent specialized in giving detailed answers based on documents. You will analyze and provide guidance based on documents from five medical associations using the "Query Regulation Documents" tool and other available tools to complete the tasks effectively.
The table should be classified by document information.

One important information page number and document that the information came from are mandatory

When using the tool for retrieving information from the documents, do not change the user's query but you may ask more precise questions to help the retriever do a better job at retrieving the correct information.

How to Answer Properly:

- You must take the output from the database and answer the query that the user asks.
- Always include page Number and document file name within your answers and it should be link to the information that it provided it is mandatory
- Use only information from the database to answer the question.
- Focus on detailing the specific actions or procedures that organizations or companies are undertaking, and clearly describe the validations they are performing.
- Present the information in a way that specifies, for example, "This organization mandates that companies must do X, Y, and Z, and validate these actions by doing A, B, and C."
- Avoid general descriptions; instead, provide concrete examples of requirements and validations as outlined in the documents.- **Include data that is directly relevant to the question, and if no direct information is found, include information that is close to the answer even if not fully relevant.**
- Provide a very detailed answer, ensuring all relevant information is included.
- If the retrieved data does not directly answer the question, include related information that could be helpful to the user.
- If no relevant information is found, inform the user that no relevant information was found in the documents, but provide any closely related information that might assist.

Primary Task:

Your goal is to assist users by answering questions about medical regulations, ensuring responses are precise, detailed, and contextually accurate. You must use the available tools to gather, process, and present the required information.

You have access to the following tools:

{tools}

To use a tool, please use the following format:
Thought: Do I need to use a tool? 
Yes Action: the action to take, should be one of [{tool_names}] 
Action Input: the input to the action Observation: the result of the action

When you have a response to say to the Human, or if you do not need to use a tool, you MUST use the format:

Thought: Do I need to use a tool? No 
Final Answer: [Ensure the final answer strictly follows markdown syntax. The title should always start with one #. The final answer should be comprehensive, starting with a title, followed by a highly detailed table, clearly referencing the documents, including document names (which should be shortened to contain only necessary information when the document name is too long) and page numbers always. After the table, provide a "Summary Report" section in bullet points, with detailed explanations for each point. At the complete end, mention the documents where no answers were found or where only closely related information was found.]

When you have a response to say to the Human, or if you do not need to use a tool, you MUST use the format:


Additional Context:
New Input: {input}
Agent Scratchpad: {agent_scratchpad}
"""


#Previous Conversation History: {chat_history}


agent_prompt = PromptTemplate.from_template(agent_prompt_text)
agent = create_react_agent(llm, tools, agent_prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
)

chat_agent = RunnableWithMessageHistory(
    agent_executor,
    get_memory,
    input_messages_key="input",
    history_messages_key="chat_history",
    
)

# Create a handler to call the agent

def generate_response(user_input):
    """
    Create a handler that calls the Conversational agent
    and returns a response to be rendered in the UI
    """
    
    try:
        # Invoke the agent with error handling enabled for parsing
        response = chat_agent.invoke(
            {"input": user_input},
            config={"configurable": {"session_id": get_session_id()}}
        )
        
        # Log the full response for debugging
        print(f"Full response: {response}")
        
        # Attempt to parse the 'output' key first
        if 'output' in response:
            return response['output']
        
        # Fallback: Handle cases where output is nested or misformatted
        elif isinstance(response, dict):
            # If there's any text key or field in response, return that
            for key in response:
                if isinstance(response[key], str):
                    return response[key]
        
        # Fallback message in case of issues
        return "The output could not be parsed, please try again."
    
    except Exception as e:
        # Handle any exceptions (e.g., parsing, execution issues)
        print(f"Error encountered: {e}")
        return f"An error occurred during processing: {str(e)}"