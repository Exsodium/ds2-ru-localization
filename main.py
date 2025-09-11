from pathlib import Path
from fmg import FmgReader

EXT = '*.fmg'

english_path = Path(r'text\english')
russian_path = Path(r'text\russian')
runglish_files = list(zip(english_path.rglob(EXT), russian_path.rglob(EXT)))

reader = FmgReader()
for english_file, russian_file in runglish_files:
    reader.write_fmg_files_to_csv(english_file, russian_file)
