"""
Disease and crop knowledge base. Ported from mobile ai_service.dart.
Used by /scan/upload to build full disease info from AI model output.
"""
from typing import Optional

# ── Crop mappings ────────────────────────────────────────────────

CROP_MAP = {
    "Tomato": ("tomato", "Tomato", "Inyanya"),
    "Potato": ("potato", "Potato", "Ibirayi"),
    "Corn": ("maize", "Maize", "Ibigori"),
    "Pepper": ("pepper", "Pepper", "Urusenda"),
    "Banana": ("banana", "Banana", "Igitoki"),
    "Cassava": ("cassava", "Cassava", "Imyumbati"),
    "Bean": ("bean", "Bean", "Ibishyimbo"),
    "Coffee": ("coffee", "Coffee", "Ikawa"),
    "Avocado": ("avocado", "Avocado", "Avoka"),
    "PassionFruit": ("passion", "Passion Fruit", "Marakooza"),
    "SweetPotato": ("sweetpotato", "Sweet Potato", "Ibijumba"),
    "Cabbage": ("cabbage", "Cabbage", "Ikabeji"),
    "Sorghum": ("sorghum", "Sorghum", "Amasaka"),
    "Strawberry": ("strawberry", "Strawberry", "Frazi"),
    "Mango": ("mango", "Mango", "Mango"),
    "Pineapple": ("pineapple", "Pineapple", "Ananasi"),
    "Papaya": ("papaya", "Papaya", "Ipapayi"),
    "Orange": ("orange", "Orange", "Oranje"),
}


def get_crop_info(raw: str):
    """Returns (crop_id, crop_en, crop_kiny) from a model crop_raw or filter key."""
    if raw in CROP_MAP:
        return CROP_MAP[raw]
    if "Tomato" in raw:
        return ("tomato", "Tomato", "Inyanya")
    if "Potato" in raw:
        return ("potato", "Potato", "Ibirayi")
    if "Corn" in raw or "maize" in raw.lower():
        return ("maize", "Maize", "Ibigori")
    if "Pepper" in raw:
        return ("pepper", "Pepper", "Urusenda")
    return ("unknown", raw, raw)


# ── Disease name (Kinyarwanda) ────────────────────────────────────

def disease_name_kiny(disease: str) -> str:
    d = disease.lower()
    if "late_blight" in d:       return "Ubunyonga bwihutirwa"
    if "early_blight" in d:      return "Ubunyonga bwungirije"
    if "bacterial_spot" in d:    return "Amababi areha bagiteri"
    if "leaf_mold" in d:         return "Ubutwa bw'amababi"
    if "mosaic" in d or "cmd" in d: return "Indwara y'amabara atandukanye"
    if "brown_streak" in d:      return "Indwara ya Brown Streak"
    if "rust" in d:              return "Indimu"
    if "septoria" in d:          return "Amababi y'uduce duto"
    if "yellow_leaf_curl" in d or "curl" in d: return "Amababi agunyuza umuhondo"
    if "spider_mite" in d:       return "Udukoko dw'ubunyovu"
    if "target_spot" in d:       return "Amababi y'inzira"
    if "northern_leaf_blight" in d: return "Ubunyonga bw'amababi y'ibigori"
    if "gray_leaf_spot" in d or "cercospora" in d: return "Amababi y'ibigori gris"
    if "sigatoka" in d:          return "Indwara ya Sigatoka"
    if "xanthomonas" in d or "bxw" in d: return "Ubwandu bwa Xanthomonas (BXW)"
    if "panama" in d or "fusarium" in d: return "Indwara ya Panama"
    if "anthracnose" in d:       return "Indwara ya Anthracnose"
    if "root_rot" in d or "phytophthora" in d: return "Indwara y'Imizi"
    if "woodiness" in d:         return "Indwara ya Woodiness"
    if "coffee_berry" in d or "cbd" in d: return "Indwara y'Imbuto z'Ikawa"
    if "coffee_wilt" in d:       return "Indwara ya Tracheomycosis y'Ikawa"
    if "angular_leaf_spot" in d: return "Amababi y'Angular Spot"
    if "powdery_mildew" in d:    return "Ubutwa bw'Ufu"
    if "downy_mildew" in d:      return "Ubutwa bw'Amazi"
    if "leaf_scorch" in d:       return "Amababi avunika"
    if "gray_mold" in d or "botrytis" in d: return "Ubutwa gris"
    if "black_rot" in d:         return "Ubora bw'Umukara"
    return "Indwara"


