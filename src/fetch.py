import requests
from json import JSONDecodeError
import re
from typing import Callable, Optional, Any, List, Dict

from backoff import on_exception, expo
from ratelimit import RateLimitDecorator, sleep_and_retry

from mytypes import MTGCard


moxfield_rate_limit = RateLimitDecorator(calls=20, period=1)


"""
DECORATORS
"""


def handle_final_exception(fail_response: Optional[Any]) -> Callable:
    """
    Decorator to handle any exception and return appropriate failure value.
    @param fail_response: Return value if Exception occurs.
    @return: Return value of the function, or fail_response.
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            # Final exception catch
            try:
                return func(*args, **kwargs)
            except (requests.RequestException, JSONDecodeError):
                # All requests failed
                return fail_response

        return wrapper

    return decorator


def handle_moxfield_request(fail_response: Optional[Any] = None) -> Callable:
    """
    Decorator to handle all Moxfield request failure cases, and return appropriate failure value.
    @param fail_response: The value to return if request failed entirely.
    @return: Requested data if successful, fail_response if not.
    """

    def decorator(func):
        @sleep_and_retry
        @moxfield_rate_limit
        @on_exception(expo, requests.RequestException, max_tries=2, max_time=0.75)
        @handle_final_exception(fail_response)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return decorator


"""
MOXFIELD REQUESTS
"""

@handle_moxfield_request({})
def get_data_url(url: str, params: Optional[Dict[str, str]] = None) -> Dict:
    """
    Get JSON data from any valid API URL.
    @param url: Valid API URL, such as Moxfield.
    @param params: Params to pass to an API endpoint.
    @return: JSON data returned.
    """
    with requests.get(url, params=(params or {})) as response:
        if response.status_code == 200:
            return response.json() or {}
        return {}


"""
UTILITY FUNCTIONS
"""


def get_cards_from_moxfield_decklist(url: str) -> List[MTGCard]:
    """
    Extract the card info from a single Moxfield decklist.
    @param url: Either the API endpoint or full URL.
    """
    cards: List[MTGCard] = list()

    res_json = get_data_url(url) or {}

    main_raw = res_json.get('mainboard', None)

    # If the mainboard is empty, skip this decklist as something went wrong
    if not isinstance(main_raw, dict):
        return []

    for key, raw_card in main_raw.items():
        # Just don't bother counting Double Faced cards. The data is incomplete
        if not raw_card.get('card', {}).get('card_faces', []):
            card = MTGCard(
                name=raw_card.get('card', {}).get('name'),
                quantity=raw_card.get('quantity', 1),
            )

            cards.append(card)

    return cards


def get_all_moxfield_decklist_cards(data: List[dict]) -> List[dict]:
    """
    Lookup Card data for every decklist on Moxfield.
    @note: https://api.moxfield.com/v2/decks/all/{deck_id}
    @return: The same JSON array with an added 'cards' item
    """

    for index, deckprofile in enumerate(data):
        decklist = deckprofile.get('decklist')

        # Extract the deck_id from a valid Moxfield decklist URL
        deck_id_match = re.search(r'moxfield\.com\/decks\/(.{22})$', decklist)

        if deck_id_match is None:
            continue

        deck_id = deck_id_match.group(1)

        cards = get_cards_from_moxfield_decklist(f"https://api.moxfield.com/v2/decks/all/{deck_id}")

        data[index]['cards'] = cards
    
    return data
