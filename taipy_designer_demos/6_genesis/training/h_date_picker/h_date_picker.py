from taipy.gui import Gui
from taipy.designer import Page


selected_date = "2021-01-01"

page = Page("h_date_picker.xprjson")
Gui(page).run(design=True)