# ── Cause ─────────────────────────────────────────────────────────

def get_cause(disease: str, lang: str) -> str:
    d = disease.lower()
    en = _cause_en(d)
    if lang == "en":
        return en
    return _cause_kiny(d)


def _cause_en(d: str) -> str:
    if "late_blight" in d:       return "Caused by Phytophthora infestans. Spreads fast in wet, cool weather."
    if "early_blight" in d:      return "Caused by Alternaria solani fungus. Favored by warm, humid conditions."
    if "bacterial_spot" in d:    return "Caused by Xanthomonas bacteria. Spreads through rain splash and tools."
    if "leaf_mold" in d:         return "Caused by Passalora fulva fungus. Common in humid conditions."
    if "mosaic" in d or "cmd" in d: return "Caused by Mosaic Virus. Spread by whitefly insects and infected plant material."
    if "brown_streak" in d:      return "Caused by Cassava Brown Streak Virus. Spread by whiteflies."
    if "rust" in d:              return "Caused by Puccinia or Hemileia fungus. Spreads through wind-borne spores."
    if "septoria" in d:          return "Caused by Septoria lycopersici fungus. Spreads in wet conditions."
    if "yellow_leaf_curl" in d or "curl" in d: return "Caused by Yellow Leaf Curl Virus. Spread by whiteflies."
    if "spider_mite" in d:       return "Caused by Tetranychus urticae mites. Thrives in hot, dry weather."
    if "target_spot" in d:       return "Caused by Corynespora cassiicola fungus."
    if "northern_leaf_blight" in d: return "Caused by Exserohilum turcicum fungus. Spreads in cool, wet conditions."
    if "gray_leaf_spot" in d or "cercospora" in d: return "Caused by Cercospora zeae-maydis. Spreads in humid weather."
    if "sigatoka" in d:          return "Caused by Mycosphaerella fijiensis fungus. Spreads through wind and rain."
    if "xanthomonas" in d or "bxw" in d: return "Caused by Xanthomonas campestris bacteria. Spread by infected tools and insects."
    if "panama" in d or "fusarium" in d: return "Caused by Fusarium oxysporum in the soil. Enters through roots."
    if "anthracnose" in d:       return "Caused by Colletotrichum gloeosporioides fungus. Spreads in warm, wet weather."
    if "root_rot" in d or "phytophthora" in d: return "Caused by Phytophthora cinnamomi. Thrives in waterlogged soils."
    if "woodiness" in d:         return "Caused by Passion Fruit Woodiness Virus. Spread by aphid insects."
    if "coffee_berry" in d or "cbd" in d: return "Caused by Colletotrichum kahawae. Infects coffee berries during wet seasons."
    if "coffee_wilt" in d:       return "Caused by Gibberella xylarioides. Spreads through soil and infected material."
    if "angular_leaf_spot" in d: return "Caused by Phaeoisariopsis griseola. Spreads in warm, humid conditions."
    if "powdery_mildew" in d:    return "Caused by powdery mildew fungi. Thrives in warm, dry days with humid nights."
    if "downy_mildew" in d:      return "Caused by Peronospora fungi. Spreads in cool, wet conditions."
    if "leaf_scorch" in d:       return "Caused by Diplocarpon earliana. Spreads in wet weather."
    if "gray_mold" in d or "botrytis" in d: return "Caused by Botrytis cinerea. Spreads in cool, humid conditions."
    if "black_rot" in d:         return "Caused by Xanthomonas campestris. Enters through leaf margins in wet weather."
    return "Fungal or bacterial infection. Spreads in humid conditions."


