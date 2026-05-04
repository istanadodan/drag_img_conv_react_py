#!/usr/bin/env python3
import os
import sys
from pathlib import Path
from PIL import Image
import pillow_heif
from services.converter import image_format_converter


def _convert_heic_to_jpg(heic_file, quality) -> tuple[int, int, int]:
    """
    HEIC → JPG 변환 (최대한 품질 보존)
    - EXIF 메타데이터 보존 (GPS, 촬영정보, 방향)
    - ICC 색상 프로파일 보존
    - 크로마 서브샘플링 비활성화 (4:4:4)
    - 파일 타임스탬프 보존
    """
    pillow_heif.register_heif_opener()
    # ✅ 고해상도 HEIC 처리를 위해 제한 해제 (신뢰할 수 있는 로컬 파일 전용)
    Image.MAX_IMAGE_PIXELS = None

    converted, failed, skipped = 0, 0, 0

    jpg_file = heic_file.with_suffix(".jpg")

    # 이미 변환된 파일 건너뜀
    if jpg_file.exists():
        print(f"⏭️  건너뜀 (이미 존재)")
        skipped += 1
        return converted, failed, skipped

    try:
        image = Image.open(heic_file)

        # ✅ 1. EXIF 추출 (방향/GPS/카메라 정보)
        exif_data = image.info.get("exif")

        # ✅ 2. ICC 색상 프로파일 추출
        icc_profile = image.info.get("icc_profile")

        # ✅ 3. EXIF 방향(Orientation) 자동 적용
        #    pillow_heif는 대부분 자동처리하지만 명시적으로 보장
        # image = _apply_exif_orientation(image)

        # RGB 변환 (JPEG는 알파채널 미지원)
        if image.mode == "RGBA":
            background = Image.new("RGB", image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[3])
            image = background
        elif image.mode != "RGB":
            image = image.convert("RGB")

        # ✅ 4. 저장 - 핵심 품질 옵션
        save_kwargs = {
            "format": "JPEG",
            "quality": quality,  # 100 = 최대 품질
            "subsampling": 1,  # 4:4:4 - 크로마 서브샘플링 없음 (기본값 2는 4:2:0)
            "optimize": True,
            "progressive": True,
        }
        if exif_data:
            save_kwargs["exif"] = exif_data
        if icc_profile:
            save_kwargs["icc_profile"] = icc_profile

        image.save(jpg_file, **save_kwargs)

        # ✅ 5. 파일 타임스탬프 보존 (생성일/수정일)
        stat = heic_file.stat()
        os.utime(jpg_file, (stat.st_atime, stat.st_mtime))

        size_mb = jpg_file.stat().st_size / (1024 * 1024)
        print(f"✅변환 완료: {heic_file.name} ({size_mb:.2f} MB)")
        converted += 1
        # 원본삭제
        heic_file.unlink()

    except Exception as e:
        print(f"❌ (오류: {e})")
        # 실패한 파일은 불완전 상태로 남지 않도록 제거
        if jpg_file.exists():
            jpg_file.unlink()
        failed += 1

    return (converted, failed, skipped)


def _apply_exif_orientation(image: Image.Image) -> Image.Image:
    """
    Pillow 10+ 호환 버전 - getexif() 사용
    """
    try:
        from PIL import ExifTags

        # ✅ Pillow 10+ : getexif() 사용 (_getexif 제거됨)
        exif = image.getexif()
        if not exif:
            return image

        orientation_key = next(
            k for k, v in ExifTags.TAGS.items() if v == "Orientation"
        )
        orientation = exif.get(orientation_key)

        rotations = {
            3: Image.Transpose.ROTATE_180,
            6: Image.Transpose.ROTATE_270,
            8: Image.Transpose.ROTATE_90,
        }
        if orientation in rotations:
            image = image.transpose(rotations[orientation])

    except Exception:
        pass

    return image


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
                    [(file, quality) for file in files],
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
