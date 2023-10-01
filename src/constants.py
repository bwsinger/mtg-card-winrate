from pathlib import Path
from typing import List

DATA_PATH = './data'
DATA_FILE_PATHS = sorted(Path(DATA_PATH).glob('*.json'))
STORAGE_PATH = Path('./storage')
