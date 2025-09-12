from pathlib import Path
from fmg.writer import FmgWriter

EXT = '*.csv'

runglish_csv_path = Path(r'runglish_csv_text\text\runglish')
translated_fmg_path = Path(r'translated_text\text\russian')
runglish_csv_files = list(runglish_csv_path.rglob(EXT))

fmg_writer = FmgWriter()
for file in runglish_csv_files:
    fmg_writer.write_csv_file_to_fmg(file)
