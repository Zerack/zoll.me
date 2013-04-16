'''
James D. Zoll

3/18/2013

Purpose: Defines constants for the My Year In Temperatures scarf application.

License: This is a public work.

'''

# Constant limits on what can be entered.
DATA_START_YEAR = 1995
MAX_COLORS = 15
MIN_COLORS = 2
MAX_TEMPERATURE = 150.0
MIN_TEMPERATURE = -50.0

# Defaults for when nothing is supplied by the user.
DEFAULT_NUM_COLORS = 6
DEFAULT_COLOR_INTERVAL = 10
DEFAULT_COLDEST_TEMP = 30

# Values affecting random color generation and color darkening.
COLOR_DARKEN_FACTOR = 0.2
GOLDEN_RATIO_CONJUGATE = 0.618033988749895
HSV_S = 0.5
HSV_V = 0.95
TCC_WHITE = 'text-color-white'
TCC_BLACK = 'text-color-black'

# Template paths
TEMPLATE_INDEX = 'scarf/index.html'
TEMPLATE_RESULTS = 'scarf/results.html'

# Cookie for counting checked rows.
CHECKED_ROW_COUNT_COOKIE = 'checked_row_count'