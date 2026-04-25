import pdfkit
from pathlib import Path

class PdfExporter:
    """Markdown 또는 HTML을 PDF로 변환하는 인프라 클래스입니다."""
    
    def __init__(self, wkhtmltopdf_path: str = None):
        # 필요 시 경로 설정 가능
        self.config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path) if wkhtmltopdf_path else None

    def export_markdown_to_pdf(self, markdown_content: str, output_path: Path) -> bool:
        """마크다운 내용을 PDF로 변환하여 저장합니다."""
        try:
            import markdown
            html_content = markdown.markdown(markdown_content, extensions=['tables'])
            # 기본 스타일 추가 (한글 폰트 등 고려)
            styled_html = f"""
            <html>
            <head><meta charset="utf-8"><style>
                body {{ font-family: 'Malgun Gothic', sans-serif; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style></head>
            <body>{html_content}</body>
            </html>
            """
            pdfkit.from_string(styled_html, str(output_path), configuration=self.config)
            return True
        except Exception as e:
            print(f"PDF 변환 오류: {e}")
            return False