def _cause_kiny(d: str) -> str:
    if "late_blight" in d:       return "Ubwandu bwatewe na Phytophthora infestans. Ikwira vuba igihe cy'imvura n'ubukonje."
    if "early_blight" in d:      return "Ubwandu bwatewe na Alternaria solani. Ikwira mu bihe bishyushye n'umwizero."
    if "bacterial_spot" in d:    return "Ubwandu bwatewe na bagiteri Xanthomonas. Ikwira n'imvura no gukoresha ibikoresho."
    if "leaf_mold" in d:         return "Ubwandu bwatewe na Passalora fulva. Ikwira mu bihe by'umwizero."
    if "mosaic" in d or "cmd" in d: return "Ubwandu bwatewe na virusi ya Mosaic. Ikwira n'insekta no gukoraho."
    if "brown_streak" in d:      return "Ubwandu bwatewe na Cassava Brown Streak Virus. Ikwira n'inzuki zera."
    if "rust" in d:              return "Ubwandu bwatewe na ubutwa. Ikwira n'umuyaga."
    if "septoria" in d:          return "Ubwandu bwatewe na Septoria. Ikwira mu bihe by'imvura."
    if "yellow_leaf_curl" in d or "curl" in d: return "Ubwandu bwatewe na virusi ikwira n'inzuki zera."
    if "spider_mite" in d:       return "Ubwandu bwatewe na udukoko Tetranychus. Ukunda igihe cishyushye."
    if "northern_leaf_blight" in d: return "Ubwandu bwatewe na Exserohilum turcicum. Ikwira igihe cy'imvura."
    if "gray_leaf_spot" in d or "cercospora" in d: return "Ubwandu bwatewe na Cercospora. Ikwira mu bihe by'umwizero."
    if "sigatoka" in d:          return "Ubwandu bwatewe na Mycosphaerella fijiensis. Ikwira n'umuyaga n'imvura."
    if "xanthomonas" in d or "bxw" in d: return "Ubwandu bwatewe na bagiteri Xanthomonas. Ikwira n'ibikoresho bisharaguwe."
    if "anthracnose" in d:       return "Ubwandu bwatewe na Colletotrichum. Ikwira mu bihe bishyushye by'imvura."
    if "root_rot" in d or "phytophthora" in d: return "Ubwandu bwatewe na Phytophthora. Gukura mu butaka budafite uburyo bwiza bwo kumena amazi."
    if "woodiness" in d:         return "Ubwandu bwatewe na virusi ya Woodiness. Ikwira n'udukoko dwa nyengeri."
    if "coffee_berry" in d or "cbd" in d: return "Ubwandu bwatewe na Colletotrichum kahawae. Bwica imbuto z'ikawa mu gihe cy'imvura."
    if "powdery_mildew" in d:    return "Ubwandu bwatewe na ubutwa bw'ufu. Ukunda igihe gishyushye cy'umucanga."
    if "downy_mildew" in d:      return "Ubwandu bwatewe na ubutwa bw'amazi. Ikwira mu bihe bikonje by'umwizero."
    return "Ubwandu bwatewe na ubutwa cyangwa bagiteri. Ikwira mu bihe by'umwizero."


# ── Signs ─────────────────────────────────────────────────────────

def get_signs(disease: str, lang: str) -> str:
    d = disease.lower()
    if lang == "en":
        return _signs_en(d)
    return _signs_kiny(d)


