import pytest

import emily_password.share.utils as utils
from emily_password.share.constants import *

@pytest.mark.dependency()
def test_correct_dir():
    assert utils.path() != password_dir

