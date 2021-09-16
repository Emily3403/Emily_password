#!/usr/bin/env python3.10

from emily_password.frontend.interaction import *
# TODO:
#   Lieber Alias statt filename → append if not in


# TODO:
#   Make a daemon that kills the process if not poked in ~5min. Ensures pw's get freed - does it?

# TODO: Platform testing?

# TODO:
#   Show password → Best matches etc.

# TODO:
#   For seeing a password → enter password


def entry_main():
    mainloop()


if __name__ == '__main__':
    entry_main()
