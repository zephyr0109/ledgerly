import pandas as pd
import plotly.express as px
from .base import get_connection, OUTPUT_DIR, ensure_output_dir

def get_asset_report_dates(report_date):
    """
    Get previous and year-start dates for assets and debts.
    """
    with get_connection() as conn:
        asset_prev_date = pd.read_sql_query(
            "SELECT MAX(snapshot_date) FROM asset_snapshot WHERE snapshot_date < ?",
            conn, params=(report_date,)
        ).iloc[0, 0]

        asset_year_start_date = pd.read_sql_query(
            "SELECT MIN(snapshot_date) FROM asset_snapshot WHERE strftime('%Y', snapshot_date) = strftime('%Y', ?)",
            conn, params=(report_date,)
        ).iloc[0, 0]

        debt_prev_date = pd.read_sql_query(
            "SELECT MAX(snapshot_date) FROM debt_snapshot WHERE snapshot_date < ?",
            conn, params=(report_date,)
        ).iloc[0, 0]

        debt_year_start_date = pd.read_sql_query(
            "SELECT MIN(snapshot_date) FROM debt_snapshot WHERE strftime('%Y', snapshot_date) = strftime('%Y', ?)",
            conn, params=(report_date,)
        ).iloc[0, 0]

    return asset_prev_date, asset_year_start_date, debt_prev_date, debt_year_start_date

def get_asset_status_df(target_date):
    """
    Fetch most recent snapshots for assets on or before target_date.
    """
    sql = """
    SELECT
        a.asset_name as '자산명',
        s.amount as '금액',
        a.category as '분류',
        a.owner as '명의',
        s.rate as '이율/수익률',
        s.snapshot_date as '집계일'
    FROM asset_account a
    JOIN asset_snapshot s ON a.asset_id = s.asset_id
    WHERE s.snapshot_date = (
        SELECT MAX(s2.snapshot_date)
        FROM asset_snapshot s2
        WHERE s2.asset_id = a.asset_id
        AND s2.snapshot_date <= ?
    )
    ORDER BY s.amount DESC
    """
    with get_connection() as conn:
        return pd.read_sql_query(sql, conn, params=(target_date,))

def get_debt_status_df(target_date):
    """
    Fetch most recent snapshots for debts on or before target_date.
    """
    sql = """
    SELECT
        d.debt_name as '부채명',
        d.owner as '명의',
        d.initial_principal as '초기원금',
        s.principal_amount as '잔액',
        s.interest_rate as '이자율',
        d.repayment_type as '상환방식',
        d.maturity_date as '만기일',
        s.accrued_interest as '누적이자',
        s.snapshot_date as '집계일'
    FROM debt_account d
    JOIN debt_snapshot s ON d.debt_id = s.debt_id
    WHERE s.snapshot_date = (
        SELECT MAX(s2.snapshot_date)
        FROM debt_snapshot s2
        WHERE s2.debt_id = d.debt_id
        AND s2.snapshot_date <= ?
    )
    ORDER BY s.principal_amount DESC
    """
    with get_connection() as conn:
        return pd.read_sql_query(sql, conn, params=(target_date,))

def calc_change(current, base):
    diff = current - base
    rate = (diff / base * 100) if base else 0
    return diff, rate

