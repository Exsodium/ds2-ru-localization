from pathlib import Path

EXT = '*.csv'

runglish_csv_path = Path(r'runglish_csv_text\text\runglish')
runglish_csv_files = list(runglish_csv_path.rglob(EXT))

lines_amount = 0
translated_lines_amount = 0
for file in runglish_csv_files:
    with open(file, 'r', encoding='utf-16', newline='') as f:
        for line in f.readlines():
            lines_amount += 1

            line_content = line.split('^')
            is_translated = line_content[2] == '+'

            if is_translated:
                translated_lines_amount += 1

print(translated_lines_amount)
print(lines_amount)
print(f'{round(translated_lines_amount / lines_amount * 100, 3)}%')
