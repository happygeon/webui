import json
import re
from gradio_client import Client
# Path to the JSON file
file_path = r'./ui_design_results.json'

# Read and parse the JSON file
try:
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        print("Data loaded successfully.")
        #print(data)  # Print the data or process it as needed
except FileNotFoundError:
    print(f"File not found: {file_path}")
except json.JSONDecodeError as e:
    print(f"Error decoding JSON: {e}")

def preprocess_html(html):
    return re.sub(r'\\n', '', html)

import re

def extract_html_and_save(response, index, is_enhance="_enhance", folder = "./response/"):
    """
    Extracts the HTML block from <html> to </html> using regex and saves it to a file.
    
    Parameters:
        text (str): The full input text containing HTML content.
        output_file (str): The name of the file to save the extracted HTML. Default is 'ex1.html'.
    """
    # 정규 표현식을 이용해 <html> 태그부터 </html>까지 매칭 (DOTALL: 줄바꿈 포함)
    match = re.search(r'<html.*?</html>', response, re.DOTALL | re.IGNORECASE)
    match = match.group()
    match = preprocess_html(match)
    if match:
        output_file = folder + str(index) + is_enhance +".html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(match)
        print(f"✅ HTML content saved to '{output_file}'")
    else:
        print("❌ No <html>...</html> block found in the text.")


for index, i in enumerate(data[:10]):
    
    query = i['query']
    file = i['html']
    file = preprocess_html(file)
    extract_html_and_save(file, index, is_enhance="")
    
    merge_query = f"""
    Enhance the following HTML by adding embedded CSS and JavaScript to improve its appearance and interactivity.

    - Add styling to make the layout visually appealing, considering aesthetics, readability, and balance.
    - If the HTML includes menus, buttons, or other interactive elements, make them interactive and visually responsive using JavaScript (e.g., collapsible menus, hover effects).
    - If there is navigation or a sidebar, style it appropriately; if not, simply style the existing structure to look clean and well-designed.
    - Choose a suitable color palette and typography that fits the context (e.g., a coffee shop or ecommerce site, if applicable).
    - All CSS and JavaScript should be embedded within the HTML.
    - Do not change the content or semantic structure unless necessary for visual or interactive improvements.

    Return the complete 'one' enhanced HTML FILE.
    """
    merge_query = query+merge_query+file
    
    client = Client("Qwen/Qwen2.5-Coder-demo")
    result = client.predict(
            query=merge_query,
            history=[],
            system="You are Qwen, created by Alibaba Cloud. You are a helpful assistant.",
            radio="7B",
            api_name="/model_chat"
    )
    htmlfile = result[1][0][1]
    extract_html_and_save(htmlfile, index)