from drafter import *
from dataclasses import dataclass

set_website_title("Dental Tooth Explorer")
set_website_style("daub")

add_website_css("""
body {
    font-family: Georgia, "Times New Roman", serif;
    max-width: 900px;
    margin: 0 auto;
    padding: 24px 32px;
    background: linear-gradient(135deg, #e6f4f4 0%, #f7fcfc 100%);
    color: #0b2545;
    line-height: 1.6;
}

h1, h2, h3 {
    font-family: Georgia, "Times New Roman", serif;
    font-weight: 700;
    color: #0b2545;
}

h1 {
    font-size: 2.6rem;
    margin-bottom: 12px;
}

input[type="text"], select {
    padding: 6px 10px;
    border: 2px solid #14919b;
    border-radius: 6px;
    color: #0b2545;
    background: white;
    font-size: 1rem;
}
""")
hide_debug_information()
# ---------------------------------------------------------------- Dataclasses

@dataclass
class Tooth:
    number: int
    name: str
    location: str
    category: str


@dataclass
class State:
    tooth_number: int
    tooth_name: str
    score: int
    question_number: int
    feedback: str
    teeth_list: list[Tooth]


# ---------------------------------------------------------------- Data

# Names for the 8 teeth in one quadrant, listed from the back of the mouth
# (third molar) to the front (central incisor).
BACK_TO_FRONT = [
    ("Third Molar", "Molar"),
    ("Second Molar", "Molar"),
    ("First Molar", "Molar"),
    ("Second Premolar", "Premolar"),
    ("First Premolar", "Premolar"),
    ("Canine", "Canine"),
    ("Lateral Incisor", "Incisor"),
    ("Central Incisor", "Incisor"),
]

CATEGORIES = ["Incisor", "Canine", "Premolar", "Molar"]

# Fixed quiz: (tooth number, question type)
QUIZ = [
    (8, "name"), (30, "category"), (3, "name"), (14, "category"), (22, "name"),
    (5, "category"), (19, "name"), (11, "category"), (1, "name"), (25, "category"),
]


def build_teeth():
    """Build all 32 teeth (Universal Numbering System)."""
    teeth = []
    for number in range(1, 33):
        if number <= 8:
            location = "Upper Right"
            index = number - 1            # 1 = third molar ... 8 = central incisor
        elif number <= 16:
            location = "Upper Left"
            index = 16 - number           # 9 = central incisor ... 16 = third molar
        elif number <= 24:
            location = "Lower Left"
            index = number - 17           # 17 = third molar ... 24 = central incisor
        else:
            location = "Lower Right"
            index = 32 - number           # 25 = central incisor ... 32 = third molar
        name, category = BACK_TO_FRONT[index]
        teeth.append(Tooth(number, name, location, category))
    return teeth


def find_tooth(state: State, number: int):
    """Loop through the State's teeth_list until the number matches."""
    for tooth in state.teeth_list:
        if tooth.number == number:
            return tooth
    return None


def teeth_in_category(state: State, category: str):
    found = []
    for tooth in state.teeth_list:
        if tooth.category == category:
            found.append(tooth)
    return found

# --------------------------------------------------- style design
@route
def index() -> Page:
    return Page([
        Header("Dental Tooth Explorer"),
        "Ordinary text, a link, and a form, in this theme.\n",
        Link("A link", "index"),
        "\nA field:",
        TextBox("field", "typed text"),
        "\n",
        Button("A button", "index")
    ])

# ---------------------------------------------------------------- Home

@route
def index(state: State) -> Page:
    return home(state)


@route
def home(state: State) -> Page:
    return Page(state, [
        Header("Dental Tooth Explorer", 1),
        Text("Learn the Tooth Numbering System!"),
        Text("Look up any of the 32 adult teeth, read about each tooth type, "
             "or test your knowledge with a quiz."),
        LineBreak(),
        Button("Tooth Finder", tooth_finder),
        Button("Take Quiz", start_quiz),
        Button("About Teeth", about_page),
    ])


# ---------------------------------------------------------------- Tooth finder

def chart_rows():
    upper = " ".join(str(n) for n in range(1, 17))
    lower = " ".join(str(n) for n in range(32, 16, -1))
    return [upper, lower]


@route
def tooth_finder(state: State) -> Page:
    upper, lower = chart_rows()
    return Page(state, [
        Header("Tooth Finder", 1),
        Text("International (Universal) Tooth Numbering Chart"),
        Text("Upper (right to left):  " + upper),
        Text("Lower (right to left):  " + lower),
        LineBreak(),
        Text("Enter a tooth number (1-32):"),
        TextBox("number", ""),
        Button("Search", search_tooth),
        LineBreak(),
        Button("Home", home),
    ])


