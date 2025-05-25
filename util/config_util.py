# /util/config_util.py

import os

def is_test_mode():
    """현재 테스트 모드 상태를 반환합니다."""
    return os.getenv("TEST_MODE", "False").lower() == "true"

def setup_test_mode(test_mode: bool = False):
    """테스트 모드를 활성화 또는 비활성화합니다."""
    os.environ["TEST_MODE"] = str(test_mode)