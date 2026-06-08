from pathlib import Path
import argparse
import os
import re
import shutil


def parse_args():
    parser = argparse.ArgumentParser(
        description="공식 따릉이 월별 CSV 파일명을 파이프라인 입력 규칙으로 정리한다."
    )
    parser.add_argument("--year", required=True, help="분석 연도. 예: 2025")
    parser.add_argument("--source-dir", required=True, help="공식 CSV 파일이 있는 폴더")
    parser.add_argument("--output-dir", required=True, help="정리된 CSV 파일을 둘 폴더")
    parser.add_argument(
        "--link-mode",
        choices=["hardlink", "symlink", "copy"],
        default="hardlink",
        help="파일 정리 방식. 기본값은 디스크를 거의 추가로 쓰지 않는 hardlink",
    )
    parser.add_argument("--overwrite", action="store_true", help="기존 출력 파일 덮어쓰기")
    return parser.parse_args()


def find_month(path: Path, year: str) -> str:
    year_suffix = year[-2:]
    match = re.search(r"_(\d{2})(\d{2})\.csv$", path.name)

    if not match:
        raise ValueError(f"월 정보를 찾지 못함: {path.name}")

    file_year_suffix, month = match.groups()

    if file_year_suffix != year_suffix:
        raise ValueError(f"연도 불일치: {path.name}, expected={year_suffix}")

    if month < "01" or month > "12":
        raise ValueError(f"월 범위 오류: {path.name}")

    return month


def link_or_copy(source: Path, target: Path, link_mode: str, overwrite: bool) -> None:
    if target.exists() or target.is_symlink():
        if not overwrite:
            raise FileExistsError(f"이미 존재함: {target}")

        target.unlink()

    if link_mode == "hardlink":
        os.link(source, target)
    elif link_mode == "symlink":
        target.symlink_to(source.resolve())
    else:
        shutil.copy2(source, target)


def main():
    args = parse_args()
    year = args.year
    source_dir = Path(args.source_dir)
    output_dir = Path(args.output_dir)

    if not source_dir.exists():
        raise FileNotFoundError(f"source-dir 없음: {source_dir}")

    output_dir.mkdir(parents=True, exist_ok=True)

    source_files = sorted(source_dir.glob("*.csv"))

    if not source_files:
        raise FileNotFoundError(f"CSV 파일 없음: {source_dir}")

    prepared = []

    for source_file in source_files:
        month = find_month(source_file, year)
        target = output_dir / f"seoul_bike_{year}_{month}.csv"
        link_or_copy(source_file, target, args.link_mode, args.overwrite)
        prepared.append(target)
        print(f"{source_file.name} -> {target.name}")

    if len(prepared) != 12:
        raise ValueError(f"월별 파일 수가 12개가 아님: {len(prepared)}")

    print("prepared_files")
    print(output_dir)


if __name__ == "__main__":
    main()
