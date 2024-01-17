from flask import Flask, render_template, request, jsonify
import random
import pandas as pd
import os

app = Flask(__name__)

def load_dataframes():
    dataframes = {}
    for filename in os.listdir("boards"):
        if filename.endswith(".csv"):
            board_name = filename.split(".")[0]
            dataframes[board_name] = pd.read_csv(os.path.join("boards", filename))
    return dataframes

def calculate_equity(holecards, deadcards, num_trials, dataframes):
    equities = []
    win_count = [0] * len(holecards)

    for _ in range(num_trials):
        for i, hand_range in enumerate(holecards):
            selected_hand = random.choice(hand_range)
            possible_boards = generate_possible_boards(selected_hand, deadcards)
            selected_board = random.choice(possible_boards)
            hand_combos = generate_hand_combos(selected_hand, selected_board)
            winning_hand = get_winning_hand(hand_combos, dataframes[selected_board])
            if winning_hand == selected_hand:
                win_count[i] += 1

    total_trials = num_trials * len(holecards)
    equities = [(count / total_trials) * 100 for count in win_count]
    loss_count = total_trials - sum(win_count)
    tie_count = 0  # You mentioned ties, but the logic for ties is not specified

    result = {
        "win": sum(win_count),
        "loss": loss_count,
        "tie": tie_count
    }

    return equities, result

def generate_possible_boards(selected_hand, deadcards):
    all_cards = [str(rank) + suit for rank in "23456789TJQKA" for suit in "CDHS"]
    remaining_cards = [card for card in all_cards if card not in selected_hand + deadcards]
    possible_boards = [random.sample(remaining_cards, 5) for _ in range(10)]
    return possible_boards

def generate_hand_combos(selected_hand, selected_board):
    hand_combos = []
    for card1 in selected_hand:
        for card2 in selected_hand:
            if card1 != card2:
                hand_combos.append(sorted([card1, card2] + selected_board))
    return hand_combos

def get_winning_hand(hand_combos, dataframe):
    for combo in hand_combos:
        if not dataframe[dataframe.apply(tuple, axis=1).isin([tuple(combo)])].empty:
            return combo
    return None

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/equity6card', methods=['POST'])
def equity6card():
    try:
        holecards_input = request.form['holecards']
        deadcards_input = request.form['deadcards']
        num_trials_input = int(request.form['num_trials'])

        holecards = [hand.split(',') for hand in holecards_input.split(';')]
        dataframes = load_dataframes()
        equities, result = calculate_equity(holecards, deadcards_input, num_trials_input, dataframes)

        return render_template('result.html', equities=equities, result=result)

    except Exception as e:
        return render_template('error.html', error=str(e))

if __name__ == '__main__':
    app.run(debug=True)
