from pathlib import Path
import csv


RAW_DIR = Path("data/raw/extracted")
SAMPLE_PATH = Path("data/sample/seoul_bike_sample.csv")
SAMPLE_ROWS = 999
ENCODINGS = ["utf-8-sig", "utf-8", "cp949", "euc-kr"]


def find_main_csv(raw_dir: Path) -> Path:
    csv_files = [
        path for path in raw_dir.rglob("*.csv")
        if path.is_file() and path.stat().st_size > 0
    ]

    if not csv_files:
        raise FileNotFoundError("data/raw/extracted 폴더에서 비어있지 않은 CSV 파일을 찾지 못함")

    csv_files.sort(key=lambda path: path.stat().st_size, reverse=True)
    return csv_files[0]


def write_sample(input_path: Path, output_path: Path, sample_rows: int) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    for encoding in ENCODINGS:
        try:
            written_rows = 0

            with input_path.open("r", encoding=encoding, newline="") as src:
                reader = csv.reader(src)

                with output_path.open("w", encoding="utf-8-sig", newline="") as dst:
                    writer = csv.writer(dst)

                    for row_idx, row in enumerate(reader):
                        if row_idx > sample_rows:
                            break

                        writer.writerow(row)
                        written_rows += 1

            if written_rows == 0:
                raise ValueError("CSV 파일을 열었으나, 작성된 데이터가 없음.")

          
            print(f" 원본 파일 경로: {input_path}")
            print(f" 인코딩 방식  : {encoding}")
            print(f" 저장된 파일  : {output_path}")
            print(f" 추출된 행 개수: {written_rows}개 (헤더 포함)")
            return

        except UnicodeDecodeError:
            continue

    raise UnicodeDecodeError(
        "unknown",
        b"",
        0,
        1,
        "지원하는 인코딩 형식 없음. 파일 확인.",
    )


if __name__ == "__main__":
    main_csv = find_main_csv(RAW_DIR)
    write_sample(main_csv, SAMPLE_PATH, SAMPLE_ROWS)
