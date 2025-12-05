#!/usr/bin/env python3
"""IAM ユーザー差分チェックツール

ベースラインリストと AWS IAM ユーザーを比較して差分を検出する:
- Added: AWS にいるがベースラインにない（不正/野良アカウント検出）
- Missing: ベースラインにあるが AWS にいない（削除事故/作成漏れ検出）
"""

import argparse
import os
import sys

import boto3

# ファイルパス
BASELINE_FILE = "iam_users_baseline.txt"
ADDED_FILE = "iam_users_added.txt"
MISSING_FILE = "iam_users_missing.txt"


def get_iam_users(profile: str | None = None) -> set[str]:
    """AWS から IAM ユーザーを全件取得する（ページネーション対応）"""
    session = boto3.Session(profile_name=profile)
    iam = session.client("iam", region_name="us-east-1")

    users = set()
    paginator = iam.get_paginator("list_users")
    for page in paginator.paginate():
        for user in page["Users"]:
            users.add(user["UserName"])

    return users


def load_baseline() -> set[str]:
    """ベースラインファイルからユーザーを読み込む"""
    if not os.path.exists(BASELINE_FILE):
        return set()

    with open(BASELINE_FILE, encoding="utf-8") as f:
        return {line.strip() for line in f if line.strip()}


def save_baseline(users: set[str]) -> None:
    """ユーザーをベースラインファイルに保存する"""
    with open(BASELINE_FILE, "w", encoding="utf-8") as f:
        for user in sorted(users):
            f.write(user + "\n")


def save_diff(filename: str, users: set[str]) -> None:
    """差分結果をファイルに保存する"""
    with open(filename, "w", encoding="utf-8") as f:
        for user in sorted(users):
            f.write(user + "\n")


def diff_users(baseline: set[str], aws_users: set[str]) -> tuple[set[str], set[str]]:
    """ベースラインと AWS ユーザーの差分を計算する

    Returns:
        tuple: (added, missing)
        - added: AWS にいるがベースラインにない
        - missing: ベースラインにあるが AWS にいない
    """
    added = aws_users - baseline
    missing = baseline - aws_users
    return added, missing


def cmd_init(args: argparse.Namespace) -> int:
    """現在の AWS IAM ユーザーでベースラインを初期化する"""
    if os.path.exists(BASELINE_FILE) and not args.force:
        print(f"エラー: {BASELINE_FILE} は既に存在します")
        print("上書きするには --force を指定してください")
        return 1

    print("AWS から IAM ユーザーを取得中...")
    users = get_iam_users(args.profile)

    save_baseline(users)
    print(f"ベースライン作成完了: {len(users)} ユーザー")
    print(f"保存先: {BASELINE_FILE}")
    return 0


def cmd_update(args: argparse.Namespace) -> int:
    """現在の AWS IAM ユーザーでベースラインを更新する"""
    print("AWS から IAM ユーザーを取得中...")
    users = get_iam_users(args.profile)

    save_baseline(users)
    print(f"ベースライン更新完了: {len(users)} ユーザー")
    print(f"保存先: {BASELINE_FILE}")
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    """ベースラインと AWS IAM ユーザーの差分をチェックする"""
    baseline = load_baseline()
    if not baseline:
        print(f"エラー: {BASELINE_FILE} が見つからないか空です")
        print("まず --init でベースラインを作成してください")
        return 1

    print("AWS から IAM ユーザーを取得中...")
    aws_users = get_iam_users(args.profile)

    added, missing = diff_users(baseline, aws_users)

    # 結果を表示
    print("\n=== IAM Users Diff Check ===")
    print(f"Baseline: {len(baseline)} users")
    print(f"AWS:      {len(aws_users)} users")
    print()

    print(f"Added ({len(added)}):    # AWS にいるが baseline にない")
    if added:
        for user in sorted(added):
            print(f"  + {user}")
    else:
        print("  (none)")

    print()
    print(f"Missing ({len(missing)}):  # baseline にあるが AWS にいない")
    if missing:
        for user in sorted(missing):
            print(f"  - {user}")
    else:
        print("  (none)")

    # 結果を保存
    save_diff(ADDED_FILE, added)
    save_diff(MISSING_FILE, missing)

    print()
    print("結果を保存しました:")
    print(f"  - {ADDED_FILE}")
    print(f"  - {MISSING_FILE}")

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="IAM Users diff check tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --init --profile my-profile   # Create baseline
  %(prog)s --profile my-profile          # Check diff
  %(prog)s --update --profile my-profile # Update baseline
""",
    )
    parser.add_argument(
        "--profile",
        help="AWS profile name (default: use AWS_PROFILE env or default)",
    )
    parser.add_argument(
        "--init",
        action="store_true",
        help="Initialize baseline with current AWS IAM users",
    )
    parser.add_argument(
        "--update",
        action="store_true",
        help="Update baseline with current AWS IAM users",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force overwrite existing baseline (with --init)",
    )

    args = parser.parse_args()

    if args.init:
        return cmd_init(args)
    elif args.update:
        return cmd_update(args)
    else:
        return cmd_check(args)


if __name__ == "__main__":
    sys.exit(main())
