#!/usr/bin/env python3.10

try:
    from .constants import *
    from .utils import *
    from .config import *
    from .crypt import *

except ImportError:
    from constants import *
    from utils import *
    from config import *
    from crypt import *

the_demo_password = ""

# TODO: Make this better
demo_passwords = [
    Password(title="Email", password="Ein_Apfel", email="AxelLalemann@gmail.com", username="K", website="Y", secret=False),
    Password(title="Youtube", password="Ein_Apfel", email="AxelLalemann@gmail.com", username="!", website="https://www.youtube.com/", secret=False),
    Password(title="EE", password="AA", email="XX", username="FFF", website="H", secret=False),

]




def create_demo_files():
    config.set_demo(True)

    generate_salt()
    encryptor(the_demo_password, demo_passwords)


    config.restore_demo()


if __name__ == '__main__':
    # Generate the demo configuration
    create_demo_files()
