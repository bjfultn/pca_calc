
import logging

import pandas as pd

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s (%(threadName)-2s) %(message)s', )
from .settings import DEBUG

if DEBUG:
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s (%(threadName)-2s) %(message)s', )

pd.set_option('mode.chained_assignment', None)
