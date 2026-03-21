import pypandoc
import os
from pathlib import Path

def export_to_pdf(markdown_text, output_file_path):
    """
    Export Markdown to PDF using pypandoc and wkhtmltopdf.
    """
    try:
        output_dir = Path(output_file_path).parent.resolve()
        original_cwd = os.getcwd()
        try:
            os.chdir(output_dir)
            pypandoc.convert_text(
                markdown_text,
                to="pdf",
                format="md",
                outputfile=str(output_file_path),
                extra_args=[
                    "--pdf-engine=wkhtmltopdf", 
                    "--from=markdown-yaml_metadata_block",
                    "--pdf-engine-opt=--enable-local-file-access"
                ]
            )
        finally:
            os.chdir(original_cwd)
        return True
    except Exception as e:
        print(f"PDF export error: {e}")
        return False

def save_markdown(markdown_text, output_file_path):
    """
    Save Markdown text to a file.
    """
    with open(output_file_path, "w", encoding="utf-8") as f:
        f.write(markdown_text)
