from typing import List


def get_total_stats(deckprofiles: List[dict]) -> (int, int, int, int, float):
    """
    """

    total_wins = sum([deck.get('wins') for deck in deckprofiles])
    total_not_wins = sum([deck.get('draws') + deck.get('losses') for deck in deckprofiles])
    total_games = total_wins + total_not_wins
    total_decks = sum([1 if deck.get('cards') else 0 for deck in deckprofiles])
    total_win_percentage = round((total_wins / total_games) * 100, 2)

    return total_wins, total_not_wins, total_games, total_decks, total_win_percentage


def count_card_stats(deckprofiles: List[dict]) -> dict:
    """
    Go through the deckprofiles array and return a dict of type 
    {
        'card_name': {
            'wins': int, 
            'draws': int, 
            'losses': int, 
            'total_games': int, 
            'total_decks': int
        }
    }
    """

    card_stats = {}

    for deck in deckprofiles:
        if deck.get('cards'):
            for card in deck.get('cards'):
                wins = (card_stats.get(card.get('name'), {}).get('wins') or 0) + deck.get('wins')
                draws = (card_stats.get(card.get('name'), {}).get('draws') or 0) + deck.get('draws')
                losses = (card_stats.get(card.get('name'), {}).get('losses') or 0) + deck.get('losses')
                total_games = wins + draws + losses
                total_decks = (card_stats.get(card.get('name'), {}).get('total_decks') or 0) + 1

                card_stats[card.get('name')] = {
                    'wins': wins,
                    'draws': draws,
                    'losses': losses,
                    'total_games': total_games,
                    'total_decks': total_decks,
                }

    return card_stats
