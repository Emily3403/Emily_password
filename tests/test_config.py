import pytest

import emily_password.share.utils as utils


@pytest.mark.dependency(
    depends=["tests/test__dependencies.py::test_correct_dir"],
    scope='session'
)
def test_generate_default_config():
    assert utils.installed_as_editable_mode() is not None


