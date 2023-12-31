import json
import questionary
from pathlib import Path
from typing import List
from src.constants import DATA_PATH, DATA_FILE_PATHS, STORAGE_PATH, MIN_GAMES_PLAYED, CSV_PATH
from src.fetch import get_all_moxfield_decklist_cards
from src.stats import get_total_stats, count_card_stats

if __name__ == "__main__":

    # Create all directories
    Path(DATA_PATH).mkdir(exist_ok=True)
    STORAGE_PATH.mkdir(exist_ok=True)
    CSV_PATH.mkdir(exist_ok=True)
    
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
    totals = get_total_stats(deckprofiles)

    total_wins, total_not_wins, total_games, total_decks, total_win_percentage = totals

    # print(f'Total Wins:              {total_wins}')
    # print(f'Total Not Wins:          {total_not_wins}')
    # print(f'Total Games:             {total_games}')
    # print(f'Total Decks:             {total_decks}')
    # print(f'Total Win Percentage:    {total_win_percentage:.2%}')

    # # Get individual card stats
    # card_stats = count_card_stats(deckprofiles=deckprofiles, totals=totals)

    # print(f'Total Unique Cards:      {len(card_stats)}')

    print(f'Total Wins:,{total_wins}')
    print(f'Total Not Wins:,{total_not_wins}')
    print(f'Total Games:,{total_games}')
    print(f'Total Decks:,{total_decks}')
    print(f'Total Win Percentage:,{total_win_percentage:.2%}')

    # Get individual card stats
    card_stats = count_card_stats(deckprofiles=deckprofiles, totals=totals)

    print(f'Total Unique Cards:,{len(card_stats)}')

    print('\n')

    relevant_card_stats = {key: card for key, card in card_stats.items() if card.get('total_games') >= MIN_GAMES_PLAYED}

    best_cards_first = sorted(relevant_card_stats, key=lambda card: card_stats.get(card, {}).get('win_percentage_diff'), reverse=True)
    worst_cards_first = sorted(relevant_card_stats, key=lambda card: card_stats.get(card, {}).get('win_percentage_diff'))

    print(f'Best performing cards (with {MIN_GAMES_PLAYED} or more games played)')
    print('{: <31} {: <15} {: <20} {: <25}'.format('Card Name', 'Win Percentage', 'Win Percentage Diff', 'Games Played'))
    
    for index, card_name in enumerate(best_cards_first):
        card = card_stats[card_name]

        card_win_percentage = card.get('win_percentage')
        win_percentage_diff = card.get('win_percentage_diff')
        games_played = card.get('total_games')

        print(f'{card_name:30s}:{card_win_percentage: >7.2%}{win_percentage_diff: >+17.2%}{games_played:17n}')

        if index == 19:
            break

    print('\n')

    print(f'Worst performing cards (with {MIN_GAMES_PLAYED} or more games played)')
    print('{: <31} {: <15} {: <20} {: <25}'.format('Card Name', 'Win Percentage', 'Win Percentage Diff', 'Games Played'))

    for index, card_name in enumerate(worst_cards_first):
        card = card_stats[card_name]

        card_win_percentage = card.get('win_percentage')
        win_percentage_diff = card.get('win_percentage_diff')
        games_played = card.get('total_games')

        print(f'{card_name:30s}:{card_win_percentage: >7.2%}{win_percentage_diff: >+17.2%}{games_played:17n}')

        if index == 19:
            break

    print('\n')

    # Make a spreadsheet of all the results
    import csv
    with open(CSV_PATH.joinpath(f'{filename}.csv'), 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        csvwriter.writerow(['Card Name', 'Win Percentage', 'Win Percentage Diff', 'Games Played'])
        
        csv_card_list = list()

        for card_name in best_cards_first:
            card = card_stats[card_name]

            csv_card_list.append([card_name, f"{card.get('win_percentage'):.2%}", f"{card.get('win_percentage_diff'):+.2%}", f"{card.get('total_games')}"])

        csvwriter.writerows(csv_card_list)

    #TODO: Add plotly for data visualization
