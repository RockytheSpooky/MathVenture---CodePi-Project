from flask import Flask, render_template, request, redirect, url_for, session
from worlds import fractions, geometry, algebra

app = Flask(__name__)
app.secret_key = "mathventure_secret"

def get_questions_for_world(world_name):
    if world_name == "fractions":
        return fractions.questions
    elif world_name == "geometry":
        return geometry.questions
    elif world_name == "algebra":
        return algebra.questions
    return None

@app.before_request
def clear_session_on_home():
    if request.endpoint == 'index':
        session.clear()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/world/<world_name>", methods=["GET", "POST"])
def math_world(world_name):
    questions = get_questions_for_world(world_name)
    if questions is None:
        return "World not found", 404

    level_key = f"{world_name}_level"
    hint_key = f"{world_name}_hints"
    level = session.get(level_key, 0)
    hints = session.get(hint_key, 0)

    if level >= len(questions):
        return render_template("result.html", correct=True, completed=True, world=world_name)

    question = questions[level]
    show_answer = False
    revealed_answer = None

    if request.method == "POST":
        selected = request.form.get("answer")
        correct = question["answer"]
        if selected == correct:
            session[level_key] = level + 1
            session[hint_key] = 0
            return redirect(url_for("math_world", world_name=world_name))
        else:
            hints += 1
            session[hint_key] = hints
            if hints >= 3:
                show_answer = True
                revealed_answer = correct

    return render_template("math_world.html",
                           world=world_name,
                           level=level + 1,
                           question=question,
                           incorrect=hints > 0,
                           hints=hints,
                           show_answer=show_answer,
                           revealed_answer=revealed_answer)

@app.route("/puzzle", methods=["GET", "POST"])
def puzzle():
    puzzle_question = {
        "question": "What 3-digit number is equal to the sum of the cubes of its digits?",
        "answer": "153",
        "hints": [
            "Try breaking the number into its digits: 1, 5, 3.",
            "Now cube each digit and add them: 1³ + 5³ + 3³"
        ]
    }

    attempts = session.get("puzzle_attempts", 0)
    hint = puzzle_question["hints"][min(attempts, 1)] if attempts < 2 else None
    show_answer = False

    if request.method == "POST":
        user_answer = request.form.get("answer", "").strip()
        if user_answer == puzzle_question["answer"]:
            session["puzzle_done"] = True
            session["puzzle_attempts"] = 0
            return render_template("result.html", correct=True, completed=True, world="puzzle")
        else:
            attempts += 1
            session["puzzle_attempts"] = attempts
            if attempts >= 3:
                show_answer = True

    return render_template("puzzle.html",
                           question=puzzle_question["question"],
                           incorrect=attempts > 0,
                           hint=hint,
                           show_answer=show_answer,
                           revealed_answer=puzzle_question["answer"] if show_answer else None)

@app.route("/bot", methods=["GET", "POST"])
def math_bot():
    response = None
    if request.method == "POST":
        user_input = request.form.get("question", "").lower()

        responses = {
            "simplifying": "Simplifying means making an expression shorter or easier to work with.",
            "distribute": "We distribute in expressions like 2(x + 3) to multiply 2 with both x and 3: 2x + 6.",
            "fully simplified": "An equation is fully simplified when all like terms are combined and it's as short as possible.",
            "solve 3x": "To solve 3x = 12, divide both sides by 3. The answer is x = 4.",
            "solving vs simplifying": "Solving means finding the value of a variable. Simplifying means reducing the expression.",
            "why solve": "We solve for x to find the unknown value in an equation.",
            "check answer": "Plug your solution back into the original equation to check if it works.",
            "4x + 8 = 48": "Subtract 8 from both sides: 4x = 40. Then divide by 4: x = 10.",
            "triangle angles": "The angles in a triangle always add up to 180°.",
            "polygon sides": "Use memory tricks: hex = 6 (like hexagon), pent = 5 (like Pentagon), etc.",
            "regular vs irregular": "A regular shape has all sides and angles equal. Irregular doesn't.",
            "area rectangle": "Multiply length × width. Area = 7 × 3 = 21, for example.",
            "why area": "Area tells us how much space is inside a shape.",
            "length vs width": "Order doesn't matter in multiplication, so length × width = width × length.",
            "geometry in life": "Geometry is used in building, design, navigation, and art.",
            "add fractions": "Find a common denominator, then add the numerators.",
            "1/2 + 1/4": "Convert to same denominator: 2/4 + 1/4 = 3/4. Not 2/6.",
            "simplify fractions": "Divide the top and bottom by the same number to simplify.",
            "smallest fraction": "Compare by common denominators or visualize. 1/3 is smaller than 1/2.",
            "greater fraction": "A 'greater' fraction has a larger value, like 3/4 > 1/2.",
            "3/5 of 20": "Multiply: 3/5 × 20 = 12.",
            "fractions in life": "Fractions are used in cooking, time, money, and measuring."
        }

        response = responses.get(user_input, "Hmm, I don’t know that one yet!")

    return render_template("math_bot.html", response=response)


if __name__ == "__main__":
    app.run(debug=True)
