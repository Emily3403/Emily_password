import os
from cryptography.hazmat.primitives import hashes

password_dir = os.path.expanduser("~/.password")
alternate_password_dir = ".password/"

config_file_name = "config.json"

password_hint = "Hints are for suckers!"
password_hint_num = 1


sleep_time = 0.01
timeout_time = 5 * 60

hash_iterations = 10 ** 1
hash_algorithm = hashes.SHA3_512()
hash_length = 32
salt_length = 64

try_no_password = True

password_id_lower = 0
password_id_upper = 1e10


check_terminal = False
num_min_cols = 10
num_min_lines = 10



pip_name = "emily-password"
