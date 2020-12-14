from .count import Count
from .distinctcount import DistinctCount
from .values import Values


names = {
    'count': Count,
    # ---
    'dc': DistinctCount,
    'distinctcount': DistinctCount,
    # ---
    'values': Values
}