def _signs_en(d: str) -> str:
    if "late_blight" in d:       return "Dark brown spots on leaves with yellow edges. Plants collapse quickly in wet weather."
    if "early_blight" in d:      return "Dark spots with yellow rings on lower leaves. Leaves turn yellow and drop."
    if "bacterial_spot" in d:    return "Small, dark water-soaked spots on leaves and fruit. Spots may have yellow halos."
    if "leaf_mold" in d:         return "Yellow spots on upper leaf surface. Olive-green mold on underside."
    if "mosaic" in d or "cmd" in d: return "Distorted, mosaic-patterned leaves (yellow-green patches). Stunted growth."
    if "brown_streak" in d:      return "Yellow streaks on leaves. Brown necrotic patches inside tubers. Root becomes inedible."
    if "rust" in d:              return "Small reddish-brown pustules on leaves. Leaves turn yellow then brown."
    if "septoria" in d:          return "Small circular spots with grey centers on leaves. Leaves yellow and fall off."
    if "yellow_leaf_curl" in d or "curl" in d: return "Leaves curl upward and turn yellow. Plants stunted. Fruit production drops."
    if "spider_mite" in d:       return "Tiny yellow or white spots on leaves. Fine webbing visible under leaves."
    if "target_spot" in d:       return "Circular spots with concentric rings on leaves. Leaves drop prematurely."
    if "northern_leaf_blight" in d: return "Long grey-green lesions on maize leaves. Leaves die from tip downward."
    if "gray_leaf_spot" in d or "cercospora" in d: return "Small rectangular grey spots on maize leaves. Leaves dry out."
    if "sigatoka" in d:          return "Yellow streaks and spots on banana leaves. Leaves turn brown. Premature fruit ripening."
    if "xanthomonas" in d or "bxw" in d: return "Yellowing and wilting of entire plant. Internal stem browning. Fruit rots unripe."
    if "panama" in d or "fusarium" in d: return "Leaves turn yellow from outer inward. Internal stem shows brown streaks. Plant collapses."
    if "anthracnose" in d:       return "Dark sunken lesions on fruit skin. Black spots on leaves and twigs. Fruit rots."
    if "root_rot" in d or "phytophthora" in d: return "Yellowing leaves and wilting. Small, blackened feeder roots. Tree declines gradually."
    if "woodiness" in d:         return "Leaves become wrinkled, mottled. Fruit becomes hard and woody. Reduced juice."
    if "coffee_berry" in d or "cbd" in d: return "Dark sunken spots on green coffee berries. Berries shrivel and drop."
    if "coffee_wilt" in d:       return "Sudden wilting of coffee branches. Dark streaks inside the stem."
    if "angular_leaf_spot" in d: return "Angular water-soaked spots on leaves. Pods show dark brown sunken lesions."
    if "powdery_mildew" in d:    return "White powdery coating on leaves, stems, and buds. Parts turn yellow and dry."
    if "downy_mildew" in d:      return "Yellow patches on upper leaf surface. Grey-purple mold on underside."
    if "leaf_scorch" in d:       return "Irregular purple-red spots on leaves. Leaves dry from edges inward."
    if "gray_mold" in d or "botrytis" in d: return "Grey fuzzy mold on fruit, flowers, and leaves. Fruit rots quickly."
    if "black_rot" in d:         return "V-shaped yellow lesions on leaf edges. Leaf veins turn black. Leaves drop."
    return "Spots, discoloration or abnormal growth on leaves or fruit."


