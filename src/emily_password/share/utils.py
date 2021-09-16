import argparse
import datetime
import difflib
import zipfile
import json
import random
import sys
from dataclasses import dataclass

from functools import lru_cache
from pathlib import Path

from typing import List, Dict

from emily_password.share.constants import *


def path(*args):
    install_dir = get_install_dir()

    if install_dir:
        return os.path.join(install_dir, alternate_password_dir, *args)
    else:
        return os.path.join(password_dir, *args)


def get_args():
    parser = argparse.ArgumentParser(prog="./main.py", formatter_class=argparse.RawTextHelpFormatter, description="""
        Password manager""")
    parser.add_argument("-v", "--verbose", help="Increases output verbosity.", action="store_true")
    parser.add_argument("-V", "--version", help="Increases output verbosity.", action='version', version='%(prog)s 2.0')
    parser.add_argument("-l", "--legacy", help="Enables legacy compatibility mode.", action="store_true")

    args = parser.parse_args()
    return args


def ensure_directories():
    os.makedirs(path(), exist_ok=True)


@dataclass
class Password:
    id: int = None
    title: str = ""
    password: str = ""
    email: str = ""
    username: str = ""
    website: str = ""
    secret: bool = False

    # TODO: Two factor
    def __post_init__(self):
        if self.id is None:
            self.id = random.randint(password_id_lower, password_id_upper)

    def __str__(self) -> str:
        return f"{self.title}: {self.password}"

    def dump(self) -> str:
        return json.dumps(self.__dict__, indent=4)

    def display_attrs(self):
        return self.__dict__.items()

    def set_attribute(self, attr, value):
        # TODO: History, Saving
        pre_change = self.__dict__.copy()
        setattr(self, attr, value)
        post_change = self.__dict__.copy()
        history.append(HistoryElement(self.title, pre_change, post_change))

    def get_attribute(self, attr):
        try:
            return self.__dict__[attr]
        except KeyError:
            return self.__dict__[attr.lower()]

    @staticmethod
    def dump_list(content: list) -> str:
        return "[\n" + ",\n".join(item.dump() for item in content) + "\n]"

    @staticmethod
    def list_from_string(content: str) -> list:
        return [Password(**item) for item in json.loads(content)]

    @staticmethod
    def select_matching_items_from_list(passwords: list, columns: list, active_search_column):
        final = []
        for item in passwords:
            for col in columns:
                if col.search_text.casefold() not in col.select_pw_attr(item).casefold():
                    break
            else:
                final.append(item)

        return sorted(final, key=lambda x: difflib.SequenceMatcher(
            None, active_search_column.select_pw_attr(x).casefold(), active_search_column.search_text.casefold()).ratio(), reverse=True)

    @staticmethod
    def set_columns_from_list(passwords: list, columns: list, content: list):
        for i, row in enumerate(content):
            for j, item in enumerate(row):
                item.set_text("")

        for i, item in enumerate(columns):
            for j, pw in enumerate(passwords):
                content[j][i].set_text(item.select_pw_attr(pw))

    def display(self) -> dict:
        return self.__dict__


class HistoryElement:
    def __init__(self, title: str, old: Dict[str, str] = None, new: Dict[str, str] = None, time: datetime.datetime = None):
        self.title = title
        self.old = old
        self.new = new
        self.time = time or datetime.datetime.now()

        changed_keys = {item[0] for item in set(self.old.items()) ^ set(self.new.items())}
        self.diff = {item: (old.get(item, None), new.get(item, None)) for item in changed_keys}

    def dump(self):
        return json.dumps([self.title, datetime.datetime.now().isoformat(), self.diff])


class History:
    def __init__(self, items: List[HistoryElement] = None):
        self._container = {}
        self.extend(items)

    def append(self, other: HistoryElement):
        if not other.diff:
            return

        self._ensure_present(other.title)
        self._container[other.title].append(other)

    def _ensure_present(self, title):
        if title not in self._container:
            self._container.update({title: []})

    def extend(self, other: List[HistoryElement]):
        if other is None:
            return

        for item in other:
            self.append(item)

    def dump(self):
        to_dump = {row: [item.dump() for item in self._container[row]] for row in self._container}
        return json.dumps(to_dump, indent=4)


possible_paths = [item for item in sys.path if "site-packages" in item]

@lru_cache()  # Cache in order not to search the entire directory every time
def installed_as_editable_mode():
    for path_item in possible_paths:
        egg_link = os.path.join(path_item, pip_name + '.egg-link')
        if os.path.isfile(egg_link):
            return True

    return False

@lru_cache()
def get_install_dir():
    package_name = pip_name + '.egg-link' if installed_as_editable_mode() else pip_name.replace("-", "_")
    for path_item in possible_paths:
        file = Path(path_item, package_name)

        if file.exists():
            if file.is_dir():
                return file.as_posix()

            with file.open() as f:
                return f.readline().strip()





if __name__ == '__main__':
    x = HistoryElement("abc", {"a": "b", "c": "d", "1": "1", "3": "3"}, {"a": "c", "c": "e", "1": "1", "2": "1"})
    history.append(x)
