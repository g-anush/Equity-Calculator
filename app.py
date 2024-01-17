from flask import Flask, request, jsonify
import pandas as pd
import random
import os

app = Flask(__name__)

def load_dataframes():
    # Implement logic to load dataframes from CSV files in the "boards" folder
    dataframes = {}
    # Example: Iterate over CSV files and load dataframes
    # for filename in os.listdir("boards"):
    #     if filename.endswith(".csv"):
    #         board_name = filename.split(".")[0]
    #         dataframes[board_name] = pd.read_csv(os.path.join("boards", filename))

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
    # Implement logic to generate possible boards
    # Remove used and dead cards from a superset of 52 cards
    # For simplicity, consider only the remaining undealt cards
    all_cards = [str(rank) + suit for rank in "23456789TJQKA" for suit in "CDHS"]
    remaining_cards = [card for card in all_cards if card not in selected_hand + deadcards]
    possible_boards = [random.sample(remaining_cards, 5) for _ in range(10)]  # Generate 10 possible boards
    return possible_boards

def generate_hand_combos(selected_hand, selected_board):
    # Implement logic to generate 2 card combos for each hand
    hand_combos = []
    for card1 in selected_hand:
        for card2 in selected_hand:
            if card1 != card2:
                hand_combos.append(sorted([card1, card2] + selected_board))
    return hand_combos

def get_winning_hand(hand_combos, dataframe):
    # Implement logic to find the winning hand based on the dataframe
    # For simplicity, consider the first winning hand found in the dataframe
    for combo in hand_combos:
        if not dataframe[dataframe.apply(tuple, axis=1).isin([tuple(combo)])].empty:
            return combo

    # If no winning hand is found, return None
    return None

@app.route('/equity6card', methods=['POST'])
def equity6card():
    try:
        request_data = request.get_json()

        holecards = request_data.get("holecards")
        deadcards = request_data.get("deadcards")
        num_trials = request_data.get("num_trials")

        if not holecards or not deadcards or not num_trials:
            return jsonify({"error": "Missing required input parameters"}), 400

        dataframes = load_dataframes()
        equities, result = calculate_equity(holecards, deadcards, num_trials, dataframes)

        response_data = {
            "equities": equities,
            "result": result
        }

        return jsonify(response_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    dataframes = load_dataframes()
    app.run(debug=True)
