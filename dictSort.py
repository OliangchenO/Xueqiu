from collections import namedtuple;

item = namedtuple('item', 'key value')

def sortByValue(dict):
    """Sorts a dictionary into a list of named tuples
       :param dict: dictionary to sort
       :returns: list of namedtuples"""
    sortedList = []
    for key in dict:
        sortedList.append(item(key, dict[key]))

    sortedList = sorted(sortedList, key=lambda item: item.value);
    
    return sortedList;