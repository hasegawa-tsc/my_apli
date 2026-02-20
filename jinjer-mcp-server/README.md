# Jinjer MCP Server

Jinjer APIのModel Context Protocol (MCP) サーバー実装です。

## セットアップ

1. **Pythonのインストール**
   Python 3.12以上が必要です。

2. **依存関係のインストール**
   uvを使用している場合は、以下のコマンドでセットアップできます：
   ```bash
   uv sync
   ```

## 使い方

### 環境変数の設定

実行前に以下の環境変数を設定してください。

- `JINJER_API_KEY`: Jinjer APIのAPIキー
- `JINJER_SECRET_KEY`: Jinjer APIのシークレットキー

Windows (PowerShell) の場合:
```powershell
$env:JINJER_API_KEY="your_api_key"
$env:JINJER_SECRET_KEY="your_secret_key"
```

### サーバーの実行

uvを使用してサーバーを実行します：

```bash
uv run server.py
```

### 利用可能なツール

- `list_employee_ids`: 従業員ID一覧を取得します。
  - `page`: ページ番号 (デフォルト: 1)
  - `employee_id`: 社員番号（部分一致）
  - `enrollment_classification_id`: 在籍区分 (0:在籍, 1:退職, 2:休職)
  - `employment_classification_id`: 雇用区分ID
  - `has_since_changed_at`: 指定日以降に変更されたデータ (yyyy-MM-dd)

- `list_employees`: 従業員情報を取得します。
  - `page`: ページ番号 (デフォルト: 1)
  - `employee_ids`: 社員番号（カンマ区切りで複数指定可、最大100件）
  - `has_since_changed_at`: 指定日以降に更新されたデータ
  - `employee_last_name`: 氏（部分一致）
  - `employee_first_name`: 名（部分一致）
  - `joined_on_period_start_date`: 入社年月日期間開始
  - `joined_on_period_end_date`: 入社年月日期間終了
  - `retirement_period_start_date`: 退職年月日期間開始
  - `retirement_period_end_date`: 退職年月日期間終了
  - `enrollment_classification_id`: 在籍区分 (0:在籍, 1:退職, 2:休職)
  - `employment_classification_id`: 雇用区分ID

- `list_labor_hour_settings`: 従業員に紐づく勤怠情報を取得します。
  - `page`: ページ番号 (デフォルト: 1)
  - `employee_ids`: 社員番号（カンマ区切りで複数指定可、最大100件）
  - `has_since_changed_at`: 指定日以降に新規登録または更新されたデータ (yyyy-MM-dd)
  - `year`: 指定した年のデータ (yyyy)

- `list_attendances`: 従業員に紐づく打刻データを取得します。
  - `month`: 打刻データの年月 (yyyy-MM)
  - `page`: ページ番号 (デフォルト: 1)
  - `employee_ids`: 社員番号（カンマ区切りで複数指定可）

- `list_salary_statements`: 従業員に紐づく給与計算結果を取得します。
  - `executed_on`: 処理月 (yyyy-MM) [必須]
  - `page`: ページ番号 (デフォルト: 1)
  - `employee_ids`: 社員番号（カンマ区切りで複数指定可、最大100件）
  - `has_since_changed_at`: 指定された年月日以降に新規登録または更新されたデータ (yyyy-MM-dd)

- `list_requested_day_offs`: 従業員に紐づく休日休暇データを取得します。
  - `month`: 取得する休日休暇データの年月 (yyyy-MM) [必須]
  - `page`: ページ番号 (デフォルト: 1)
  - `employee_ids`: 社員番号（カンマ区切りで複数指定可、最大100件）

## 開発

依存関係の追加:
```bash
uv add [package_name]
```
