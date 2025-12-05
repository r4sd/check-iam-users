"""差分ロジックのテスト"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from check_users import diff_users


class TestDiffUsers:
    """diff_users 関数のテストケース"""

    def test_no_diff(self):
        """差分なし: 両方のセットが同一"""
        baseline = {"user1", "user2", "user3"}
        aws_users = {"user1", "user2", "user3"}

        added, missing = diff_users(baseline, aws_users)

        assert added == set()
        assert missing == set()

    def test_users_added(self):
        """追加検出: AWS にいるがベースラインにない"""
        baseline = {"user1", "user2"}
        aws_users = {"user1", "user2", "user3", "user4"}

        added, missing = diff_users(baseline, aws_users)

        assert added == {"user3", "user4"}
        assert missing == set()

    def test_users_missing(self):
        """削除検出: ベースラインにあるが AWS にいない"""
        baseline = {"user1", "user2", "user3"}
        aws_users = {"user1"}

        added, missing = diff_users(baseline, aws_users)

        assert added == set()
        assert missing == {"user2", "user3"}

    def test_both_added_and_missing(self):
        """追加と削除の両方を検出"""
        baseline = {"user1", "user2", "user3"}
        aws_users = {"user2", "user4", "user5"}

        added, missing = diff_users(baseline, aws_users)

        assert added == {"user4", "user5"}
        assert missing == {"user1", "user3"}

    def test_empty_baseline(self):
        """ベースラインが空: 全 AWS ユーザーが追加扱い"""
        baseline = set()
        aws_users = {"user1", "user2"}

        added, missing = diff_users(baseline, aws_users)

        assert added == {"user1", "user2"}
        assert missing == set()

    def test_empty_aws(self):
        """AWS が空: 全ベースラインユーザーが削除扱い"""
        baseline = {"user1", "user2"}
        aws_users = set()

        added, missing = diff_users(baseline, aws_users)

        assert added == set()
        assert missing == {"user1", "user2"}

    def test_both_empty(self):
        """両方とも空"""
        baseline = set()
        aws_users = set()

        added, missing = diff_users(baseline, aws_users)

        assert added == set()
        assert missing == set()
