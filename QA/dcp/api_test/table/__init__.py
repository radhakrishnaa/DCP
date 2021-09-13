import pytest


needs_publish = pytest.mark.skipif(
    pytest.config.getoption('--no-publish'),
    reason="won't run with --no-publish option")
