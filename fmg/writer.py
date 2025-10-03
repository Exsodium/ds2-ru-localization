from pathlib import Path
import struct
import os
from openpyxl import Workbook
import csv
from fmg.reader import FmgReader


class FmgWriter:
    def write_fmg_files_to_csv(self, eng_file_path: Path, rus_file_path: Path) -> None:
        workbook = Workbook()
        self.sheet = workbook.active

        is_eng = True
        self.write_fmg_file_to_excel(eng_file_path, is_eng)

        is_eng = False
        self.write_fmg_file_to_excel(rus_file_path, is_eng)

        runglish_csv_file_path_str = str(rus_file_path).replace(
            'original_text',
            'runglish_csv_text'
        ).replace('russian', 'runglish')
        runglish_csv_file_path = Path(runglish_csv_file_path_str)
        runglish_csv_file_path.parent.mkdir(exist_ok=True, parents=True)

        with open(f'{runglish_csv_file_path}.csv', 'w', encoding='utf-16', newline='') as file:
            writer = csv.writer(file, delimiter='^', quotechar=None)

            for row in self.sheet.rows:
                writer.writerow([cell.value for cell in row])

        workbook.close()

    def write_fmg_file_to_excel(self, file_path: str, is_eng: bool) -> None:
        with open(file_path, 'rb') as self.file:
            FmgReader.read_int(self.file, int_type=8, offset=9)

            num_entries = FmgReader.read_int(
                self.file,
                int_type=32,
                offset=0xC
            )
            start_offset = FmgReader.read_int(
                self.file,
                int_type=32,
                offset=0x14
            )
            row_number = 0

            for i in range(num_entries):
                start_index = FmgReader.read_int(
                    self.file,
                    int_type=32,
                    offset=0x1C + i * 0xC
                )
                start_id = FmgReader.read_int(
                    self.file,
                    int_type=32,
                    offset=0x1C + i * 0xC + 4
                )
                end_id = FmgReader.read_int(
                    self.file,
                    int_type=32,
                    offset=0x1C + i * 0xC + 8
                )

                for id in range(start_id, end_id + 1):
                    text_offset = FmgReader.read_int(
                        self.file,
                        int_type=32,
                        offset=start_offset + (start_index + id - start_id) * 4
                    )
                    text = str()

                    if text_offset > 0:
                        text = FmgReader.read_unicode_string(
                            self.file,
                            text_offset
                        )
                        text = text.replace('\n', '/n/')

                    row_number += 1

                    if is_eng:
                        id_column_char = 'A'
                        text_column_char = 'B'
                    else:
                        id_column_char = 'D'
                        text_column_char = 'E'

                    self.sheet[f'{id_column_char}{row_number}'] = id
                    self.sheet[f'{text_column_char}{row_number}'] = text

    def write_csv_file_to_fmg(self, runglish_csv_path: Path) -> None:
        with open(runglish_csv_path, 'r', encoding='utf-16', newline='') as self.csv_file:
            csv_lines = self.csv_file.readlines()

        translated_path_str = str(runglish_csv_path)[:-4]
        translated_path_str = translated_path_str.replace(
            'runglish_csv_text',
            'translated_text'
        ).replace('runglish', 'russian')
        translated_path = Path(translated_path_str)
        translated_path.parent.mkdir(exist_ok=True, parents=True)

        with open(translated_path, 'wb') as self.fmg_file:
            entries_amount = 0
            previous_id = -2
            chunks_amount = 0

            for line in csv_lines:
                line_content = line.split('^')
                current_id = int(line_content[0])

                if current_id > previous_id + 1:
                    chunks_amount += 1

                entries_amount += 1
                previous_id = current_id

            start_offset = 0x1c + 0xC * chunks_amount
            text_offset = start_offset + entries_amount * 4

            first_id = int(csv_lines[0].split('^')[0])
            last_id = first_id
            start_entry = 0
            entries_amount = 0
            chunks_amount = 0

            for line in csv_lines:
                line_content = line.split('^')
                current_id = int(line_content[0])

                if current_id > last_id + 1:
                    self.write_int(
                        int_type=32,
                        offset=0x1C + chunks_amount * 0xC,
                        value=start_entry
                    )
                    self.write_int(
                        int_type=32,
                        offset=0x1C + chunks_amount * 0xC + 4,
                        value=first_id
                    )
                    self.write_int(
                        int_type=32,
                        offset=0x1C + chunks_amount * 0xC + 8,
                        value=last_id
                    )

                    first_id = current_id
                    start_entry = entries_amount
                    chunks_amount += 1

                string = line_content[-1].replace('\r\n', '')

                if string:
                    self.write_int(
                        int_type=32,
                        offset=start_offset + entries_amount * 4,
                        value=text_offset
                    )

                    string = string.replace('/n/', '\n')

                    if not string.endswith('\0'):
                        string += '\0'

                    self.write_unicode_string(text_offset, string)
                    text_offset += len(string) * 2

                entries_amount += 1
                last_id = current_id

            if os.fstat(self.fmg_file.fileno()).st_size % 4 == 2:
                self.write_int(
                    int_type=16,
                    offset=text_offset,
                    value=0
                )

            self.write_int(
                int_type=32,
                offset=0x1C + chunks_amount * 0xC,
                value=start_entry
            )
            self.write_int(
                int_type=32,
                offset=0x1C + chunks_amount * 0xC + 4,
                value=first_id
            )
            self.write_int(
                int_type=32,
                offset=0x1C + chunks_amount * 0xC + 8,
                value=last_id
            )

            self.write_int(
                int_type=32,
                offset=0,
                value=0x10000
            )
            self.write_int(
                int_type=8,
                offset=0x8,
                value=1
            )

            self.write_int(
                int_type=32,
                offset=0x4,
                value=os.fstat(self.fmg_file.fileno()).st_size
            )
            self.write_int(
                int_type=32,
                offset=0xC,
                value=chunks_amount + 1
            )
            self.write_int(
                int_type=32,
                offset=0x10,
                value=entries_amount
            )
            self.write_int(
                int_type=32,
                offset=0x14,
                value=start_offset
            )

    def write_unicode_string(self, offset: int, string: str) -> None:
        self.fmg_file.seek(offset)
        encoded_string = string.encode('utf-16-le')
        self.fmg_file.write(encoded_string)

    def write_int(self, int_type: int, offset: int, value: int) -> None:
        self.fmg_file.seek(offset)

        match int_type:
            case 8:
                format = 'b'
            case 16:
                format = '<h'
            case 32:
                format = '<i'

        self.fmg_file.write(struct.pack(format, value))


if __name__ == '__main__':
    pass
