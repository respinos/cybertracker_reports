def group(iterable, num):
    """Group an iterable into an n-tuples iterable. Incomplete tuples
    are discarded e.g.
    
    >>> list(group(range(10), 3))
    [(0, 1, 2), (3, 4, 5), (6, 7, 8), (9, None, None)]
    """
    return map(None, *[iter(iterable)] * num)
    
from math import ceil

def paginate(items, page=0, max_per_page=10):
    """Simple generic pagination.

    Given an iterable, this function returns:
     * the slice of objects on the requested page,
     * the total number of items, and
     * the total number of pages.

    The `items` parameter can be a list, tuple, or iterator:

    >>> items = range(12)
    >>> items
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    >>> paginate(items)
    ([0, 1, 2, 3, 4, 5, 6, 7, 8, 9], 12, 2)
    >>> paginate(items, page=1)
    ([10, 11], 12, 2)
    >>> paginate(iter(items))
    ([0, 1, 2, 3, 4, 5, 6, 7, 8, 9], 12, 2)
    >>> paginate(iter(items), page=1)
    ([10, 11], 12, 2)

    This function also works with generators:

    >>> def generate():
    ...     for idx in range(12):
    ...         yield idx
    >>> paginate(generate())
    ([0, 1, 2, 3, 4, 5, 6, 7, 8, 9], 12, 2)
    >>> paginate(generate(), page=1)
    ([10, 11], 12, 2)

    The `max_per_page` parameter can be used to set the number of items that
    should be displayed per page:

    >>> items = range(12)
    >>> paginate(items, page=0, max_per_page=6)
    ([0, 1, 2, 3, 4, 5], 12, 2)
    >>> paginate(items, page=1, max_per_page=6)
    ([6, 7, 8, 9, 10, 11], 12, 2)
    """
    if not page:
        page = 0
    start = page * max_per_page
    stop = start + max_per_page

    count = None

    try:
        count = items.count()
    except:
        count = len(items)

    try: # Try slicing first for better performance
        retval = items[start:stop]
    except TypeError: # Slicing not supported, so iterate through the whole list
        retval = []
        for idx, item in enumerate(items):
            if start <= idx < stop:
                retval.append(item)
            # If we already obtained the total number of items via `len()`,
            # we can break out of the loop as soon as we've got the last item
            # for the requested page
            if count is not None and idx >= stop:
                break
        if count is None:
            count = idx + 1

    return retval, count, int(ceil(float(count) / max_per_page))