def _signs_kiny(d: str) -> str:
    if "late_blight" in d:       return "Amababi afite amabara y'umukara-rusingo. Ibihingwa birangirira vuba mu gihe cy'imvura."
    if "early_blight" in d:      return "Amababi y'hasi yirabura afite inzira y'umuhondo. Amababi ayimuka aragwa."
    if "bacterial_spot" in d:    return "Uduce duto dwirabura ku mababi no ku biribwa. Harimo umuhondo urehereje."
    if "mosaic" in d or "cmd" in d: return "Amababi afite amabara atandukanye y'umuhondo n'icyatsi. Igihingwa gikura bike."
    if "brown_streak" in d:      return "Amababi afite imirongo y'umuhondo. Imizi inakeraho imbere."
    if "rust" in d:              return "Uduce duto dw'umutuku-rusingo ku mababi. Amababi agenda anyabanyaba."
    if "yellow_leaf_curl" in d or "curl" in d: return "Amababi agunyuza hejuru kandi anyabanyaba. Igihingwa gikura bike."
    if "spider_mite" in d:       return "Uduce duto dw'umuhondo ku mababi. Umunyuzi muto hasi y'amababi."
    if "northern_leaf_blight" in d: return "Amababi y'ibigori afite imirongo mirenze. Amababi agaba uhereye hejuru."
    if "gray_leaf_spot" in d or "cercospora" in d: return "Uduce duto dusize gris ku mababi y'ibigori. Amababi ayuma."
    if "sigatoka" in d:          return "Amababi y'igitoki anyabanyaba. Imbuto zivuka mbere y'igihe."
    if "xanthomonas" in d or "bxw" in d: return "Igitoki cyose kigaragara nabi. Imbere y'umutwe wirabura. Imbuto ziriya mbere y'igihe."
    if "anthracnose" in d:       return "Amababi n'imbuto bifite amakiringirane y'umukara. Imbuto ziriya vuba."
    if "root_rot" in d or "phytophthora" in d: return "Amababi anyabanyaba. Imizi yirabura. Igihingwa cyarangirira."
    if "woodiness" in d:         return "Amababi agunyuka kandi afite amabara atandukanye. Imbuto zihinduka z'umuhimu."
    if "powdery_mildew" in d:    return "Ufu urashe ku mababi no ku mashami. Amababi anyabanyaba kandi anyuma."
    if "downy_mildew" in d:      return "Amababi yiziwa haruguru. Ubutwa bw'amabara gris hasi. Amababi agunyuka."
    if "black_rot" in d:         return "Amababi afite amabara y'umuhondo ku nkuru. Imirongo y'amababi irahinduka umukara."
    return "Amababi afite amabara atandukanye cyangwa igihingwa kigaragara nabi."


# ── Prevention ────────────────────────────────────────────────────

def get_prevention(disease: str, lang: str) -> str:
    d = disease.lower()
    if lang == "en":
        return _prevention_en(d)
    return _prevention_kiny(d)


def _prevention_en(d: str) -> str:
    if "late_blight" in d or "early_blight" in d:
        return "Use certified seeds. Avoid overhead watering. Remove infected leaves. Rotate crops each season."
    if "bacterial" in d:
        return "Use disease-free seeds. Avoid working with wet plants. Disinfect tools between plants."
    if "mosaic" in d or "virus" in d or "curl" in d or "cmd" in d:
        return "Control whiteflies with insecticide. Remove and burn infected plants. Wash hands before handling plants."
    if "rust" in d:
        return "Plant resistant varieties. Scout fields early. Remove infected leaves. Apply fungicide at first sign."
    if "septoria" in d:
        return "Remove lower infected leaves. Avoid wetting foliage. Rotate crops."
    if "spider_mite" in d:
        return "Keep plants well-watered. Remove heavily infested leaves. Use miticide spray."
    if "northern_leaf_blight" in d or "gray_leaf_spot" in d or "cercospora" in d:
        return "Plant resistant maize varieties. Rotate crops. Avoid overhead watering."
    if "sigatoka" in d:
        return "Remove and destroy infected leaves. Improve drainage. Apply copper-based fungicide."
    if "xanthomonas" in d or "bxw" in d:
        return "Remove and burn infected plants immediately. Disinfect tools with bleach. Use clean planting material."
    if "panama" in d or "fusarium" in d:
        return "Use resistant varieties. Avoid moving soil from infected areas. Plant in well-drained soil."
    if "anthracnose" in d:
        return "Apply copper fungicide at flowering. Handle fruit carefully. Remove fallen infected material."
    if "root_rot" in d or "phytophthora" in d:
        return "Improve soil drainage. Avoid overwatering. Apply Phosphonate fungicide. Plant on raised beds."
    if "woodiness" in d:
        return "Control aphids with insecticide. Remove and burn infected plants. Use certified virus-free seedlings."
    if "coffee_berry" in d or "cbd" in d:
        return "Spray copper fungicide at flower opening. Harvest all ripe berries promptly."
    if "coffee_wilt" in d:
        return "Remove and burn infected trees. Disinfect pruning tools. Use resistant varieties."
    if "powdery_mildew" in d:
        return "Apply sulfur or potassium bicarbonate. Improve air circulation. Remove infected plant parts."
    if "downy_mildew" in d or "black_rot" in d:
        return "Apply copper-based fungicide. Improve drainage. Avoid overhead watering."
    return "Use certified seeds. Practice crop rotation. Remove infected plant material."


