from taipy.gui import Gui
from taipy.designer import Page
import copy


fruits = [
    "Apple",
    "Banana",
    "Orange",
    "Mango",
    "Strawberry",
    "Grapes",
    "Watermelon",
    "Pineapple",
    "Cherry",
    "Peach",
    "Papaya",
    "Kiwi",
    "Plum",
    "Pomegranate",
    "Blueberry",
    "Raspberry",
    "Blackberry",
    "Cantaloupe",
    "Lemon",
    "Lime",
]

seleced_fruit = fruits[0]

list_fruits = []


def add_fruit_to_list(state):
    list_fruits = state.list_fruits
    list_fruits.append(state.seleced_fruit)
    state.list_fruits = copy.deepcopy(list_fruits)


page = Page("o_crud_template.xprjson")
Gui(page).run(design=True)
