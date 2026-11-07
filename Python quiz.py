

import json
import random
import time
from datetime import datetime


class Questions:
    POINTS = {"easy": 10, "medium": 20, "hard": 30}

    def __init__(self, text, category, difficulty, answer):
        self.text = text
        self.category = category
        self.difficulty = difficulty
        self.answer = answer

    def get_points(self):
        return Questions.POINTS[self.difficulty]

    def display(self):
        print(self.text)

    def is_correct(self, answer):
        return str(self.answer).lower() == str(answer).lower()


class MultipleChoiceQuestion(Questions):
    def __init__(self, text, category, difficulty, answer, options):
        super().__init__(text, category, difficulty, answer)
        self.options = options

    def display(self):
        print(self.text)
        for i, option in enumerate(self.options, start=1):
            print(f"{i}. {option}")

    def is_correct(self, answer):
        answer = str(answer).strip()

        if answer.isdigit():
            number = int(answer)
            if 1 <= number <= len(self.options):
                answer = self.options[number - 1]

        return str(self.answer).strip().lower() == answer.lower()


class TrueFalseQuestion(Questions):
    pass


class Question(Questions):
    pass


def load_questions(filename):
    questions = []

    try:
        with open(filename, "r") as file:
            data = json.load(file)

        for item in data:
            try:
                if item["type"] == "multiple":
                    question = MultipleChoiceQuestion(
                        item["text"],
                        item["category"],
                        item["difficulty"],
                        item["answer"],
                        item["options"]
                    )

                elif item["type"] == "truefalse":
                    question = TrueFalseQuestion(
                        item["text"],
                        item["category"],
                        item["difficulty"],
                        item["answer"]
                    )

                elif item["type"] == "typed":
                    question = Question(
                        item["text"],
                        item["category"],
                        item["difficulty"],
                        item["answer"]
                    )

                else:
                    continue

                questions.append(question)

            except KeyError:
                print(f"Warning: A question is missing information: {item}")

    except FileNotFoundError:
        print(f"Could not find {filename}.")

    except json.JSONDecodeError:
        print(f"Error reading {filename}. The JSON file is not formatted correctly.")

    return questions


# INTEGER INPUT VALIDATION
def get_int(prompt, low, high):
    while True:
        answer = input(prompt)

        if answer.isdigit():
            answer = int(answer)

            if low <= answer <= high:
                return answer

        print(f"Please enter a number between {low} and {high}.")


# CHOICE INPUT VALIDATION
def get_choice(prompt, valid_options):
    while True:
        answer = input(prompt).strip().lower()

        if answer in valid_options:
            return answer

        print("Invalid choice. Please try again.")


# CALCULATE POINTS
def calculate_points(question, streak, seconds):
    points = question.get_points()
    messages = []

    if seconds < 10:
        points += 5
        messages.append("speed bonus +5")

    if streak >= 3:
        points *= 2
        messages.insert(0, "streak x2")

    return points, messages


# INSERTION SORT - HIGHEST SCORE FIRST
def insertion_sort(highscores):
    for i in range(1, len(highscores)):
        key = highscores[i]
        j = i - 1

        while j >= 0 and highscores[j]["score"] < key["score"]:
            highscores[j + 1] = highscores[j]
            j -= 1

        highscores[j + 1] = key


# LOAD QUESTIONS
print("==============================")
print("          PYTHON QUIZ")
print("==============================")

loaded_questions = load_questions("questions.json")