@route
def search_tooth(state: State, number: str) -> Page:
    upper, lower = chart_rows()
    results = []

    cleaned = number.strip()
    if not cleaned.isdigit() or int(cleaned) < 1 or int(cleaned) > 32:
        # If statement 1: number out of range / not a number -> error
        results = [Text("Error: please enter a whole number from 1 to 32.")]
    else:
        tooth = find_tooth(state, int(cleaned))
        # If statement 2: number matches a tooth -> show its info
        if tooth is not None:
            state.tooth_number = tooth.number
            state.tooth_name = tooth.name
            results = [
                HorizontalRule(),
                Header("Results for Tooth #" + str(tooth.number), 2),
                Table([
                    ["Detail", "Info"],
                    ["Name", tooth.name],
                    ["Location", tooth.location],
                    ["Type", tooth.category],
                ]),
            ]
        else:
            results = [Text("Error: that tooth could not be found.")]

    return Page(state, [
        Header("Tooth Finder", 1),
        Text("International (Universal) Tooth Numbering Chart"),
        Text("Upper (right to left):  " + upper),
        Text("Lower (right to left):  " + lower),
        LineBreak(),
        Text("Enter a tooth number (1-32):"),
        TextBox("number", cleaned if cleaned else ""),
        Button("Search", search_tooth),
        LineBreak(),
    ] + results + [
        LineBreak(),
        Button("Home", home),
    ])
# ---------------------------------------------------------------- Quiz

@route
def start_quiz(state: State) -> Page:
    state.score = 0
    state.question_number = 0
    state.feedback = ""
    return quiz_page(state)


@route
def quiz_page(state: State) -> Page:
    number, kind = QUIZ[state.question_number]
    content = [
        Header("Tooth Number Quiz", 1),
        Text("Question " + str(state.question_number + 1) + " of " + str(len(QUIZ))
             + "   |   Score: " + str(state.score)),
    ]
    if state.feedback != "":
        content.append(Text(state.feedback))
    content.append(LineBreak())

    if kind == "name":
        content.append(Text("What is the name of Tooth #" + str(number) + "?"))
        content.append(Text("(Example format: Central Incisor, Second Molar)"))
        content.append(TextBox("answer", ""))
    else:
        content.append(Text("What type of tooth is Tooth #" + str(number) + "?"))
        content.append(SelectBox("answer", CATEGORIES, CATEGORIES[0]))

    content.append(Button("Submit", check_answer))
    content.append(LineBreak())
    content.append(Button("Quit to Home", home))
    return Page(state, content)


@route
def check_answer(state: State, answer: str) -> Page:
    number, kind = QUIZ[state.question_number]
    tooth = find_tooth(state, number)

    if kind == "name":
        correct = tooth.name
    else:
        correct = tooth.category

    # If statement 3: correct answer adds a point, otherwise score is unchanged
    if answer.strip().lower() == correct.lower():
        state.score += 1
        state.feedback = "Correct! Tooth #" + str(number) + " is the " + correct + "."
    else:
        state.feedback = "Not quite. Tooth #" + str(number) + " is the " + correct + "."

    state.question_number += 1

    # If statement 4: finished all questions -> results page
    if state.question_number >= len(QUIZ):
        return quiz_results(state)
    return quiz_page(state)


@route
def quiz_results(state: State) -> Page:
    total = len(QUIZ)
    if state.score >= 8:
        message = "Excellent work!"
    elif state.score >= 5:
        message = "Good job. Review the tooth pages and try again!"
    else:
        message = "Keep studying, you'll get it!"
    return Page(state, [
        Header("Quiz Results", 1),
        Text(state.feedback),
        Text("Your Score: " + str(state.score) + "/" + str(total)),
        Text(message),
        LineBreak(),
        Button("Try Again", start_quiz),
        Button("Home", home),
    ])


# ---------------------------------------------------------------- About teeth

@route
def about_page(state: State) -> Page:
    return Page(state, [
        Header("About Teeth", 1),
        Text("Learn about:"),
        Button("Incisors", incisors_page),
        Button("Canines", canines_page),
        Button("Premolars", premolars_page),
        Button("Molars", molars_page),
        LineBreak(),
        Button("Home", home),
    ])


def category_page(state: State, title: str, category: str, description: str) -> Page:
    rows = [["Tooth #", "Name", "Location"]]
    for tooth in teeth_in_category(state, category):
        rows.append([str(tooth.number), tooth.name, tooth.location])
    return Page(state, [
        Header(title, 1),
        Text(description),
        HorizontalRule(),
        Header("There are " + str(len(rows) - 1) + " in the adult mouth", 2),
        Table(rows),
        HorizontalRule(),
        Button("Back to About Teeth", about_page),
        Button("Home", home),
    ])

@route
def incisors_page(state: State) -> Page:
    return category_page(state, "Incisors", "Incisor",
                         "Incisors are the thin, flat front teeth used for cutting food.")


@route
def canines_page(state: State) -> Page:
    return category_page(state, "Canines", "Canine",
                         "Canines are the pointed teeth next to the incisors, used for tearing food.")


@route
def premolars_page(state: State) -> Page:
    return category_page(state, "Premolars", "Premolar",
                         "Premolars sit between the canines and molars and are used for crushing and tearing.")


@route
def molars_page(state: State) -> Page:
    return category_page(state, "Molars", "Molar",
                         "Molars are the large back teeth used for grinding food. "
                         "The third molars are also called wisdom teeth.")


start_server(State(0, "", 0, 0, "", build_teeth()))
