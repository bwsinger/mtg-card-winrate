import json
import questionary
from pathlib import Path
from typing import List
from src.constants import DATA_FILE_PATHS, STORAGE_PATH
from src.fetch import get_all_moxfield_decklist_cards
from src.stats import get_total_stats, count_card_stats

if __name__ == "__main__":
    
    # Prompt user to select from a list of deck data from the /data folder
    # NOTE: Data comes from edhtop16.com/api/req API
    path_dict = {str(path.stem): path for path in DATA_FILE_PATHS}

    filename = questionary.select(
        "Which data set do you want to analyze?",
        choices=path_dict,
    ).ask()

    storage_file_name = f'{filename}-storage.json'

    # Read win/loss and decklist data into memory
    deckprofiles: List[dict] = []

    if STORAGE_PATH.joinpath(storage_file_name).exists():
        # Grab the stored data that was previously fetched
        with open(STORAGE_PATH.joinpath(storage_file_name)) as data_file:
            deckprofiles = json.load(data_file)
    else:
        data_raw: List[dict] = None

        with open(path_dict.get(filename)) as data_file:
            data_raw = json.load(data_file)

        # Add the cards to the results and write to file for faster retrieval
        deckprofiles = get_all_moxfield_decklist_cards(data_raw)

        with open(STORAGE_PATH.joinpath(storage_file_name), 'w', encoding='utf-8') as f:
            json.dump(deckprofiles, f, sort_keys = True, ensure_ascii=False, indent=4)

    # Get metrics
    total_wins, total_not_wins, total_games, total_decks, total_win_percentage = get_total_stats(deckprofiles)

    print(f'total_wins:              {total_wins}')
    print(f'total_not_wins:          {total_not_wins}')
    print(f'total_games:             {total_games}')
    print(f'total_decks:             {total_decks}')
    print(f'total_win_percentage:    {total_win_percentage}')


    # Get individual card stats
    card_stats = count_card_stats(deckprofiles=deckprofiles)

    for index, (card_name, card) in enumerate(card_stats.items()):
        print(f'{card_name:30s}: {card}')

        if index == 9:
            break

    #TODO: Add plotly for data visualization
