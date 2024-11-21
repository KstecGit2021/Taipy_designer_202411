from taipy.gui import Gui
from taipy.designer import Page
import plotly.express as px


fig = px.imshow([[1, 20, 30], [20, 1, 60], [30, 60, 1]])


page = Page("i_plotly_figure.xprjson")
Gui(page).run(design=True)
