from taipy.gui import Gui
from taipy.designer import Page


a = 1
b = 5
c = a + b


def on_change(state, var, val):
    if var == "a" or var == "b":
        state.c = state.a + state.b


page = Page("a_sliders_value.xprjson")
Gui(page).run(design=True)
