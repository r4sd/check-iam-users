# check_iam_users

AWS IAM ユーザーの差分チェックツール

## 概要

ベースラインリストと AWS IAM ユーザーを比較して差分を検出する:

- **Added**: AWS にいるがベースラインにない（不正/野良アカウント検出）
- **Missing**: ベースラインにあるが AWS にいない（削除事故/作成漏れ検出）

## 必要条件

- Python 3.12+
- boto3
- 有効な AWS 認証情報

## インストール

```bash
pip install boto3
```

開発用:

```bash
pip install -e .[dev]
```

## 使い方

### 初回: ベースライン作成

```bash
python check_users.py --init --profile my-profile
```

### 差分チェック

```bash
python check_users.py --profile my-profile
```

### ベースライン更新

```bash
python check_users.py --update --profile my-profile
```

## コマンドオプション

| オプション | 説明 |
|-----------|------|
| `--profile` | AWS プロファイル名（省略時は環境変数 `AWS_PROFILE` または default） |
| `--init` | 現在の AWS IAM ユーザーでベースラインを作成 |
| `--update` | 現在の AWS IAM ユーザーでベースラインを更新 |
| `--force` | 既存のベースラインを上書き（`--init` と併用） |

## 出力ファイル

| ファイル | 内容 |
|---------|------|
| `iam_users_baseline.txt` | ベースラインユーザーリスト |
| `iam_users_added.txt` | AWS にいるがベースラインにないユーザー |
| `iam_users_missing.txt` | ベースラインにあるが AWS にいないユーザー |

## 出力例

```
=== IAM Users Diff Check ===
Baseline: 10 users
AWS:      12 users

Added (2):    # AWS にいるが baseline にない
  + new_user_1
  + new_user_2

Missing (0):  # baseline にあるが AWS にいない
  (none)

結果を保存しました:
  - iam_users_added.txt
  - iam_users_missing.txt
```

## テスト実行

```bash
pytest -v
```

## Docker でのテスト実行

```bash
# テスト実行
docker compose run test

# リンター
docker compose run lint

# フォーマットチェック
docker compose run format

# フォーマット適用（修正）
docker compose run format-fix

# 全チェック（CI相当）
docker compose run ci
```

## CI

GitHub Actions で以下を自動実行:

- `ruff check`: リンター
- `ruff format --check`: フォーマットチェック
- `pytest`: テスト