# MAIN MENU
while True:
    print("\n1. Play")
    print("2. Highscores")
    print("3. Quit")

    choice = get_int("Choose an option: ", 1, 3)

    if choice == 1:

        # PLAYER NAME VALIDATION
        while True:
            player_name = input("Enter your name: ").strip()

            if 1 <= len(player_name) <= 20:
                break

            print("Your name must be between 1 and 20 characters.")

        print(f"Hello {player_name}, welcome to the quiz game!")

        # CATEGORY SELECTION
        categories = []

        for question in loaded_questions:
            if question.category not in categories:
                categories.append(question.category)

        categories.sort()

        print("\nChoose a category:")
        print("0. All")

        for i in range(len(categories)):
            print(f"{i + 1}. {categories[i]}")

        category_choice = get_int(
            "Choose a category: ", 0, len(categories)
        )

        if category_choice == 0:
            selected_category = "All"
        else:
            selected_category = categories[category_choice - 1]

        # DIFFICULTY SELECTION
        print("\nChoose a difficulty:")
        print("1. Easy")
        print("2. Medium")
        print("3. Hard")
        print("4. Mixed")

        difficulty_choice = get_int(
            "Choose a difficulty: ", 1, 4
        )

        if difficulty_choice == 1:
            selected_difficulty = "easy"

        elif difficulty_choice == 2:
            selected_difficulty = "medium"

        elif difficulty_choice == 3:
            selected_difficulty = "hard"

        else:
            selected_difficulty = "Mixed"

        # FILTER QUESTIONS
        filtered_questions = []

        for question in loaded_questions:
            category_matches = (
                selected_category == "All"
                or question.category == selected_category
            )

            difficulty_matches = (
                selected_difficulty == "Mixed"
                or question.difficulty == selected_difficulty
            )

            if category_matches and difficulty_matches:
                filtered_questions.append(question)

        if len(filtered_questions) == 0:
            print("There are no questions matching your choices.")
            continue

        if len(filtered_questions) < 10:
            print(f"There are only {len(filtered_questions)} questions available.")

        # KEEP THE 10-QUESTION LIMIT
        selected_questions = random.sample(
            filtered_questions,
            min(10, len(filtered_questions))
        )

        # GAME VARIABLES
        score = 0
        lives = 3
        streak = 0
        used_5050 = False

        # GAMEPLAY
        for question in selected_questions:

            if lives == 0:
                break

            print("\n--------------------")
            print(f"Score: {score}")
            print(f"Lives: {lives}")

            question.display()

            start_time = time.time()

            if isinstance(question, TrueFalseQuestion):

                answer = get_choice(
                    "Type True or False: ",
                    ["true", "false"]
                )

            elif isinstance(question, MultipleChoiceQuestion):

                valid_answers = [
                    str(i) for i in range(1, len(question.options) + 1)
                ]

                valid_answers.append("50")

                answer = get_choice(
                    "Your answer (or type 50 for 50/50): ",
                    valid_answers
                )

                if answer == "50":

                    if used_5050:
                        print("You have already used your 50/50 lifeline.")

                        answer = get_choice(
                            "Your answer: ",
                            valid_answers[:-1]
                        )

                    else:
                        used_5050 = True

                        wrong_options = []

                        for i, option in enumerate(question.options):
                            if str(option).lower() != str(question.answer).lower():
                                wrong_options.append(i)

                        removed_options = random.sample(
                            wrong_options,
                            min(2, len(wrong_options))
                        )

                        print("\n50/50 lifeline used!")

                        for i, option in enumerate(question.options, start=1):
                            if i - 1 not in removed_options:
                                print(f"{i}. {option}")

                        answer = get_choice(
                            "Your answer: ",
                            valid_answers[:-1]
                        )

            else:
                answer = input("Your answer: ").strip()

                while answer == "":
                    print("Your answer cannot be empty.")
                    answer = input("Your answer: ").strip()

            end_time = time.time()
            seconds = end_time - start_time

            # CHECK ANSWER AND CALCULATE SCORE
            if question.is_correct(answer):
                streak += 1

                points, messages = calculate_points(
                    question, streak, seconds
                )

                score += points

                bonus_text = ""

                if messages:
                    bonus_text = " (" + ", ".join(messages) + ")"

                print(f"Correct! +{points}{bonus_text}")

            else:
                print(f"Incorrect! The correct answer was {question.answer}")
                lives -= 1
                streak = 0

        # GAME SUMMARY
        print("\n--------------------")
        print("Game over!")
        print(f"Final score: {score}")
        print(f"Lives remaining: {lives}")

        if lives > 0:
            print("You completed all the questions!")

        # SAVE HIGHSCORES
        try:
            with open("highscores.json", "r") as file:
                highscores = json.load(file)

        except FileNotFoundError:
            highscores = []

        highscores.append({
            "name": player_name,
            "score": score,
            "date": datetime.now().strftime("%d/%m/%Y")
        })

        insertion_sort(highscores)

        with open("highscores.json", "w") as file:
            json.dump(highscores, file, indent=4)

    elif choice == 2:

        # DISPLAY HIGHSCORES
        try:
            with open("highscores.json", "r") as file:
                highscores = json.load(file)

        except FileNotFoundError:
            highscores = []

        insertion_sort(highscores)

        print("\n--- Highscores ---")

        if len(highscores) == 0:
            print("No highscores yet!")

        for i in range(len(highscores)):
            print(
                f"{i + 1}. {highscores[i]['name']} - "
                f"{highscores[i]['score']} points - "
                f"{highscores[i]['date']}"
            )

    elif choice == 3:
        print("Goodbye!")
        break
