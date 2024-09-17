from typing import List, Any


def prepare_empty_lists(num_of_list: int) -> List[List[Any]]:
    lists = []
    for i in range(num_of_list):
        lists.append([])
    return lists
