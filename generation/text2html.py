from LLM import LLM
import re
from html2image import Html2Image

hti = Html2Image(
    browser="chrome", 
    custom_flags=[
        '--no-sandbox', 
        '--headless', 
        '--disable-gpu', 
        '--disable-software-rasterizer', 
        '--disable-dev-shm-usage'
    ])

GROQ_API_KEY = ""

ui_agent = LLM("llama",GROQ_API_KEY)

design_requests = [
    "Modern and sleek coffee ordering webpage.The webpage should have a warm, elegant aesthetic with a color palette of mocha brown, cream, and charcoal, accented with a pop color like muted orange or gold. Use a stylish serif font like 'Playfair Display' for headings and a clean sans-serif like 'Inter' or 'Roboto' for body text. The layout should be minimalist, using card-based UI and grid displays with soft shadows, rounded corners, and smooth transitions. The header should be sticky and slightly transparent, featuring a logo on the left, navigation links (Home, Menu, Order, About, Contact), and a profile/login icon on the right. The hero section can have a full-screen background video or image with a tagline like “Brewed Fresh. Served Fast.” and a primary CTA button. The menu should display coffee items in interactive cards with images, names, prices, and a “Customize” or “Add to Cart” button. Clicking “Customize” opens a modal with options for size, milk, and add-ons, with real-time price updates. A cart sidebar should slide in from the right, showing selected items, total price, and checkout options. The checkout section should include floating label forms, order summary, and payment choices with a clear progress bar. The footer should contain contact info, social links, a newsletter field, and a light/dark mode toggle. Mobile design should include a responsive layout, burger menu, sticky bottom CTA, and tap-friendly interactions. Additional nice touches include microinteractions, PWA support, and an animated order confirmation screen.",
    "A travel blog website that includes a personal diary of global adventures.",
    "A website for a personal health and wellness coach offering one-on-one coaching sessions.",
    "A sleek and modern landing page for a new tech startup.",
    "A corporate blog for a tech company that provides industry news, product updates, and thought leadership content.",
    "A sophisticated, image-driven portfolio website for a professional photographer.",
    "An educational website for an online course provider.",
    "A local restaurant that features an online ordering system.",
    "A non-profit organization that focuses on environmental conservation.",
    "A modern, responsive e-commerce website with a clean, minimalist design that includes a user-friendly product search and checkout system.",
    "A modern, user-friendly e-commerce website for a fashion retailer.",
    ]


for d in range(4):
    prompt = f"""
    You are a frontend engineer in HTML/CSS/JS.

    Your task is to generate a website.

    The design request is:
    {design_requests[d]}

    ONLY output html and answer strictly in the given format with html/css/js all integrated in one file:
    ```html
    <html>
        ...
    </html>
    ```
    """
    for i in range(3):
        htmlcode = ui_agent.run(prompt)
        match = re.search(r"<html>.*?</html>", htmlcode, flags=re.DOTALL | re.IGNORECASE)
        clean_html = match.group(0) if match else ""

        #save clean_html to file in a directory called codes
        with open(f"{d}_test_{i}.html", "w") as f:
            f.write(clean_html)
        hti.screenshot(html_str=clean_html, save_as=f"{d}_test_{i}.png")