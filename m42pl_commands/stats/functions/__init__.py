from .count import Count
from .values import Values
from .minmax import Min, Max
from .firstlast import First, Last


# Stats functions (aka. functors) mapping
# The following dict maps the functors names with their classes.
names = {
    'count': Count,
    'values': Values,
    'min': Min,
    'max': Max,
    'first': First,
    'last': Last
}
