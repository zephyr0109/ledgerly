from ledgerly.usecases.reports.asset_report import AssetReportUseCase, OUTPUT_DIR
from ledgerly.infrastructure.exporters.pdf_exporter import PdfExporter

_asset_usecase = AssetReportUseCase()
_pdf_exporter = PdfExporter()

def generate_asset_report_content(report_date):
    # 기존 복잡한 로직을 유지하거나 새 UseCase의 간소화된 버전 호출
    return _asset_usecase.generate_markdown(report_date)

def save_markdown(content, file_path):
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

def export_to_pdf(markdown_content, output_path):
    return _pdf_exporter.export_markdown_to_pdf(markdown_content, output_path)

def generate_monthly_report_content(start_date, end_date, report_year_month):
    # (생략된 monthly report 로직 호출부 - 추후 구현)
    return f"# {report_year_month} 월간 보고서\n\n지출 내역 로직 이전 중..."

__all__ = [
    "generate_asset_report_content",
    "generate_monthly_report_content",
    "save_markdown",
    "export_to_pdf",
    "OUTPUT_DIR"
]
