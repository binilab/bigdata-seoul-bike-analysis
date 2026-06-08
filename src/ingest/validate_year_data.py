from pathlib import Path
import argparse
import csv


EXPECTED_HEADER = [
    "자전거번호",
    "대여일시",
    "대여 대여소번호",
    "대여 대여소명",
    "대여거치대",
    "반납일시",
    "반납대여소번호",
    "반납대여소명",
    "반납거치대",
    "이용시간(분)",
    "이용거리(M)",
    "생년",
    "성별",
    "이용자종류",
    "대여대여소ID",
    "반납대여소ID",
    "자전거구분",
]


def parse_args():
    parser = argparse.ArgumentParser(description="연도별 따릉이 CSV 스키마를 점검한다.")
    parser.add_argument("--input-dir", required=True, help="점검할 CSV 폴더")
    parser.add_argument("--glob", default="*.csv", help="점검할 CSV 파일 패턴")
    parser.add_argument("--encoding", default="cp949", help="CSV 인코딩. 기본값: cp949")
    parser.add_argument("--sample-rows", type=int, default=1000, help="파일별 샘플 점검 행 수")
    parser.add_argument("--count-lines", action="store_true", help="전체 라인 수까지 계산")
    return parser.parse_args()


def validate_file(path: Path, encoding: str, sample_rows: int, count_lines: bool):
    bad_rows = []
    line_count = None

    with path.open("r", encoding=encoding, errors="replace", newline="") as file_obj:
        reader = csv.reader(file_obj)
        header = next(reader)

        if header != EXPECTED_HEADER:
            raise ValueError(f"헤더 불일치: {path.name}: {header}")

        for row_idx, row in enumerate(reader, start=2):
            if row_idx > sample_rows + 1:
                break

            if len(row) != len(EXPECTED_HEADER):
                bad_rows.append((row_idx, len(row)))

    if count_lines:
        with path.open("r", encoding=encoding, errors="replace", newline="") as file_obj:
            line_count = sum(1 for _ in file_obj)

    return {
        "file": path.name,
        "bad_rows": bad_rows,
        "line_count": line_count,
    }


def main():
    args = parse_args()
    input_dir = Path(args.input_dir)
    paths = sorted(input_dir.glob(args.glob))

    if not paths:
        raise FileNotFoundError(f"CSV 파일 없음: {input_dir}/{args.glob}")

    total_data_rows = 0

    for path in paths:
        result = validate_file(path, args.encoding, args.sample_rows, args.count_lines)

        if result["bad_rows"]:
            raise ValueError(f"컬럼 수 오류: {result}")

        if result["line_count"] is None:
            print(f"{result['file']}: schema_ok")
        else:
            data_rows = result["line_count"] - 1
            total_data_rows += data_rows
            print(f"{result['file']}: schema_ok, data_rows={data_rows}")

    print("validated_files")
    print(len(paths))

    if args.count_lines:
        print("total_data_rows")
        print(total_data_rows)


if __name__ == "__main__":
    main()
