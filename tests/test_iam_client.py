"""moto を使った IAM クライアント機能のテスト"""

import sys
from pathlib import Path

import boto3
from moto import mock_aws

sys.path.insert(0, str(Path(__file__).parent.parent))

from check_users import get_iam_users


@mock_aws
class TestGetIamUsers:
    """get_iam_users 関数のテストケース"""

    def test_empty_users(self):
        """IAM ユーザーが存在しない場合"""
        # moto がモック AWS 環境を作成する
        users = get_iam_users()
        assert users == set()

    def test_single_user(self):
        """IAM ユーザーが 1 人の場合"""
        iam = boto3.client("iam", region_name="us-east-1")
        iam.create_user(UserName="test-user")

        users = get_iam_users()

        assert users == {"test-user"}

    def test_multiple_users(self):
        """IAM ユーザーが複数の場合"""
        iam = boto3.client("iam", region_name="us-east-1")
        iam.create_user(UserName="user1")
        iam.create_user(UserName="user2")
        iam.create_user(UserName="user3")

        users = get_iam_users()

        assert users == {"user1", "user2", "user3"}

    def test_pagination(self):
        """ページネーションが正しく動作するかテスト（大量ユーザー）"""
        iam = boto3.client("iam", region_name="us-east-1")

        # ページネーションをトリガーするために十分なユーザーを作成（デフォルトは100件）
        expected_users = set()
        for i in range(150):
            username = f"user{i:03d}"
            iam.create_user(UserName=username)
            expected_users.add(username)

        users = get_iam_users()

        assert users == expected_users
        assert len(users) == 150
