from .count import Count
from.distinctcount import DistinctCount
from .values import Values
from ._list import List
from .minmax import Min, Max
from .firstlast import First, Last

from .aggregates import Aggregates


# Stats functions (aka. functors) mapping
# The following dict maps the functors names with their classes.
names = {
    'count': Count,
    'dc': DistinctCount,
    'distinctcount': DistinctCount,
    'values': Values,
    'list': List,
    'min': Min,
    'max': Max,
    'first': First,
    'last': Last,
    # ---
    'aggregates': Aggregates
}