def _prevention_kiny(d: str) -> str:
    if "late_blight" in d or "early_blight" in d:
        return "Koresha imbuto zemewe. Irinda gusuka amazi haruguru. Vana amababi arwaye vuba. Hindura imyaka."
    if "bacterial" in d:
        return "Koresha imbuto zidafite ubwandu. Irinda gukora ibihingwa bishyize. Oza ibikoresho byawe."
    if "mosaic" in d or "virus" in d or "curl" in d:
        return "Kurwanya inzuki n'insekta n'insecticide. Vana ibihingwa birwaye ubishe. Oga intoki mbere yo gukorana."
    if "rust" in d:
        return "Koresha indimu zikumira indwara. Vana amababi arwaye. Soma vuba."
    if "sigatoka" in d:
        return "Vana amababi arwaye ubishe. Ungura amazi neza. Suka imiti ya shaba."
    if "xanthomonas" in d or "bxw" in d:
        return "Vana ibihingwa birwaye vuba ubishe. Oza ibikoresho na bleach. Koresha imikono itanduye."
    if "anthracnose" in d:
        return "Suka imiti ya shaba ibimera bifunguka. Kora neza imbuto. Bika mu bihe bikonje."
    if "root_rot" in d or "phytophthora" in d:
        return "Ungura amazi neza. Irinda gusuka cyane. Hinga ku butaka buzamutse."
    if "woodiness" in d:
        return "Kurwanya udukoko dwa nyengeri n'insecticide. Vana ibihingwa birwaye vuba."
    if "powdery_mildew" in d:
        return "Suka sulfuri cyangwa imiti ya bicarbonate. Ungura umwuka neza. Vana ibice birwaye."
    return "Koresha imbuto zemewe. Hindura imyaka. Vana ibihingwa birwaye."


# ── Medicine ──────────────────────────────────────────────────────

