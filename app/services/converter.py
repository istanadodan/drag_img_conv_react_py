import os
from pathlib import Path
from typing import Optional, Union
from io import BytesIO
from PIL import Image, ImageFile
import pillow_heif
from schemas.upload import ResizeConfig
from core.enums import ResizeMode


class ImageFormatConverter:
    def __init__(self):
        # Pillow 설정
        pillow_heif.register_heif_opener()
        Image.MAX_IMAGE_PIXELS = None

    def convert_from_bytes(
        self,
        file_bytes: bytes,
        filename: str,
        output_dir: Path,
        quality: int,
        resize_config: ResizeConfig,
        keep_origin: bool = True,
    ) -> dict:
        """
        HEIC → JPG 변환 (bytes 입력, 파일 저장 없이 메모리에서 처리)

        Args:
            file_bytes: HEIC 파일 bytes
            filename: 원본 파일명
            output_dir: 출력 디렉토리
            quality: JPEG 품질 (1-100)
            resize_config: 리사이징 설정

        Returns:
            {
                "status": "converted" | "skipped" | "failed",
                "output": 생성된 파일 이름 (파일명만),
                "error": 에러 메시지 (실패시에만)
            }
        """
        src_file = output_dir / filename
        output_dir.mkdir(parents=True, exist_ok=True)

        tgt_file = self._create_output_filename(src_file, quality)
        # 이미 변환된 파일 건너뜀
        if tgt_file.exists():
            return {
                "status": "skipped",
                "output": tgt_file.name,
                "error": None,
            }

        try:
            # bytes를 BytesIO로 변환하여 이미지 오픈
            self._run_image_save(file_bytes, tgt_file, quality, resize_config)

            if not keep_origin:
                src_file.unlink()  # 원본 파일 삭제

            return {
                "status": "converted",
                "output": tgt_file.name,
                "error": None,
            }

        except Exception as e:
            # 실패한 파일은 불완전 상태로 남지 않도록 제거
            if tgt_file.exists():
                tgt_file.unlink()

            return {
                "status": "failed",
                "output": jpg_filename,
                "error": str(e),
            }

    def convert_with_suffix(
        self,
        src_file: Path,
        quality: int,
        resize_config: ResizeConfig,
        keep_origin: bool = True,
    ) -> dict:
        """
        HEIC → JPG 변환 (품질 보존, 파일명에 quality suffix 추가)

        동기 함수: asyncio.run_in_executor()로 비동기 컨텍스트에서 호출됨

        Args:
            src_file: 변환할 HEIC 파일 경로
            quality: JPEG 품질 (1-100)
            keep_origin: 원본 파일 유지 여부
            resize: 리사이징 설정 (선택사항)

        Returns:
            {
                "status": "converted" | "skipped" | "failed",
                "output": 생성된 파일 이름 (파일명만),
                "error": 에러 메시지 (실패시에만)
            }

        처리:
            - EXIF 메타데이터 보존 (GPS, 촬영정보, 방향)
            - ICC 색상 프로파일 보존
            - 크로마 서브샘플링 비활성화 (4:4:4)
            - 파일 타임스탬프 보존
            - 이미지 리사이징 (선택사항)
            - 출력 파일명: {stem}_q{quality}.jpg (예: IMG001_q85.jpg)
        """
        jpg_file = self._create_output_filename(src_file, quality)
        # 이미 변환된 파일 건너뜀
        if jpg_file.exists():
            return {
                "status": "skipped",
                "output": jpg_file.name,
                "error": None,
            }

        try:
            self._save_image(src_file, jpg_file, quality, resize_config)

            if not keep_origin:
                src_file.unlink()  # 원본 파일 삭제

            return {
                "status": "converted",
                "output": jpg_file.name,
                "error": None,
            }

        except Exception as e:
            # 실패한 파일은 불완전 상태로 남지 않도록 제거
            if jpg_file.exists():
                jpg_file.unlink()

            return {
                "status": "failed",
                "output": jpg_file.name,
                "error": str(e),
            }

    def _create_save_kwargs(self, image: ImageFile.ImageFile, quality: int) -> dict:
        # EXIF 추출
        exif_data = image.info.get("exif")

        # ICC 색상 프로파일 추출
        icc_profile = image.info.get("icc_profile")

        # 저장 - 핵심 품질 옵션
        save_kwargs = {
            "format": "JPEG",
            "quality": quality,
            "subsampling": 1,  # 4:4:4 - 크로마 서브샘플링 없음
            "optimize": True,
            "progressive": True,
        }
        if exif_data:
            save_kwargs["exif"] = exif_data
        if icc_profile:
            save_kwargs["icc_profile"] = icc_profile

        return save_kwargs

    def _save_image(
        self,
        src_file: Path,
        tgt_file: Path,
        quality: int,
        resize_config: ResizeConfig,
    ) -> None:
        # 파일 타임스탬프 보존
        stat = src_file.stat()
        # 저장
        self._run_image_save(src_file, tgt_file, quality, resize_config)

        os.utime(tgt_file, (stat.st_atime, stat.st_mtime))

    def _run_image_save(
        self,
        src_file: Path | bytes,
        tgt_file: Path,
        quality: int,
        resize_config: ResizeConfig,
    ) -> None:
        # 이미지 취득
        if isinstance(src_file, Path):
            image = Image.open(src_file)
        else:
            image = Image.open(BytesIO(src_file))

        # RGB 변환 (JPEG는 알파채널 미지원)
        if image.mode == "RGB":
            image2 = image.convert("RGB")
        elif image.mode == "RGBA":
            background = Image.new("RGB", image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[3])
            image2 = background
        else:
            raise ValueError("Unsupported image mode")

        # 리사이징 (설정이 있으면 적용)
        if resize_config.use_resize:
            image2 = self._resize_image(image2, resize_config)

        # 저장
        save_kwargs = self._create_save_kwargs(image, quality)
        image2.save(tgt_file, **save_kwargs)

    def _resize_image(
        self, image: Image.Image, resize_config: ResizeConfig
    ) -> Image.Image:
        """이미지 리사이징
        - ratio: 축소 비율을 가로세로에 동일하게 적용 (0.5 = 50%)
        - long_side_length: 이미지의 긴 쪽(가로/세로 중)을 기준으로 리사이징 (비율 유지)
        """
        original_width, original_height = image.size
        aspect_ratio = original_width / original_height

        if resize_config.mode == ResizeMode.FIXED:
            # 긴 쪽을 기준으로 리사이징
            if original_width >= original_height:
                new_width = min(resize_config.long_side_length or 10**5, original_width)
                new_height = int(new_width / aspect_ratio)
            else:
                new_height = min(
                    resize_config.long_side_length or 10**5, original_height
                )
                new_width = int(new_height * aspect_ratio)

            new_size = (new_width, new_height)
            return image.resize(new_size, Image.Resampling.LANCZOS)

        elif resize_config.mode == ResizeMode.RATIO:
            # 비율 축소: 가로세로 모두 동일하게 적용
            new_width = int(original_width * (resize_config.ratio or 1.0))
            new_height = int(original_height * (resize_config.ratio or 1.0))
            new_size = (new_width, new_height)
            return image.resize(new_size, Image.Resampling.LANCZOS)

        return image

    def _create_output_filename(self, path: Path, quality: int) -> Path:
        """출력 파일명 생성 (quality suffix 포함)
        출력 파일명: IMG001.heic → IMG001_q85.jpg"""
        return path.parent / f"{path.stem}_q{quality}.jpg"


image_format_converter = ImageFormatConverter()
