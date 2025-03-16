import nltk
from nltk.corpus import words
from nltk.corpus import wordnet
import random
import customtkinter as ctk
from collections import Counter
import requests
from bs4 import BeautifulSoup
import urllib.request
import re

try:
    nltk.data.find("corpora/words.zip")
except LookupError:
    nltk.download("words")

try:
    nltk.data.find("corpora/wordnet.zip")
except LookupError:
    nltk.download("wordnet")

difficulty = ""
number_of_guesses = None
min_word_length = None
max_word_length = None
word_list = []
word_length = None
guesses_left = None
guessed_letters_list = []
word_display = []
definition = ""


def show_settings():
    settings_frame.pack(fill="both", expand=True)
    game_frame.pack_forget()


def select_difficulty(selected_difficulty):
    global difficulty, number_of_guesses

    if selected_difficulty == "Novice":
        difficulty = "Novice"
    if selected_difficulty == "Easy":
        difficulty = "Easy"
    if selected_difficulty == "Medium":
        difficulty = "Medium"
    if selected_difficulty == "Hard":
        difficulty = "Hard"
    if selected_difficulty == "Impossible":
        difficulty = "Impossible"

    if difficulty == "Novice":
        number_of_guesses = 10
    if difficulty == "Easy":
        number_of_guesses = 9
    if difficulty == "Medium":
        number_of_guesses = 8
    if difficulty == "Hard":
        number_of_guesses = 7
    if difficulty == "Impossible":
        number_of_guesses = 6

    setup_game()
    show_game()


def show_game():
    settings_frame.pack_forget()
    game_frame.pack(fill="both", expand=True)
    restart_button.pack_forget()

    update_game()


def setup_game():
    global number_of_guesses, word_list, word_length, guesses_left, guessed_letters_list, word_display

    word_list = words.words()

    word_length = random.randint(3, 12)

    word_list = list(set([word.lower() for word in word_list if len(word) == word_length]))

    guesses_left = number_of_guesses

    guessed_letters_list = []
    word_display = ['_'] * word_length

    result_label.configure(text="", text_color="black")
    definition_label.configure(text="", text_color="black")
    guess_entry.delete(0, 'end')
    guess_entry.configure(state="normal")
    guess_entry.bind("<Return>", lambda event: submit_guess())
    guess_button.configure(state="normal")
    restart_button.pack_forget()
    update_game()


def update_game():
    word_label.configure(text=" ".join(word_display))
    guessed_label.configure(text="Guessed letters: " + ", ".join(guessed_letters_list))
    attempts_label.configure(text="Guesses left: " + str(guesses_left))


def submit_guess():
    global word_list, guesses_left, guessed_letters_list, definition

    letter_guessed = guess_entry.get().lower()

    if len(letter_guessed) != 1 or not letter_guessed.isalpha():
        return

    if letter_guessed in guessed_letters_list:
        result_label.configure(text="You've already guessed \"" + letter_guessed + ".\"", text_color="red")
        return

    guessed_letters_list.append(letter_guessed)

    new_word_list = []
    for word in word_list:
        has_letter = False
        for letter in word:
            if letter == letter_guessed:
                has_letter = True
        if not has_letter:
            new_word_list.append(word)

    if len(new_word_list) == 0:
        letter_positions = [tuple(i for i, letter in enumerate(word) if letter == letter_guessed) for word in word_list]
        position_counts = Counter(tuple(sorted(pos)) for pos in letter_positions)
        most_common_combinations = position_counts.most_common()
        max_count = most_common_combinations[0][1]
        tied_combinations = [combination for combination, count in most_common_combinations if count == max_count]
        most_common_combination = random.choice(tied_combinations)
        word_list = [word for word in word_list if tuple(i for i, letter in enumerate(word) if letter == letter_guessed) == most_common_combination]

        for index in most_common_combination:
            word_display[index] = letter_guessed
        result_label.configure(text="Good job! \"" + letter_guessed + "\" is in the word!", text_color="green")
    else:
        word_list = new_word_list
        guesses_left -= 1
        result_label.configure(text="Womp womp... \"" + letter_guessed + "\" isn't in the word.", text_color="red")

    update_game()

    guess_entry.delete(0, "end")


    def game_over():
        global definition
        try:
            definition = get_definition(answer)
        except:
            definition = "Definition not found"
        guess_entry.configure(state="disabled")
        guess_entry.unbind("<Return>")
        guess_button.configure(state="disabled")
        restart_button.pack(pady=10)


    if '_' not in word_display:
        result_label.configure(text="Congratulations! You guessed the word!", text_color="blue")
        game_over()
        definition_label.configure(text=definition, text_color="blue")
    elif guesses_left == 0:
        answer = random.choice(word_list)
        result_label.configure(text="Game over! The word was: " + answer + ".", text_color="red")
        game_over()
        definition_label.configure(text=definition, text_color="red")


