from typing import List
from fastapi import APIRouter, HTTPException
from core.config import settings, Zone
from schemas.zone import ZoneResponse, ZoneCreate

router = APIRouter(prefix="/api/zones", tags=["zones"])


@router.get("")
async def list_zones() -> List[ZoneResponse]:
    """설정된 모든 zone 반환"""
    return [
        ZoneResponse(
            id=z.id,
            label=z.label,
            description=z.description,
            quality=z.quality,
            color=z.color,
            resize=z.resize,
        )
        for z in settings.zones
    ]


@router.post("")
async def create_zone(zone_data: ZoneCreate) -> ZoneResponse:
    """새로운 zone 생성 및 config.json에 저장"""
    # 중복된 id 체크
    if any(z.id == zone_data.id for z in settings.zones):
        raise HTTPException(
            status_code=400, detail=f"Zone with id '{zone_data.id}' already exists"
        )

    # 새로운 zone 생성
    new_zone = Zone(
        id=zone_data.id,
        label=zone_data.label,
        description=zone_data.description,
        quality=zone_data.quality,
        color=zone_data.color,
        resize=zone_data.resize,
    )

    # settings에 추가
    settings.zones.append(new_zone)

    # config.json에 저장
    settings.save()

    return ZoneResponse(
        id=new_zone.id,
        label=new_zone.label,
        description=new_zone.description,
        quality=new_zone.quality,
        color=new_zone.color,
        resize=new_zone.resize,
    )


@router.put("/{zone_id}")
async def update_zone(zone_id: str, zone_data: ZoneCreate) -> ZoneResponse:
    """zone 업데이트 및 config.json에 저장"""
    # zone 찾기
    zone = next((z for z in settings.zones if z.id == zone_id), None)
    if not zone:
        raise HTTPException(status_code=404, detail=f"Zone not found: {zone_id}")

    # zone 업데이트
    zone.label = zone_data.label
    zone.description = zone_data.description
    zone.quality = zone_data.quality
    zone.color = zone_data.color
    zone.resize = zone_data.resize

    # config.json에 저장
    settings.save()

    return ZoneResponse(
        id=zone.id,
        label=zone.label,
        description=zone.description,
        quality=zone.quality,
        color=zone.color,
        resize=zone.resize,
    )


@router.delete("/{zone_id}")
async def delete_zone(zone_id: str) -> dict:
    """zone 삭제 및 config.json에 저장"""
    # zone 찾기
    zone = next((z for z in settings.zones if z.id == zone_id), None)
    if not zone:
        raise HTTPException(status_code=404, detail=f"Zone not found: {zone_id}")

    # zone 삭제
    settings.zones = [z for z in settings.zones if z.id != zone_id]

    # config.json에 저장
    settings.save()

    return {"message": f"Zone '{zone_id}' deleted successfully"}
