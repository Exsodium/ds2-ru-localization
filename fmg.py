from io import BufferedReader
from openpyxl import Workbook
import csv
from pathlib import Path


class FmgReader:
    file: BufferedReader = None

    def write_fmg_files_to_csv(self, english_file_path: Path, russian_file_path: Path) -> None:
        workbook = Workbook()
        self.sheet = workbook.active
        is_english = True

        self.write_fmg_file_to_excel(english_file_path, is_english)

        is_english = False
        self.write_fmg_file_to_excel(russian_file_path, is_english)

        self.sheet = workbook.active
        russian_file_path_str = str(
            russian_file_path).replace('russian', 'runglish')
        runglish_file_path = Path(russian_file_path_str)
        runglish_file_path.parent.mkdir(exist_ok=True, parents=True)

        with open(f'{runglish_file_path}.csv', 'w', encoding='utf-16', newline='') as f:
            writer = csv.writer(f, delimiter=',')

            for row in self.sheet.rows:
                writer.writerow([cell.value for cell in row])

        workbook.close()

    def read_int8(self, loc: int) -> int:
        self.file.seek(loc)
        byte = self.file.read(1)
        value = int.from_bytes(byte, byteorder='little', signed=True)

        return value

    def read_int32(self, loc: int) -> int:
        self.file.seek(loc)
        byte = self.file.read(4)

        return int.from_bytes(byte, byteorder='little', signed=True)

    def read_unicode_string(self, loc: int) -> str:
        self.file.seek(loc)
        result = ''

        while True:
            byte = self.file.read(2)
            char = byte.decode('utf-16-le')

            if char == '\x00':
                break

            result += char

        return result

    def write_fmg_file_to_excel(self, file_path: str, is_english: bool) -> None:
        with open(file_path, 'rb') as self.file:
            row = 0
            self.read_int8(9)

            num_entries = self.read_int32(0xC)
            start_offset = self.read_int32(0x14)

            for i in range(num_entries):
                start_index = self.read_int32(0x1C + i * 0xC)
                start_id = self.read_int32(0x1C + i * 0xC + 4)
                end_id = self.read_int32(0x1C + i * 0xC + 8)

                for j in range(start_id, end_id + 1):
                    txt_offset = self.read_int32(
                        start_offset + (start_index + j - start_id) * 4)
                    txt = ''

                    if txt_offset > 0:
                        txt = self.read_unicode_string(txt_offset)
                        txt = txt.replace('\n', '/n/')

                    row += 1

                    if is_english:
                        self.sheet[f'A{row}'] = j
                        self.sheet[f'B{row}'] = txt
                    else:
                        self.sheet[f'D{row}'] = j
                        self.sheet[f'E{row}'] = txt


if __name__ == '__main__':
    pass
