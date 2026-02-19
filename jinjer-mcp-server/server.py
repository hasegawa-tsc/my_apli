from mcp.server.fastmcp import FastMCP
import httpx
import os
import time
from typing import Optional, Any

# 環境変数からAPIキーを取得
JINJER_API_KEY = os.environ.get("JINJER_API_KEY")
JINJER_SECRET_KEY = os.environ.get("JINJER_SECRET_KEY")

if not JINJER_API_KEY or not JINJER_SECRET_KEY:
    print("Warning: JINJER_API_KEY and JINJER_SECRET_KEY environment variables are required.")

mcp = FastMCP("jinjer")

class JinjerClient:
    BASE_URL = "https://api.jinjer.biz"

    def __init__(self, api_key: str, secret_key: str):
        self.api_key = api_key
        self.secret_key = secret_key
        self.access_token: Optional[str] = None
        self.token_expiry: float = 0
        self.client = httpx.Client(base_url=self.BASE_URL)

    def _get_token(self) -> str:
        """アクセストークンを取得または更新して返す"""
        current_time = time.time()
        # トークンがあり、有効期限切れまでまだ余裕がある(例えば5分以上)場合は既存のトークンを使用
        if self.access_token and current_time < self.token_expiry - 300:
            return self.access_token

        # 新しいトークンを取得
        response = self.client.get(
            "/v2/token",
            headers={
                "X-API-KEY": self.api_key,
                "X-SECRET-KEY": self.secret_key
            }
        )
        response.raise_for_status()
        data = response.json()

        if data.get("results") != "success":
            raise Exception(f"Failed to get token: {data}")

        self.access_token = data["data"]["access_token"]
        # 有効期限は4時間だが、安全マージンを取って3時間50分とする
        self.token_expiry = current_time + (4 * 3600)
        return self.access_token

    def request(self, method: str, path: str, params: Optional[dict] = None, json_data: Optional[dict] = None) -> Any:
        """認証付きでAPIリクエストを行う"""
        token = self._get_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        response = self.client.request(
            method,
            path,
            headers=headers,
            params=params,
            json=json_data
        )

        # 429 Too Many Requests の場合の簡単なリトライロジックなどはここで考慮可能
        if response.status_code == 429:
            raise Exception("Rate limit exceeded")

        response.raise_for_status()
        return response.json()

# クライアントのインスタンス化（遅延初期化推奨だが、今回は簡易的にグローバル変数で扱う）
# 実際のリクエスト時にインスタンスがない場合はエラーにするか、リクエスト時に作成する
client = None

def get_client() -> JinjerClient:
    global client
    if client is None:
        if not JINJER_API_KEY or not JINJER_SECRET_KEY:
            raise ValueError("JINJER_API_KEY and JINJER_SECRET_KEY environment variables are not set")
        client = JinjerClient(JINJER_API_KEY, JINJER_SECRET_KEY)
    return client

