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
from tools.cypher import cypher_qa


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
    Tool.from_function(
        name="General Chat",
        description="For general medical inquiries not covered by other tools",
        func=medic_chat.invoke,
    ), 
    Tool.from_function(
        name="Query Regulation Documents",
        description="For when a user needs information about Mecial practices as strictly described in the documents and it users vector search",
        func=get_medic_docs,
    ),
    # Tool.from_function(
    #     name="Generate Table",
    #     description="Generates a well-formatted table from input data, returning the table in markdown format.",
    #     func=generate_dynamic_table,
    # ),
    # Tool.from_function(
    #     name="Document information",
    #     description="Provide information about about Mecial practices as strictly described in the documents and it is using cypher search",
    #     func = cypher_qa,
    # )
]

# Create chat history callback
def get_memory(session_id):
    return Neo4jChatMessageHistory(session_id=session_id, graph=graph)

# Create the agent
agent_prompt_text =  """
Role and Objective:
You are an AI Assistant specializing in medical regulatory practices. You will analyze and provide guidance based on documents from five medical associations using the "Query Regulation Documents" tool and other available tools to complete the tasks effectively.
You are working with 3 instituions  ABRL,  MURC and GHRI so when reffered in querry as instituions you have to pull out information of all the three even if not mentioned by the user , and if you dont have particular information of a certian insitute then you just specifc that uyou couldnt retrieve but you always check for all
Primary Task:
Your goal is to assist users by answering questions about medical regulations, ensuring responses are precise, detailed, and contextually accurate. You must use the available tools at each step to gather, process, and present the required information.

Important information when you are doing your search using the tools to querry document, and if the question contain multiple question in one, for example: would you be able to give me the best restaurant in germany, luxembourg and turkish. As you can see the location are different making it 3 search rather than one search. so make sure you querry the database three time for the amount of question within input.
Another important information always ask for variation of the question, change the meaning, or ask for specific information to get more data from it. for example you may get questions like : How does the 3 institution have the ability to do something, now you see you may not know what are the three institution, therefore you may ask more information on that particular part.
So you will have a better understanding of the question the user ask and you have the ability to give more correct and precise answer, so ask a buch of querries to the database gather information and then reply, minimum should be 5 questions asked.
You have access to the following tools:

{tools}

To use a tool, please use the following format:

```
Thought: Do I need to use a tool? Yes
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action

```

When you have a response to say to the Human, or if you do not need to use a tool, you MUST use the format:

```

Thought: Do I need to use a tool? No
Final Answer: [Make sure that the final answer is strickly in markdown, and do not pass the thinking process or any other information of the process within the final answer also the title should only contain one "#" when starting ok all time: The final answer should be a detail answer, first what you will do is create a tite which is going to be the start of the answer, then you will create a table a very detailed one and mention the reference within the table in a collum, you mention the document it come from and the page if any given, then you will provied a summary report with a title then the summary in bullet point, the summary in bullet point should be detailed.]

```

Additional Context:
Previous Conversation History: {chat_history}
New Input: {input}
Agent Scratchpad: {agent_scratchpad}

"""

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
