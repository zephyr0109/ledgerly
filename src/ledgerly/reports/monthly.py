import pandas as pd
import plotly.express as px
from .base import get_connection, OUTPUT_DIR, ensure_output_dir

def get_expense_summary(start_date, end_date):
    sql = f"""
    SELECT
        category,
        merchant_name,
        SUM(amount) AS total_amount
    FROM expenditure
    WHERE used_at >= '{start_date}'
    AND used_at < '{end_date}'
    GROUP BY category, merchant_name
    ORDER BY total_amount DESC
    """
    with get_connection() as conn:
        return pd.read_sql_query(sql, conn)

def get_income_summary(start_date, end_date):
    sql = f"""
    SELECT SUM(amount) AS total_income, income_type
    FROM income
    WHERE income_date >= '{start_date}'
    AND income_date < '{end_date}'
    GROUP BY income_type
    """
    with get_connection() as conn:
        return pd.read_sql_query(sql, conn)

def generate_monthly_report_content(start_date, end_date, report_year_month):
    """
    Generates monthly report data, markdown, and charts.
    """
    ensure_output_dir()
    expense_summary_df = get_expense_summary(start_date, end_date)
    income_summary_df = get_income_summary(start_date, end_date)

    # 데이터가 없는 경우를 대비하여 안전하게 합계 계산
    expense_sum = expense_summary_df.sum(numeric_only=True)
    total_expense = expense_sum.get("total_amount", 0)

    income_sum = income_summary_df.sum(numeric_only=True)
    total_income = income_sum.get("total_income", 0)

    expense_excluding_invest_df = expense_summary_df[~expense_summary_df["category"].isin(["저축", "투자"])]
    expense_excluding_invest_sum = expense_excluding_invest_df.sum(numeric_only=True)
    expense_excluding_invest = expense_excluding_invest_sum.get("total_amount", 0)

    net_profit = total_income - total_expense
    adjusted_net = total_income - expense_excluding_invest

    # Summary Markdown
    summary_md = f"""# {report_year_month} 월간 보고서

## 1. 순수익 요약

| 항목 | 금액 (원) |
|------|-----------|
| 총 수입 | {total_income:,.0f} |
| 총 지출 | {total_expense:,.0f} |
| 총 지출 (저축/투자 제외) | {expense_excluding_invest:,.0f} |
| 순수익 (수입 - 지출) | {net_profit:,.0f} |
| 실질 순수익 (저축/투자 제외) | {adjusted_net:,.0f} |
"""

    # Income Detail Markdown
    income_rows = ""
    for _, row in income_summary_df.iterrows():
        income_rows += f"| {row['income_type']} | {row['total_income']:,.0f} |\n"
    income_detail_md = f"\n## 2. 수입 상세\n\n| 수입 형태 | 금액 (원) |\n|------------|-----------|\n{income_rows}"

    # Expense Category Summary
    category_summary = (
        expense_summary_df
        .groupby("category", as_index=False)["total_amount"]
        .sum()
        .sort_values(by="total_amount", ascending=False)
    )
    
    expense_rows = ""
    for _, row in category_summary.iterrows():
        expense_rows += f"| {row['category']} | {int(row['total_amount']):,} |\n"
    expense_rows += f"| **총 지출** | **{int(total_expense):,}** |\n"
    
    expense_category_md = f"\n## 3-1. 지출 분류별 요약\n\n| 분류 | 금액 (원) |\n|----------|-----------|\n{expense_rows}"

    # Expense Chart
    chart_file_path = OUTPUT_DIR / f"{report_year_month}-expense-category-chart.png"
    fig = px.pie(category_summary, names="category", values="total_amount", title=f"{report_year_month} 지출 분류별 비율")
    fig.update_traces(textinfo="percent+label")
    fig.write_image(str(chart_file_path))
    
    expense_chart_md = f"\n## 3-2. 지출 분류 차트\n![지출 분류 차트 보기]({chart_file_path.name})\n"

    # Expense Detail
    detail_rows = ""
    for _, row in expense_summary_df.iterrows():
        detail_rows += f"| {row['category']} | {row['merchant_name']} | {int(row['total_amount']):,} |\n"
    detail_rows += f"| **총합** |  | **{int(total_expense):,}** |\n"
    
    expense_detail_md = f"\n## 3-3. 지출 분류별 상세\n| 분류 |사용처| 금액 (원) |\n|----------|-----------|-----------|\n{detail_rows}"

    full_markdown = summary_md + income_detail_md + expense_category_md + expense_chart_md + expense_detail_md
    return full_markdown
