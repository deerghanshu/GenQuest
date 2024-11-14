import os  
from openai import AzureOpenAI  

endpoint = os.getenv("ENDPOINT_URL", "https://genai-openai-teamgenquest.openai.azure.com/")  
deployment = os.getenv("DEPLOYMENT_NAME", "gpt-4o")  
search_endpoint = os.getenv("SEARCH_ENDPOINT", "https://barc-genai-test.search.windows.net")  
search_key = os.getenv("SEARCH_KEY", "XXXXX")  
search_index = os.getenv("SEARCH_INDEX_NAME", "openaiindex")  
subscription_key = os.getenv("AZURE_OPENAI_API_KEY", "XXXXX")  

# Initialize Azure OpenAI client with key-based authentication
client = AzureOpenAI(  
  azure_endpoint=endpoint,  
  api_key=subscription_key,  
  api_version="2024-05-01-preview",  
)  

role_info = "You are an AI assistant that helps people find information. Always, try to include graph or tables along with your answer."

post_query = """

Determine if you can create any kind of graphical representation on the related topic.
You can only create line graph, and/or bar graph.
Give the output in a specific json format for all the further responses.
Give a text output with a general description as well. Give that whole text output as a value to the field with the name "text". Add "\n" to the text value after every paragraph break, wherever necessary.
Don't inlcude any pretext or posttext to this json output. Json should compulsorily contain a field called as "isgraph" which is a boolean which will tell if graph data is present. Other json field would be "data" which is a nested json object.
If the graph type is line graph
The nested json object in "data" field contain a field "type" with value "line" which contains two arrays, "x" and "y"
If the graph type is bar graph,
the nested json object in "data" field contain a field "type" with value "bar" which contains two arrays, "x", "y" and "z" wi where "x" and "y" represent data points and "z" is the value at (x,y)
"""

# Prepare the chat prompt  
init_prompt = [
  {
    "role": "system",
    "content": role_info
  }
]

# Generate the completion  
def generate_completion(user_query, chat_history):
  if not chat_history:
    chat_history = init_prompt
  chat_history = append_to_chat_history(chat_history, "user", user_query)
  completion = client.chat.completions.create(  
    model=deployment,  
    messages=chat_history,
    max_tokens=800,  
    temperature=0.7,  
    top_p=0.95,  
    frequency_penalty=0,  
    presence_penalty=0,  
    stop=None,  
    stream=False,
    extra_body={
      "data_sources": [{
        "type": "azure_search",
        "parameters": {
          "endpoint": f"{search_endpoint}",
          "index_name": f"{search_index}",
          "semantic_configuration": "default",
          "query_type": "vector_simple_hybrid",
          "fields_mapping": {},
          "in_scope": True,
          "role_information": role_info,
          "filter": None,
          "strictness": 3,
          "top_n_documents": 5,
          "authentication": {
            "type": "api_key",
            "key": f"{search_key}"
          },
          "embedding_dependency": {
            "type": "deployment_name",
            "deployment_name": "text-embedding-ada-002"
          }
        }
      }]
    })   
  response = completion.choices[0].message.content
  chat_history = append_to_chat_history(chat_history, "assistant", response, user_query)
  return chat_history

def append_to_chat_history(chat_history, role, message, query=""):
  if role=="assistant":
    uq = chat_history[-1]
    uq["content"] = query
    chat_history[-1] = uq
    message = message[7:-3].strip()
  else:
    message += post_query

  chat_history.append({
    "role": role,
    "content": message
  })
  return chat_history

# a = generate_completion("What are the major outcomes of breaches in businesses between 2018 and 2021?", [])
# print(a[-1]["content"])
#
# b = generate_completion("Tell me the reasons behind this?", a)
# print(b[-1]["content"])
