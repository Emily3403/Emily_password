#!/usr/bin/env python3.10
import json
import os
import string
import sys
import base64

from emily_password.share.constants import *
from emily_password.share.utils import *


my_name = "emily_password"

config_name_mapping = {
    "encrypted_file_name": "Encrypted File Name",
    "salt_file_name": "Salt File Name",
    "temp_file_name": "Temporary File Name",

    "is_demo": "Toggle Demo Mode",
    "demo_prefix": "Demo Prefix",
    "password_contents": "Password Content",
    "password_length": "Password Length",
    "show_password_num_initial": "Number of Passwords to show",

    "exit": "Exit button",
    "website": "Enter the Website",
    "username": "Enter the Username",
    "email": "Enter the E-Mail",
    "password": "Enter the Password",
}


class Config:
    __config = {}
    __file_contents = {}
    __password = None

    def __init__(self, content: Dict[str, str] = None, password: str = None):
        if password is not None:
            Config.__password = password

        # Prevent multiple file reads
        if Config.__config and Config.__file_contents:
            return
        content = content or {}

        try:
            with open(path(config_file_name)) as f:
                Config.__config.update(json.load(f))
        except FileNotFoundError:
            print("I could not find the config.json file. Please regenerate it!")

        # Config.__config |= content

        def load_file_into_config(name, mode="r", is_demo=False):

            try:
                with open(path(Config.__config["demo_prefix"] * is_demo + Config.__config[name + "_file_name"]), mode) as f:
                    # TODO: Why??
                    # the_name = f.read()
                    # try:
                    #     the_name = the_name.decode()
                    # except ValueError:
                    #     pass
                    Config.__file_contents |= {"demo_" * is_demo + name: f.read()}
            except FileNotFoundError:
                # Config.__file_contents |= {"demo_" * is_demo + name: ""}
                pass
        load_file_into_config("encrypted", "rb")
        load_file_into_config("salt", "rb")

        load_file_into_config("encrypted", "rb", is_demo=True)
        load_file_into_config("salt", "rb", is_demo=True)

        Config.__config |= {"backup_demo": Config.__config["is_demo"]}

    @classmethod
    def from_file(cls):
        with open(path(config_file_name)) as f:
            return cls(json.load(f))

    def save(self):
        with open(path(config_file_name), "w+") as f:
            f.write(self.to_json())

    @staticmethod
    def password():
        return Config.__password

    @staticmethod
    def encrypted_file_contents():
        return Config.__file_contents[Config.demo() * "demo_" + "encrypted"]

    @staticmethod
    def legacy_file_contents():
        return Config.__file_contents["legacy"]

    @staticmethod
    def salt():
        return Config.__file_contents["salt"]

    @staticmethod
    def demo():
        return Config.__config["is_demo"]

    @staticmethod
    def set_demo(value: bool):
        Config.__config["backup_demo"] = Config.__config["is_demo"]
        Config.__config["is_demo"] = value

    @staticmethod
    def restore_demo():
        Config.__config["is_demo"] =Config.__config["backup_demo"]

    @staticmethod
    def encrypted_file():
        return Config.demo() * Config.__config["demo_prefix"] + Config.__config["encrypted_file_name"]


    @staticmethod
    def legacy_file():
        return Config.__config["legacy_file_name"]

    @staticmethod
    def salt_file():
        return Config.__config["salt_file_name"]


    def __getitem__(self, item):
        return Config.__config[item]

    @staticmethod
    def __setitem__(key, value):
        Config.__config[key] = value

    def __delitem__(self, key):
        del Config.__config[key]

    def __len__(self):
        return len(Config.__config)

    def __iter__(self):
        return iter(Config.__config)

    def to_json(self):
        return json.dumps(Config.__config, indent=4)


def generate_default_config():
    default_config = {
        "encrypted_file_name": "PasswordsEncrypted.txt",
        "salt_file_name": "PasswordsSalt.txt",
        "temp_file_name": "PasswordsTemp.txt",

        "is_demo": True,
        "demo_prefix": "Demo",

        "password_contents": string.printable[:94],  # A string of characters → i.e. "abc123"
        "password_length": 63,
        "show_password_num_initial": 13,

        "password_input_mapping": {
            "exit": "esc",
            "website": "end",
            "username": "home",
            "email": "page_down",
            "password": "delete",
        }
    }

    config = Config(default_config)
    config.save()


def make_files_from_config():
    # TODO
    config = Config()

    # if not os.path.exists((filename := path(config["salt_file"]))):
    #     with open(filename, "wb+") as f:
    #         f.write(os.urandom(salt_length))


def setup_config():
    ensure_directories()
    generate_default_config()
    make_files_from_config()


if __name__ == '__main__':
    setup_config()

# try:
#     config
# except NameError:
#     config = Config()
