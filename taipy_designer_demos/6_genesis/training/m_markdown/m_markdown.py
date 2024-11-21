from taipy.gui import Gui
from taipy.designer import Page


# Open the file in read mode ('r')
with open('example.md', 'r') as file:
    # Read the content of the file into a string
    markdown_content = file.read()


page = Page("m_markdown.xprjson")
Gui(page).run(design=True)