def get_medicines(disease: str) -> list:
    d = disease.lower()
    if "late_blight" in d:
        return [{"name": "Ridomil Gold MZ 68WG", "dosage_en": "25g per 20L water",
                 "dosage_kiny": "25g mu ntebe y'amazi (20L)",
                 "how_to_use_en": "Spray every 7–14 days during rainy season.",
                 "how_to_use_kiny": "Suka buri nshuro 7-14 mu gihe cy'imvura.",
                 "price_est": "2,000 – 4,500 RWF"}]
    if "early_blight" in d:
        return [{"name": "Mancozeb 80WP", "dosage_en": "30g per 20L water",
                 "dosage_kiny": "30g mu ntebe y'amazi (20L)",
                 "how_to_use_en": "Spray every 7 days. Start before disease appears.",
                 "how_to_use_kiny": "Suka buri ndwi. Tangira mbere y'indwara.",
                 "price_est": "1,500 – 3,000 RWF"}]
    if "bacterial" in d:
        return [{"name": "Copper Oxychloride", "dosage_en": "30g per 20L water",
                 "dosage_kiny": "30g mu ntebe y'amazi (20L)",
                 "how_to_use_en": "Spray every 5–7 days. Cover all plant surfaces.",
                 "how_to_use_kiny": "Suka buri minsi 5-7. Bika igihingwa cyose.",
                 "price_est": "1,000 – 2,500 RWF"}]
    if "rust" in d:
        return [{"name": "Tilt 250 EC", "dosage_en": "10ml per 20L water",
                 "dosage_kiny": "10ml mu ntebe y'amazi (20L)",
                 "how_to_use_en": "Spray at first sign. Repeat after 14 days.",
                 "how_to_use_kiny": "Suka ibimenyetso bya mbere. Subiramo nyuma y'iminsi 14.",
                 "price_est": "3,000 – 5,000 RWF"}]
    if "leaf_mold" in d:
        return [{"name": "Chlorothalonil 75WP", "dosage_en": "20g per 20L water",
                 "dosage_kiny": "20g mu ntebe y'amazi (20L)",
                 "how_to_use_en": "Spray every 7 days. Improve ventilation.",
                 "how_to_use_kiny": "Suka buri ndwi. Fungura imiryango.",
                 "price_est": "1,500 – 3,000 RWF"}]
    if "northern_leaf_blight" in d:
        return [{"name": "Mancozeb 80WP", "dosage_en": "30g per 20L water",
                 "dosage_kiny": "30g mu ntebe y'amazi (20L)",
                 "how_to_use_en": "Spray every 7–10 days.",
                 "how_to_use_kiny": "Suka buri minsi 7-10.",
                 "price_est": "1,500 – 3,000 RWF"}]
    if "gray_leaf_spot" in d or "cercospora" in d:
        return [{"name": "Amistar (Azoxystrobin)", "dosage_en": "10ml per 20L water",
                 "dosage_kiny": "10ml mu ntebe y'amazi (20L)",
                 "how_to_use_en": "Spray at onset. Repeat after 14 days.",
                 "how_to_use_kiny": "Suka indwara itangiriye. Subiramo nyuma y'iminsi 14.",
                 "price_est": "3,000 – 6,000 RWF"}]
    if "sigatoka" in d:
        return [{"name": "Copper Oxychloride 50WP", "dosage_en": "40g per 20L water",
                 "dosage_kiny": "40g mu ntebe y'amazi (20L)",
                 "how_to_use_en": "Spray every 14 days. Focus on leaf undersides.",
                 "how_to_use_kiny": "Suka buri ibyumweru bibiri. Bitera hasi y'amababi.",
                 "price_est": "1,500 – 3,500 RWF"}]
    if "xanthomonas" in d or "bxw" in d:
        return [{"name": "No chemical cure — Remove infected plant",
                 "dosage_en": "Cut plant at soil level. Burn all parts.",
                 "dosage_kiny": "Tema igihingwa mu butaka. Bisha byose.",
                 "how_to_use_en": "Sterilize tools in 1:10 bleach solution after cutting each plant.",
                 "how_to_use_kiny": "Oza ibikoresho mu masugi ya bleach (1:10) nyuma yo gutera buri gihingwa.",
                 "price_est": "Ubufasha bw'ubuhinzi"}]
    if "rust" in d or "coffee_rust" in d:
        return [{"name": "Copper Oxychloride / Bayleton", "dosage_en": "30g per 20L water",
                 "dosage_kiny": "30g mu ntebe y'amazi (20L)",
                 "how_to_use_en": "Spray at start of rainy season. Repeat every 3 weeks.",
                 "how_to_use_kiny": "Suka intangiriro y'imvura. Subiramo buri ibyumweru 3.",
                 "price_est": "2,000 – 5,000 RWF"}]
    if "coffee_berry" in d or "cbd" in d:
        return [{"name": "Copper Oxychloride 50WP", "dosage_en": "40g per 20L water",
                 "dosage_kiny": "40g mu ntebe y'amazi (20L)",
                 "how_to_use_en": "Spray at 50% flower opening. Repeat every 2 weeks during rains.",
                 "how_to_use_kiny": "Suka ibimera bifunguka igice. Subiramo buri ibyumweru 2.",
                 "price_est": "1,500 – 3,500 RWF"}]
    if "spider_mite" in d:
        return [{"name": "Abamectin 1.8 EC", "dosage_en": "5ml per 20L water",
                 "dosage_kiny": "5ml mu ntebe y'amazi (20L)",
                 "how_to_use_en": "Spray on leaf undersides. Repeat after 7 days.",
                 "how_to_use_kiny": "Suka hasi y'amababi. Subiramo nyuma y'iminsi 7.",
                 "price_est": "2,000 – 4,000 RWF"}]
    if "powdery_mildew" in d:
        return [{"name": "Sulfur 80WP", "dosage_en": "30g per 20L water",
                 "dosage_kiny": "30g mu ntebe y'amazi (20L)",
                 "how_to_use_en": "Spray weekly. Do not apply in hot sun above 30°C.",
                 "how_to_use_kiny": "Suka buri ndwi. Ntusuke mu zuba rishyushye (hejuru ya 30°C).",
                 "price_est": "1,500 – 3,000 RWF"}]
    if "anthracnose" in d or "downy_mildew" in d or "black_rot" in d:
        return [{"name": "Copper Oxychloride 50WP", "dosage_en": "30g per 20L water",
                 "dosage_kiny": "30g mu ntebe y'amazi (20L)",
                 "how_to_use_en": "Spray every 7–10 days. Apply to both leaf sides.",
                 "how_to_use_kiny": "Suka buri minsi 7-10. Suka impande zombi z'amababi.",
                 "price_est": "1,000 – 2,500 RWF"}]
    # Default
    return [{"name": "Consult local agro-dealer",
             "dosage_en": "Ask your nearest agro-shop for advice",
             "dosage_kiny": "Baza agatebo kawe k'ubuhinzi",
             "how_to_use_en": "Describe symptoms and get specific treatment.",
             "how_to_use_kiny": "Sobanura ibimenyetso ubonere imiti ikwiye.",
             "price_est": "1,000 – 5,000 RWF"}]


