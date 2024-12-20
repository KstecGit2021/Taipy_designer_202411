from taipy.gui import Gui
from taipy.designer import Page


def print_message(select_fruit):
    message = "The selected fruit is: " + select_fruit
    return message


fruits = [
    "apple",
    "banana",
    "cherry",
    "date",
    "elderberry",
    "fig",
    "grape",
    "kiwi",
    "lemon",
    "mango",
]
select_fruit = fruits[0]
message = print_message(select_fruit)


def on_change(state, var, val):
    if var == "select_fruit":
        state.message = print_message(state.select_fruit)


page = Page("f_select.xprjson")
Gui(page).run(design=True)
