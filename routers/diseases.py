from fastapi import APIRouter, HTTPException
from schemas import CropOut, DiseaseOut, MedicineOut
from services.disease_service import CROPS, build_disease_info

router = APIRouter(prefix="/diseases", tags=["diseases"])

# Pre-built disease library keyed by crop
_DISEASE_LIBRARY = {
    "tomato": [
        ("Tomato___Late_blight", "Tomato", "Inyanya"),
        ("Tomato___Early_blight", "Tomato", "Inyanya"),
        ("Tomato___Bacterial_spot", "Tomato", "Inyanya"),
        ("Tomato___Leaf_Mold", "Tomato", "Inyanya"),
        ("Tomato___Tomato_mosaic_virus", "Tomato", "Inyanya"),
        ("Tomato___Septoria_leaf_spot", "Tomato", "Inyanya"),
        ("Tomato___Tomato_Yellow_Leaf_Curl_Virus", "Tomato", "Inyanya"),
        ("Tomato___Spider_mites_Two-spotted_spider_mite", "Tomato", "Inyanya"),
        ("Tomato___Target_Spot", "Tomato", "Inyanya"),
    ],
    "potato": [
        ("Potato___Late_blight", "Potato", "Ibirayi"),
        ("Potato___Early_blight", "Potato", "Ibirayi"),
    ],
    "maize": [
        ("Corn_maize___Cercospora_leaf_spot_Gray_leaf_spot", "Maize", "Ibigori"),
        ("Corn_maize___Common_rust_", "Maize", "Ibigori"),
        ("Corn_maize___Northern_Leaf_Blight", "Maize", "Ibigori"),
    ],
    "pepper": [
        ("Pepper_bell___Bacterial_spot", "Pepper", "Urusenda"),
    ],
    "banana": [
        ("Banana___Black_Sigatoka", "Banana", "Igitoki"),
        ("Banana___Xanthomonas_Wilt_BXW", "Banana", "Igitoki"),
        ("Banana___Panama_Disease_Fusarium", "Banana", "Igitoki"),
    ],
    "cassava": [
        ("Cassava___Mosaic_Disease_CMD", "Cassava", "Imyumbati"),
        ("Cassava___Brown_Streak_CBSD", "Cassava", "Imyumbati"),
    ],
    "bean": [
        ("Bean___Angular_Leaf_Spot", "Bean", "Ibishyimbo"),
        ("Bean___Common_Rust", "Bean", "Ibishyimbo"),
    ],
    "coffee": [
        ("Coffee___Leaf_Rust_CLR", "Coffee", "Ikawa"),
        ("Coffee___Coffee_Berry_Disease_CBD", "Coffee", "Ikawa"),
        ("Coffee___Coffee_Wilt", "Coffee", "Ikawa"),
    ],
    "avocado": [
        ("Avocado___Root_Rot_Phytophthora", "Avocado", "Avoka"),
        ("Avocado___Anthracnose", "Avocado", "Avoka"),
    ],
    "strawberry": [
        ("Strawberry___Leaf_scorch", "Strawberry", "Frazi"),
        ("Strawberry___Gray_Mold_Botrytis", "Strawberry", "Frazi"),
    ],
}


def _disease_raw(full_id: str) -> str:
    parts = full_id.split("___")
    return parts[1] if len(parts) > 1 else full_id


@router.get("/crops", response_model=list[CropOut])
async def list_crops():
    return [CropOut(**c) for c in CROPS]


@router.get("/crops/{crop_id}", response_model=CropOut)
async def get_crop(crop_id: str):
    for c in CROPS:
        if c["id"] == crop_id:
            return CropOut(**c)
    raise HTTPException(status_code=404, detail="Crop not found")


@router.get("/", response_model=list[DiseaseOut])
async def list_diseases(crop_id: str | None = None):
    results = []
    library = _DISEASE_LIBRARY
    if crop_id:
        library = {crop_id: _DISEASE_LIBRARY.get(crop_id, [])}

    for c_id, diseases in library.items():
        for (full_id, crop_en, crop_kiny) in diseases:
            raw = _disease_raw(full_id)
            info = build_disease_info(c_id, crop_en, crop_kiny, raw)
            results.append(DiseaseOut(
                id=info["id"],
                crop_id=info["crop_id"],
                name_en=info["name_en"],
                name_kiny=info["name_kiny"],
                cause_en=info["cause_en"],
                cause_kiny=info["cause_kiny"],
                signs_en=info["signs_en"],
                signs_kiny=info["signs_kiny"],
                prevention_en=info["prevention_en"],
                prevention_kiny=info["prevention_kiny"],
                medicines=[MedicineOut(**m) for m in info["medicines"]],
            ))
    return results


@router.get("/{disease_id}", response_model=DiseaseOut)
async def get_disease(disease_id: str):
    for c_id, diseases in _DISEASE_LIBRARY.items():
        for (crop_en, crop_kiny) in [(d[1], d[2]) for d in diseases]:
            for full_id, cen, ckiny in diseases:
                if _disease_raw(full_id) in disease_id or disease_id in full_id:
                    raw = _disease_raw(full_id)
                    info = build_disease_info(c_id, cen, ckiny, raw)
                    return DiseaseOut(
                        id=info["id"], crop_id=info["crop_id"],
                        name_en=info["name_en"], name_kiny=info["name_kiny"],
                        cause_en=info["cause_en"], cause_kiny=info["cause_kiny"],
                        signs_en=info["signs_en"], signs_kiny=info["signs_kiny"],
                        prevention_en=info["prevention_en"], prevention_kiny=info["prevention_kiny"],
                        medicines=[MedicineOut(**m) for m in info["medicines"]],
                    )
    raise HTTPException(status_code=404, detail="Disease not found")