@mcp.tool()
def list_employee_ids(
    page: int = 1,
    employee_id: Optional[str] = None,
    enrollment_classification_id: Optional[str] = None,
    employment_classification_id: Optional[str] = None,
    has_since_changed_at: Optional[str] = None
) -> str:
    """
    従業員ID一覧を取得します。

    Args:
        page: ページ番号 (デフォルト: 1)
        employee_id: 社員番号（部分一致）
        enrollment_classification_id: 在籍区分 (0:在籍, 1:退職, 2:休職)
        employment_classification_id: 雇用区分ID
        has_since_changed_at: 指定日以降に変更されたデータ (yyyy-MM-dd)
    """
    try:
        jinjer = get_client()
        params = {"page": page}
        if employee_id:
            params["employee-id"] = employee_id
        if enrollment_classification_id:
            params["enrollment-classification-id"] = enrollment_classification_id
        if employment_classification_id:
            params["employment-classification-id"] = employment_classification_id
        if has_since_changed_at:
            params["has-since-changed-at"] = has_since_changed_at

        result = jinjer.request("GET", "/v1/employees/employee-ids", params=params)
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def list_employees(
    page: int = 1,
    employee_ids: Optional[str] = None,
    has_since_changed_at: Optional[str] = None,
    employee_last_name: Optional[str] = None,
    employee_first_name: Optional[str] = None,
    joined_on_period_start_date: Optional[str] = None,
    joined_on_period_end_date: Optional[str] = None,
    retirement_period_start_date: Optional[str] = None,
    retirement_period_end_date: Optional[str] = None,
    enrollment_classification_id: Optional[str] = None,
    employment_classification_id: Optional[str] = None,
) -> str:
    """
    従業員情報を取得します。

    Args:
        page: ページ番号 (デフォルト: 1)
        employee_ids: 社員番号（カンマ区切りで複数指定可、最大100件）
        has_since_changed_at: 指定日以降に更新されたデータ (yyyy-MM-dd)
        employee_last_name: 氏（部分一致）
        employee_first_name: 名（部分一致）
        joined_on_period_start_date: 入社年月日期間開始 (yyyy-MM-dd)
        joined_on_period_end_date: 入社年月日期間終了 (yyyy-MM-dd)
        retirement_period_start_date: 退職年月日期間開始 (yyyy-MM-dd)
        retirement_period_end_date: 退職年月日期間終了 (yyyy-MM-dd)
        enrollment_classification_id: 在籍区分 (0:在籍, 1:退職, 2:休職)
        employment_classification_id: 雇用区分ID
    """
    try:
        jinjer = get_client()
        params = {"page": page}

        # オプショナルパラメータの設定
        if employee_ids:
            params["employee-ids"] = employee_ids
        if has_since_changed_at:
            params["has-since-changed-at"] = has_since_changed_at
        if employee_last_name:
            params["employee-last-name"] = employee_last_name
        if employee_first_name:
            params["employee-first-name"] = employee_first_name
        if joined_on_period_start_date:
            params["joined-on-period-start-date"] = joined_on_period_start_date
        if joined_on_period_end_date:
            params["joined-on-period-end-date"] = joined_on_period_end_date
        if retirement_period_start_date:
            params["retirement-period-start-date"] = retirement_period_start_date
        if retirement_period_end_date:
            params["retirement-period-end-date"] = retirement_period_end_date
        if enrollment_classification_id:
            params["enrollment-classification-id"] = enrollment_classification_id
        if employment_classification_id:
            params["employment-classification-id"] = employment_classification_id

        result = jinjer.request("GET", "/v1/employees", params=params)
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def list_labor_hour_settings(
    page: int = 1,
    employee_ids: Optional[str] = None,
    has_since_changed_at: Optional[str] = None,
    year: Optional[str] = None
) -> str:
    """
    従業員に紐づく勤怠情報を取得します。

    Args:
        page: ページ番号 (デフォルト: 1)
        employee_ids: 社員番号（カンマ区切りで複数指定可、最大100件）
        has_since_changed_at: 指定日以降に新規登録または更新されたデータ (yyyy-MM-dd)
        year: 指定した年のデータ (yyyy)
    """
    try:
        jinjer = get_client()
        params = {"page": page}
        if employee_ids:
            params["employee-ids"] = employee_ids
        if has_since_changed_at:
            params["has-since-changed-at"] = has_since_changed_at
        if year:
            params["year"] = year

        result = jinjer.request("GET", "/v1/employees/labor-hour-settings", params=params)
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def list_attendances(
    month: str,
    page: int = 1,
    employee_ids: Optional[str] = None
) -> str:
    """
    従業員に紐づく打刻データを取得します。

    Args:
        month: 打刻データの年月 (yyyy-MM)
        page: ページ番号 (デフォルト: 1)
        employee_ids: 社員番号（カンマ区切りで複数指定可）
    """
    try:
        jinjer = get_client()
        params = {"month": month, "page": page}
        if employee_ids:
            params["employee-ids"] = employee_ids

        result = jinjer.request("GET", "/v2/employees/attendances", params=params)
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def list_salary_statements(
    executed_on: str,
    page: int = 1,
    employee_ids: Optional[str] = None,
    has_since_changed_at: Optional[str] = None
) -> str:
    """
    従業員に紐づく給与計算結果を取得します。

    Args:
        executed_on: 処理月 (yyyy-MM) [必須]
        page: ページ番号 (デフォルト: 1)
        employee_ids: 社員番号（カンマ区切りで複数指定可、最大100件）
        has_since_changed_at: 指定された年月日以降に新規登録または更新されたデータ (yyyy-MM-dd)
    """
    try:
        jinjer = get_client()
        params = {"executed-on": executed_on, "page": page}
        if employee_ids:
            params["employee-ids"] = employee_ids
        if has_since_changed_at:
            params["has-since-changed-at"] = has_since_changed_at

        result = jinjer.request("GET", "/v1/employees/salary-statements", params=params)
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    mcp.run()
