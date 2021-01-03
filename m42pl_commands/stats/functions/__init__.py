from .count import Count
from .distinctcount import DistinctCount
from .values import Values


# Stats functions (aka. functors) mapping
# The following dict map a functor name with its class.
names = {
    'count': Count,
    'values': Values
}