def generate_asset_report_content(report_date):
    """
    Generates report data, markdown, and charts.
    """
    ensure_output_dir()
    ap_date, ay_date, dp_date, dy_date = get_asset_report_dates(report_date)

    # Get totals
    asset_current_df = get_asset_status_df(report_date)
    asset_current = asset_current_df['금액'].sum()
    asset_prev = get_asset_status_df(ap_date)['금액'].sum() if ap_date else 0
    asset_year_start = get_asset_status_df(ay_date)['금액'].sum() if ay_date else 0

    debt_current_df = get_debt_status_df(report_date)
    debt_current = debt_current_df['잔액'].sum()
    debt_prev = get_debt_status_df(dp_date)['잔액'].sum() if dp_date else 0
    debt_year_start = get_debt_status_df(dy_date)['잔액'].sum() if dy_date else 0

    fin_current = asset_current_df.loc[asset_current_df['분류'] != '현물', '금액'].sum()
    fin_prev = get_asset_status_df(ap_date).loc[lambda x: x['분류'] != '현물', '금액'].sum() if ap_date else 0
    fin_year_start = get_asset_status_df(ay_date).loc[lambda x: x['분류'] != '현물', '금액'].sum() if ay_date else 0

    net_current = asset_current - debt_current
    net_prev = asset_prev - debt_prev
    net_year_start = asset_year_start - debt_year_start

    # Summary table
    metrics = [
        ("총 자산", asset_current, asset_prev, asset_year_start),
        ("총 부채", debt_current, debt_prev, debt_year_start),
        ("순자산", net_current, net_prev, net_year_start),
        ("금융자산", fin_current, fin_prev, fin_year_start),
    ]

    summary_rows = []
    for label, curr, prev, year in metrics:
        diff_m, rate_m = calc_change(curr, prev)
        diff_y, rate_y = calc_change(curr, year)
        summary_rows.append({
            "구분": label,
            "금액": curr,
            "전월 대비 증감": diff_m,
            "전월 대비율(%)": rate_m,
            "연초 대비 증감": diff_y,
            "연초 대비율(%)": rate_y
        })
    summary_df = pd.DataFrame(summary_rows)

    # Markdown - Summary
    report_title = f"# {report_date[:7]} 자산 보고서"
    display_summary_df = summary_df.copy()
    for col in ["금액", "전월 대비 증감", "연초 대비 증감"]:
        display_summary_df[col] = display_summary_df[col].apply(lambda x: f"{x:,.0f}")
    for col in ["전월 대비율(%)", "연초 대비율(%)"]:
        display_summary_df[col] = display_summary_df[col].apply(lambda x: f"{x:.2f}%")
    summary_md = "## 1. 자산 요약\n\n" + display_summary_df.to_markdown(index=False)

    # Markdown - Asset details
    display_asset_df = asset_current_df.copy()
    display_asset_df['금액'] = display_asset_df['금액'].apply(lambda x: f"{x:,}")
    if '이율/수익률' in display_asset_df.columns:
        display_asset_df['이율/수익률'] = display_asset_df['이율/수익률'].apply(lambda x: f"{x}%" if pd.notnull(x) else "-")
    asset_detail_md = f"## 2. 자산 현황 상세 (기준일: {report_date})\n\n" + display_asset_df.to_markdown(index=False)

    # Charts
    dates = pd.date_range(start=ay_date if ay_date else report_date, end=report_date, freq='ME')
    if pd.to_datetime(report_date) > dates[-1] if not dates.empty else True:
        dates = dates.append(pd.DatetimeIndex([report_date]))
    
    trend_data = []
    debt_trend_data = []
    for d in dates:
        d_str = d.strftime("%Y-%m-%d")
        a_df = get_asset_status_df(d_str)
        d_df = get_debt_status_df(d_str)
        trend_data.append({
            "date": d_str,
            "총자산": a_df['금액'].sum(),
            "금융자산": a_df.loc[a_df['분류'] != '현물', '금액'].sum()
        })
        debt_trend_data.append({"date": d_str, "총부채": d_df['잔액'].sum()})
    
    asset_chart_path = OUTPUT_DIR / f"asset_trend_{report_date[:7]}.png"
    fig_asset = px.line(pd.DataFrame(trend_data), x="date", y=["총자산", "금융자산"], markers=True, title="자산 변동 추이")
    fig_asset.update_yaxes(tickformat=",")
    fig_asset.write_image(str(asset_chart_path))

    debt_chart_path = OUTPUT_DIR / f"debt_trend_{report_date[:7]}.png"
    fig_debt = px.line(pd.DataFrame(debt_trend_data), x="date", y="총부채", markers=True, title="부채 변동 추이")
    fig_debt.update_traces(line_color='red')
    fig_debt.update_yaxes(tickformat=",")
    fig_debt.write_image(str(debt_chart_path))

    asset_trend_md = f"## 3. 자산 증감 상세\n\n![자산 증감 차트]({asset_chart_path.name})"
    debt_trend_md = f"## 5. 부채 증감 상세\n\n![부채 증감 차트]({debt_chart_path.name})"

    # Markdown - Debt details
    display_debt_df = debt_current_df.copy()
    display_debt_df['초기원금'] = display_debt_df['초기원금'].apply(lambda x: f"{x:,}")
    display_debt_df['잔액'] = display_debt_df['잔액'].apply(lambda x: f"{x:,}")
    display_debt_df['이자율'] = display_debt_df['이자율'].apply(lambda x: f"{x}%" if pd.notnull(x) else "-")
    if '누적이자' in display_debt_df.columns:
        display_debt_df['누적이자'] = display_debt_df['누적이자'].apply(lambda x: f"{x:,}" if pd.notnull(x) else "-")
    debt_detail_md = f"## 4. 부채 현황 상세 (기준일: {report_date})\n\n" + display_debt_df.to_markdown(index=False)

    full_markdown = "\n\n".join([report_title, summary_md, asset_detail_md, asset_trend_md, debt_detail_md, debt_trend_md])
    return full_markdown