# ── Main builder ──────────────────────────────────────────────────

def build_disease_info(crop_id: str, crop_en: str, crop_kiny: str, disease_raw: str) -> dict:
    """Build complete disease dict from AI model disease_raw string."""
    name_en = disease_raw.replace("_", " ").replace("-", " ").title()
    return {
        "id": disease_raw,
        "crop_id": crop_id,
        "name_en": f"{crop_en} - {name_en}",
        "name_kiny": f"{crop_kiny} - {disease_name_kiny(disease_raw)}",
        "cause_en": get_cause(disease_raw, "en"),
        "cause_kiny": get_cause(disease_raw, "kiny"),
        "signs_en": get_signs(disease_raw, "en"),
        "signs_kiny": get_signs(disease_raw, "kiny"),
        "prevention_en": get_prevention(disease_raw, "en"),
        "prevention_kiny": get_prevention(disease_raw, "kiny"),
        "medicines": get_medicines(disease_raw),
    }


# ── Static crop/disease library for /diseases/ endpoint ──────────

CROPS = [
    {"id": "tomato", "name_en": "Tomato", "name_kiny": "Inyanya", "emoji": "🍅", "is_active": True},
    {"id": "potato", "name_en": "Potato", "name_kiny": "Ibirayi", "emoji": "🥔", "is_active": True},
    {"id": "maize", "name_en": "Maize", "name_kiny": "Ibigori", "emoji": "🌽", "is_active": True},
    {"id": "pepper", "name_en": "Pepper", "name_kiny": "Urusenda", "emoji": "🫑", "is_active": True},
    {"id": "banana", "name_en": "Banana", "name_kiny": "Igitoki", "emoji": "🍌", "is_active": True},
    {"id": "cassava", "name_en": "Cassava", "name_kiny": "Imyumbati", "emoji": "🌿", "is_active": True},
    {"id": "bean", "name_en": "Bean", "name_kiny": "Ibishyimbo", "emoji": "🫘", "is_active": True},
    {"id": "coffee", "name_en": "Coffee", "name_kiny": "Ikawa", "emoji": "☕", "is_active": True},
    {"id": "avocado", "name_en": "Avocado", "name_kiny": "Avoka", "emoji": "🥑", "is_active": True},
    {"id": "passion", "name_en": "Passion Fruit", "name_kiny": "Marakooza", "emoji": "🟡", "is_active": True},
    {"id": "sweetpotato", "name_en": "Sweet Potato", "name_kiny": "Ibijumba", "emoji": "🍠", "is_active": True},
    {"id": "cabbage", "name_en": "Cabbage", "name_kiny": "Ikabeji", "emoji": "🥬", "is_active": True},
    {"id": "sorghum", "name_en": "Sorghum", "name_kiny": "Amasaka", "emoji": "🌾", "is_active": True},
    {"id": "strawberry", "name_en": "Strawberry", "name_kiny": "Frazi", "emoji": "🍓", "is_active": True},
    {"id": "mango", "name_en": "Mango", "name_kiny": "Mango", "emoji": "🥭", "is_active": True},
]
