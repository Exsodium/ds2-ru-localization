from pathlib import Path
from fmg.writer import FmgWriter
from time import time

EXT = '*.fmg'

english_path = Path(r'original_text\text\english')
russian_path = Path(r'original_text\text\russian')
runglish_files = list(zip(english_path.rglob(EXT), russian_path.rglob(EXT)))

fmg_writer = FmgWriter()
start_time = time()

for english_file, russian_file in runglish_files:
    fmg_writer.write_fmg_files_to_csv(english_file, russian_file)

end_time = time()
print(f'{round(end_time - start_time, 3)} с.')