def restrict_input(event):
    current_input = guess_entry.get()

    if event.keysym == "BackSpace":
        return

    if len(current_input) >= 1:
        return "break"
    if event.char.isalpha():
        guess_entry.delete(0, "end")
        guess_entry.insert(0, event.char.lower())
        return "break"

    if not event.char.isalpha():
        return "break"


def get_definition(word):
    global definition
    url = f"https://www.merriam-webster.com/dictionary/{word}"

    headers = {'User-Agent': 'Mozilla/5.0'}

    req = urllib.request.Request(url, headers=headers)
    resp = urllib.request.urlopen(req)
    resp_data = resp.read()

    return re.findall(r'data-share-description="(\D*?)\\xe2\\x80\\xa6', str(resp_data))[0]


root = ctk.CTk()
root.title("Hangman 2")
root.geometry("800x600")
root.resizable(False, False)

settings_frame = ctk.CTkFrame(root)
game_frame = ctk.CTkFrame(root)

header_label = ctk.CTkLabel(root, text="                                        HANGMAN 2                                        ", font=('Helvetica', 36, 'bold'), fg_color="#4CAF50", text_color="black", pady=16)
header_label.pack(fill="x")

novice_button = ctk.CTkButton(settings_frame, text="Novice - 10 guesses", font=('Helvetica', 32), command=lambda: select_difficulty("Novice"))
novice_button.pack(pady=16)
easy_button = ctk.CTkButton(settings_frame, text="Easy - 9 guesses", font=('Helvetica', 32), command=lambda: select_difficulty("Easy"))
easy_button.pack(pady=16)
medium_button = ctk.CTkButton(settings_frame, text="Medium - 8 guesses", font=('Helvetica', 32), command=lambda: select_difficulty("Medium"))
medium_button.pack(pady=16)
hard_button = ctk.CTkButton(settings_frame, text="Hard - 7 guesses", font=('Helvetica', 32), command=lambda: select_difficulty("Hard"))
hard_button.pack(pady=16)
hard_button = ctk.CTkButton(settings_frame, text="Impossible - 6 guesses", font=('Helvetica', 32), command=lambda: select_difficulty("Impossible"))
hard_button.pack(pady=16)

settings_label = ctk.CTkButton(game_frame, text="Settings", font=('Helvetica', 20), command=show_settings)
settings_label.pack(side="bottom", anchor="w", padx=10, pady=10)
word_label = ctk.CTkLabel(game_frame, text=" ".join(word_display), font=('Helvetica', 40, 'bold'), text_color="black")
word_label.pack(pady=20)
guessed_label = ctk.CTkLabel(game_frame, text="Guessed letters: ", font=('Helvetica', 20), text_color="black")
guessed_label.pack(pady=10)
attempts_label = ctk.CTkLabel(game_frame, text="Guesses left: " + str(guesses_left), font=('Helvetica', 20, "bold"), text_color="black")
attempts_label.pack(pady=10)
result_label = ctk.CTkLabel(game_frame, text="", font=('Helvetica', 24, "bold"), text_color="black")
result_label.pack(pady=10)
definition_label = ctk.CTkLabel(game_frame, text="", font=('Helvetica', 12, 'bold'), text_color="black", wraplength=600)
definition_label.pack(pady=10)
guess_entry = ctk.CTkEntry(game_frame, font=('Helvetica', 24), width=60, justify="center", text_color="black")
guess_entry.pack(pady=10)
guess_entry.bind("<KeyPress>", restrict_input)
guess_entry.bind("<Return>", lambda event: submit_guess())
guess_button = ctk.CTkButton(game_frame, text="Submit Guess", font=('Helvetica', 20, 'bold'), fg_color="#f4b400", text_color="black", command=submit_guess)
guess_button.pack(pady=20)
restart_button = ctk.CTkButton(game_frame, text="Restart Game", font=('Helvetica', 20, 'bold'), fg_color="#4CAF50", text_color="black", command=setup_game)

show_settings()

root.mainloop()
