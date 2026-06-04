from fastapi import APIRouter, File, HTTPException, Request, UploadFile, status, Depends
from utils.enum import UserRole
from middleware.auth import require_roles
from domain.service.image_service import ImageService
from schema.upload_schema import ImageDeleteResponse, ImageUploadResponse


router = APIRouter(prefix="/images", tags=["Image Management"])


@router.post("", response_model=ImageUploadResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_roles(UserRole.CLIENT, UserRole.EMPLOYEE, UserRole.ADMIN))])
def upload_image(request: Request, file: UploadFile = File(...)):
    try:
        base_url = str(request.base_url)
        result = ImageService.save_upload(file=file, base_url=base_url)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return ImageUploadResponse(**result)

@router.delete("", response_model=ImageDeleteResponse, dependencies=[Depends(require_roles(UserRole.ADMIN))])
def delete_image(img_url: str):
    try:
        result = ImageService.delete_by_url(img_url)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return ImageDeleteResponse(**result)
