#!/usr/bin/env python3
import os
import sys
from pathlib import Path
from PIL import Image
import pillow_heif
from services.converter import image_format_converter


def select_folder():
    print("=" * 50)
    print("🖼️  HEIC to JPG 변환기 (품질 최대 보존)")
    print("=" * 50)

    while True:
        folder = input("\n변환할 폴더 경로를 입력하세요: ").strip().strip("\"'")
        if not folder:
            print("❌ 폴더 경로를 입력해주세요.")
            continue
        if Path(folder).is_dir():
            return folder
        print(f"❌ 폴더를 찾을 수 없습니다: {folder}")


def get_allfiles_in(path: str) -> list[Path] | None:

    folder_path = Path(path)

    if not folder_path.exists():
        print(f"❌ 폴더를 찾을 수 없습니다: {folder_path}")
        return
    if not folder_path.is_dir():
        print(f"❌ 디렉토리가 아닙니다: {folder_path}")
        return

    # 대소문자 구분없이 수집
    heic_files = list(
        folder_path.rglob("*.heic")
    )  # + list(folder_path.rglob("*.HEIC"))

    if not heic_files:
        print("⚠️  HEIC 파일을 찾을 수 없습니다.")
        return

    print(f"🔍 {len(heic_files)}개의 HEIC 파일 발견\n")

    return heic_files


from concurrent.futures import ThreadPoolExecutor
import os
from itertools import repeat


def get_quality():
    """사용자로부터 품질값(1-100) 입력받기"""
    while True:
        try:
            quality = input("\n품질값을 입력하세요 (1-100, 기본값: 90): ").strip()
            if not quality:
                return 90
            quality = int(quality)
            if 1 <= quality <= 100:
                return quality
            print("❌ 1-100 사이의 값을 입력해주세요.")
        except ValueError:
            print("❌ 숫자를 입력해주세요.")


def _convert_to_tuple(result: dict) -> tuple:
    """Convert result to tuple if it's not already."""
    match (result["status"]):
        case "converted":
            return (1, 0, 0)
        case "failed":
            return (0, 1, 0)
        case "skipped":
            return (0, 0, 1)
        case _:
            print(f"Unknown status: {result['status']}")
            return (0, 0, 0)


if __name__ == "__main__":
    from functools import reduce

    try:
        folder_path = sys.argv[1] if len(sys.argv) > 1 else select_folder()
        quality = sys.argv[2] if len(sys.argv) > 2 else get_quality()
        print()

        if files := get_allfiles_in(folder_path):
            aggr = [0, 0, 0]
            with ThreadPoolExecutor(
                max_workers=os.cpu_count(), thread_name_prefix="pic"
            ) as executor:
                tasks = executor.map(
                    lambda args: image_format_converter.convert_with_suffix(*args),
                    [(file, quality, None, False) for file in files],
                )
                aggr = reduce(
                    lambda acc, task: list(map(sum, zip(acc, _convert_to_tuple(task)))),
                    tasks,
                    [0, 0, 0],
                )

                converted, failed, skipped = aggr
                print(f"\n{'='*50}")
                print(f"✅ 변환 완료 : {converted}개")
                print(f"⏭️  건너뜀   : {skipped}개")
                print(f"❌ 실패      : {failed}개")
                print(f"{'='*50}")

    except KeyboardInterrupt:
        print("\n\n❌ 사용자가 중단했습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        sys.exit(1)
