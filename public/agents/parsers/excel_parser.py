"""Парсер Excel файлов."""

from __future__ import annotations

from pathlib import Path

from .base import BaseParser, ParsedDocument


class ExcelParser(BaseParser):
    """Парсер для .xlsx, .xls, .xlsm, .xlsb файлов."""

    @property
    def supported_extensions(self) -> list[str]:
        return [".xlsx", ".xls", ".xlsm", ".xlsb"]

    def can_parse(self, file_path: Path) -> bool:
        return file_path.suffix.lower() in self.supported_extensions

    def parse(self, file_path: Path) -> ParsedDocument:
        """Парсинг Excel файла."""
        try:
            import openpyxl

            wb = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
            all_content = []
            fragments = []
            fragment_id = 0

            for sheet_name in wb.sheetnames:
                ws = wb[sheet_name]
                sheet_content = [f"=== Лист: {sheet_name} ==="]

                for row in ws.iter_rows(values_only=True):
                    row_values = [str(cell) if cell is not None else "" for cell in row]
                    if any(row_values):
                        row_text = " | ".join(v for v in row_values if v)
                        if row_text:
                            sheet_content.append(row_text)

                if len(sheet_content) > 1:
                    fragment_id += 1
                    content = "\n".join(sheet_content)
                    all_content.append(content)
                    fragments.append({
                        "fragment_id": f"frag_{fragment_id}",
                        "title": sheet_name,
                        "text": content,
                        "type": "sheet",
                        "sheet_name": sheet_name,
                    })

            wb.close()

            full_content = "\n\n".join(all_content)

            return ParsedDocument(
                source=str(file_path),
                filename=file_path.name,
                content=full_content,
                fragments=fragments,
                metadata={
                    "encoding": "utf-8",
                    "size": len(full_content),
                    "sheets": wb.sheetnames,
                },
            )
        except ImportError:
            return ParsedDocument(
                source=str(file_path),
                filename=file_path.name,
                content="",
                errors=["openpyxl не установлен. Установите: pip install openpyxl"],
            )
        except Exception as e:
            return ParsedDocument(
                source=str(file_path),
                filename=file_path.name,
                content="",
                errors=[f"Ошибка парсинга Excel: {e}"],
            )

    def parse_text(self, text: str, source: str = "text") -> ParsedDocument:
        """Excel нельзя парсить из текста напрямую."""
        return ParsedDocument(
            source=source,
            filename="excel",
            content="",
            errors=["Excel формат не поддерживает парсинг из текста"],
        )
