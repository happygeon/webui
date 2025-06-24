from bs4 import BeautifulSoup

for i in range(113):
    # Load HTML content
    try:
        with open(f"./output/html/{i}.html", "r", encoding="utf-8") as file:
            html_content = file.read()
    except FileNotFoundError:
        continue

    # Parse the HTML using BeautifulSoup
    soup = BeautifulSoup(html_content, "html.parser")

    # Remove <style>, <script>, <link>, <meta>, and other non-structural tags
    for tag in soup(["style", "script", "link", "meta", "noscript", "iframe", "svg"]):
        tag.decompose()

    # Remove all inline styles, class, id, data-* attributes, etc.
    for tag in soup(True):
        tag.attrs = {k: v for k, v in tag.attrs.items() if k not in ["style", "class", "id"] and not k.startswith("data-")}

    # Save the cleaned HTML structure to a new file
    output_path = f"./output/after_html/{i}.html"
    with open(output_path, "w", encoding="utf-8") as file:
        file.write(str(soup))