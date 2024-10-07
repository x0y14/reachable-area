from typing import List, Any


def prepare_empty_lists(num_of_list: int) -> List[List[Any]]:
    lists = []
    for i in range(num_of_list):
        lists.append([])
    return lists


def list_include(a: list[str], b: list[str]) -> bool:
    for a_content in a:
        if a_content in b:
            return True
    return False
