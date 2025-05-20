import json
import re
from gradio_client import Client
# Path to the JSON file
file_path = r'./books_reference_queries/books_reference_queries.json'

# Read and parse the JSON file
try:
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        print("Data loaded successfully.")
        print(data)  # Print the data or process it as needed
except FileNotFoundError:
    print(f"File not found: {file_path}")
except json.JSONDecodeError as e:
    print(f"Error decoding JSON: {e}")
    
for i in data[:10]:
    query = i['query']
    

    client = Client("Qwen/Qwen2.5-Coder-demo")
    result = client.predict(
            query=query,
            history=[],
            system="You are Qwen, created by Alibaba Cloud. You are a helpful assistant.",
            radio="7B",
            api_name="/model_chat"
    )
    print(result)
    print("-------------------------------------------------")
    htmlfile = result[1][0][1]
    
    matches = re.findall(r'```(.*?)```', htmlfile, re.DOTALL)

    # 결과 출력
    print(matches)