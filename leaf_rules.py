"""Fallback for categories with no reviewed rule:
 1) LEAF_RULES: keywords in the LAST TWO breadcrumb levels -> HSN heading (first match wins; order = most specific first)
 2) PRIORS: which chapters are plausible under each top-level Amazon category (stops absurd matches, e.g. stamps for earphones)."""
import re
G = ["women", "womens", "ladies", "girls", "girl"]
LEAF_RULES = [
 (r"movies? &|tv shows|\\bdvds?\\b|blu-?ray|\\bmusic\\b|audio cd|\\bcds?\\b", "8523"),
 (r"cook ?books?", "4901"), (r"shoe ?laces?", "6307"), (r"pill organi[sz]er|pill box", "3924"), (r"gimbal|selfie stick|monopod", "9006"),
 (r"pressure washer", "8424"), (r"coin (set|collect)|collectible coin", "7118"), (r"dart", "9504"), (r"spring", "7320"),
 (r"clamp", "8205"), (r"stapler|staple pin|punches", "8305"), (r"towel (bar|rack|ring|rail)|toilet roll|soap dish|bathroom hardware", "8302"),
 (r"dutch oven|cocotte|casserole|stock pot", "7323"), (r"price ?marker|labels? &|name tag", "4821"), (r"cutting mat", "3926"),
 (r"ponytail|hair (accessor|styling accessor|tie|band|clip)|headband|elastics|scrunch|tiara|\bcombs?\b", "9615"),
 (r"pressure regulator|valve|faucet|\btaps?\b|aerator", "8481"), (r"hamster|exercise wheel|cage|aquarium accessor", "3926"),
 (r"plugs?\b.*(nail|screw|fastener)|oil drain plug", "7318"), (r"leg warmer|socks|hosiery|stockings|tights", "6115"),
 (r"spark plug|ignition", "8511"), (r"pipe fitting|pipe &|plumbing fitting|couplings?", "7307"),
 (r"foam blaster|toy gun|nerf", "9503"), (r"3d printer|3d printing", "8485"), (r"filament", "3916"),
 (r"\bmasks? (and|&)? ?respirator|respirator|face mask", "6307"), (r"scale|weighing", "8423"),
 # electronics
 (r"power ?bank", "8507"), (r"rechargeable batter|li-ion|lithium", "8507"), (r"batter(y|ies)\b", "8506"),
 (r"\bcables?\b|cable assem|usb cable|hdmi|vga|ethernet|coaxial|jack cable|sata|extension cord|electrical wire", "8544"),
 (r"memory card|micro ?sd|flash drive|pen drive|solid state|\bssd\b|hard drive|hard disk", "8523"),
 (r"headphone|headset|earbud|earphone|speaker|microphone|amplifier|soundbar|bluetooth speaker|home audio|car stereo|hi-fi", "8518"),
 (r"security camera|dome camera|bullet camera|dash ?cam|digital camera|video camera|action camera|webcam|camcorder", "8525"),
 (r"camera (case|bag|strap)|lens|tripod|camera accessor", "9006"),
 (r"monitor|television|\btvs?\b|projector", "8528"), (r"\bprinters?\b|print server", "8443"),
 (r"keyboard|\bmice\b|\bmouse\b|laptop|tablet|computers?\b|desktop|graphics card|motherboard|processor", "8471"),
 (r"router|modem|network adapter|wifi|wi-fi|bluetooth adapter|signal booster|telephone|mobile phone|smartphone", "8517"),
 (r"charger|power adapter|power supply|inverter|transformer", "8504"),
 (r"smart ?watch|fitness band|wearable", "8517"), (r"watch strap|watch band", "9113"), (r"wrist watch|\bwatches\b|\bclocks?\b", "9102"),
 (r"led bulb|light bulb|bulbs", "8539"), (r"lamp|lantern|chandelier|ceiling light|night light|lighting|torch|flashlight|headlamp", "9405"),
 (r"\bfans?\b|exhaust fan|cooling fan", "8414"), (r"heater|geyser|\biron\b|hair dryer|straightener|electric kettle|toaster|oven|induction", "8516"),
 (r"refrigerator|freezer", "8418"), (r"washing machine", "8450"), (r"air conditioner", "8415"),
 (r"mixer grinder|blender|juicer|food processor|chopper", "8509"), (r"vacuum cleaner", "8508"), (r"water purifier", "8421"),
 (r"epilator|trimmer|shaver|hair clipper", "8510"), (r"massager", "9019"),
 (r"\bswitch(es)?\b|socket|plug|circuit breaker|\bmcb\b|connector", "8536"),
 # tools & hardware
 (r"screw|bolt|\bnuts?\b|rivet|fastener|threaded insert|spacers", "7318"), (r"padlock", "8301"),
 (r"\bhooks?\b|hinge|door handle|latch|bracket|door closer|curtain rod|drawer pull|cabinet", "8302"),
 (r"wrench|spanner|pliers|screwdriver|socket set", "8204"), (r"hammer", "8205"), (r"\bsaws?\b|saw blade", "8202"),
 (r"drill|power tools|grinder|sander", "8467"), (r"measuring tape|folding rule|\bruler\b", "9017"),
 (r"multimeter|test(er|ers)\b|voltage|thermometer|oscilloscope", "9030"),
 (r"knife|knives|cutter", "8211"), (r"scissor|shears", "8213"), (r"razor|shaving set|blades", "8212"),
 # household
 (r"cookware|pots? &|pan set|pressure cooker|tawa|kadai|utensil", "7323"),
 (r"dinnerware|dinner plate|tea cup|tea cups|crockery|ceramic", "6912"), (r"tumbler|flask|water bottle|canteen|lunch box|container|storage box", "3924"),
 (r"pillow|mattress|cushion cover", "9404"), (r"bedsheet|bed sheet|towel|bath mat|duvet cover|pillow cover", "6302"),
 (r"curtain", "6303"), (r"blanket|quilt", "6301"), (r"\bumbrella", "6601"), (r"\bbrooms?\b|\bmops?\b|duster|brush set|toothbrush|scrubber", "9603"),
 (r"photo frame|picture frame|wall art|artwork|poster|art print", "4911"), (r"candle", "3406"), (r"artificial (flower|plant)", "6702"),
 (r"detergent|cleaner|disinfect|dishwash|floor clean|toilet clean|laundry", "3402"), (r"air freshener|room spray|incense|fragrance", "3307"),
 (r"insect|pest control|repellent|flea|mosquito", "3808"),
 # personal care
 (r"shampoo|conditioner|hair spray|hair gel|hair colou?r|hair oil|hair serum|hair styling", "3305"),
 (r"lipstick|lip gloss|lip balm|\blips\b|make-?up|nail polish|compact|foundation|concealer|eye ?liner|mascara|kajal|blush|face cream|moisturi|serum|sunscreen|skin care|body lotion|face wash|face mask|cream", "3304"),
 (r"perfume|eau de|cologne|body spray|fragrance for", "3303"), (r"deodorant|antiperspirant|talc|after ?shave|shaving cream|hair removal", "3307"),
 (r"soap|body wash|shower gel|hand wash|sanitizer|wipes", "3401"), (r"toothpaste|mouthwash|oral care|dental floss|denture", "3306"),
 (r"bandage|first aid|plaster|gauze|cotton", "3005"), (r"sanitary|pantyliner|diaper|nappy|tampon", "9619"),
 (r"vitamin|supplement|protein|nutrition|omega|probiotic|whey|amino|capsules", "2106"),
 (r"thermometer.*(body|digital)|blood pressure|glucometer|nebuli|oximeter|stethoscope|massage gun", "9018"),
 (r"\bbrace|support|splint|orthop|walking stick|crutch", "9021"),
 # fashion
 (r"sunglasses|safety glasses|goggles|blue ?light", "9004"), (r"eyewear frame|spectacle frame|eyeglass frame|reading glasses", "9003"),
 (r"wallet|handbag|backpack|luggage|duffle|trolley|messenger|sling bag|purse|laptop bag|travel bag|pouch", "4202"),
 (r"jewel+ery|necklace|earring|bangle|bracelet|pendant|\brings?\b|anklet|nose ring|chain|kada|mangalsutra", "7117"),
 (r"hair accessor|hair band|hair clip|scrunch|tiara|\bcomb", "9615"), (r"\bcaps?\b|\bhats?\b|beanie|balaclava", "6505"),
 (r"\bsocks?\b", "6115"), (r"\bgloves?\b", "6116"), (r"\bbelts?\b|suspender", "6217"), (r"swim|bikini|swimsuit", "6112"),
 (r"shoe polish|shoe care|shoe cream", "3405"), (r"shoes?|sneakers|sandals|floaters|clogs|boots|slippers|footwear|flip flop|loafers", "6404"),
 # toys, sports, stationery
 (r"board game|card game|puzzle|jigsaw|brain teaser|video game|gaming|controller|joystick|steering wheel", "9504"),
 (r"toy|doll|playset|figures|action figure|building block|lego|plush|stuffed|model kit|rc car|slime|clay & dough|yo-yo|spinning", "9503"),
 (r"dumbbell|barbell|yoga|exercise|fitness|gym|cricket|badminton|football|tennis|volleyball|basketball|golf|cycling accessor|skate|boxing|swimming|diving|fishing|camping|hiking|sports", "9506"),
 (r"\bpens?\b|ballpoint|rollerball|fountain pen|refills", "9608"), (r"pencil|crayon|marker|highlighter", "9609"),
 (r"notebook|diary|writing pad|notepad|exercise book|sketchbook|planner|journal", "4820"), (r"\bbooks?\b|textbook|literature|humanities|reference", "4901"),
 (r"sticker|label|decal", "4911"), (r"gift wrap|wrapping|streamer|party supplies|balloon|decoration|confetti|banner", "9505"),
 (r"paint|colou?rs|watercolou?r|acrylic", "3213"), (r"glue|adhesive|caulk|sealant|epoxy", "3506"), (r"\btape\b", "3919"),
 (r"guitar|violin|ukulele|drum|synthesi[sz]er|piano|harmonica|flute|musical", "9207"),
 # auto, pets, food, garden
 (r"tyre|tire", "4011"), (r"car (parts|accessor|styling|interior|exterior)|auto parts|vehicle|motorbike|motorcycle|spark plug|brake|clutch|wiper|gear shift|steering", "8708"),
 (r"dog|cat|pet|bird|fish|aquarium", "2309"),
 (r"honey", "0409"), (r"\btea\b|green tea|coffee|\bsnack|biscuit|cookie|chocolate|spread|jam\b|sauce|noodle|pasta|cereal|oats", "2106"),
 (r"seeds|plant|planter|pots & planters|garden|hose|sprinkler|irrigation|fertili[sz]er", "3926"),
]
# chapters that make sense under a top-level Amazon category (generous but excludes absurd ones)
PRIORS = {
 "electronics": {85, 84, 90, 91, 94, 95, 39, 73, 76, 82, 83, 87, 96, 71, 39, 70, 40},
 "computers & accessories": {84, 85, 90, 39, 42, 73, 94},
 "home & kitchen": {39, 48, 49, 63, 69, 70, 73, 76, 82, 83, 84, 85, 94, 96, 33, 34, 44, 46, 56, 57, 58, 40, 71, 91, 95, 97, 62, 61, 42, 67, 66},
 "health & personal care": {30, 33, 34, 90, 21, 96, 48, 39, 85, 40, 63, 56, 62, 61, 29, 15, 19, 20, 17},
 "beauty": {33, 34, 96, 85, 39, 42, 90, 30, 71, 67, 82, 21, 68},
 "toys & games": {95, 39, 85, 49, 48, 96, 40, 94, 90, 37, 32, 34, 63, 62, 61, 42, 71},
 "baby": {95, 61, 62, 39, 96, 40, 94, 33, 34, 48, 63, 64, 42, 87, 85, 21, 19, 30},
 "sports, fitness & outdoors": {95, 39, 63, 42, 64, 61, 62, 73, 76, 90, 40, 85, 87, 89, 33, 21, 11, 94, 56, 66, 96, 82, 65},
 "clothing & accessories": {61, 62, 65, 42, 71, 63, 64, 66, 33, 96, 90, 91, 58},
 "shoes & handbags": {64, 42, 71, 63, 33, 34, 96, 40, 41},
 "jewellery": {71, 91, 96, 42, 39, 70}, "watches": {91, 71, 42, 85},
 "bags, wallets and luggage": {42, 63, 39, 61, 62, 96},
 "books": {49, 48}, "music": {85, 49, 92}, "movies & tv shows": {85, 49}, "video games": {95, 85, 49}, "software": {85, 49},
 "musical instruments": {92, 85, 39, 44, 73, 42, 90, 95},
 "office products": {48, 96, 39, 82, 83, 84, 85, 42, 49, 73, 44, 95, 90, 40, 94, 70},
 "car & motorbike": {87, 85, 40, 34, 39, 27, 73, 82, 83, 84, 90, 94, 70, 68, 59, 63, 95, 32, 38, 42, 61},
 "grocery & gourmet foods": {9, 4, 10, 11, 15, 17, 18, 19, 20, 21, 22, 23, 12, 7, 8, 2, 3, 16},
 "pet supplies": {23, 42, 39, 63, 96, 73, 40, 61, 62, 95, 94, 3, 5, 85, 82, 30, 33, 34},
 "industrial & scientific": {84, 85, 73, 90, 39, 82, 83, 40, 76, 70, 38, 69, 94, 48, 72, 74, 79, 68, 59, 56, 87, 81, 28, 29, 32, 34, 35, 91, 96},
 "home improvement": {85, 39, 73, 82, 83, 84, 69, 32, 94, 68, 70, 44, 76, 40, 72, 74, 25, 34, 90, 63, 57, 55, 39},
 "outdoor living": {84, 82, 39, 73, 94, 6, 12, 31, 38, 85, 63, 76, 44, 69, 95, 40, 87},
 "lab & scientific products": {90, 70, 39, 84, 85, 38, 30, 40, 73}, "cooking & baking supplies": {19, 17, 21, 9, 15, 18, 11, 39, 73},
}
def key_levels(crumb):
    return [x.strip() for x in crumb.split(">") if x.strip()]

def allowed(crumb):
    lv = key_levels(crumb)
    return PRIORS.get(lv[0].lower()) if lv else None

def leaf_heading(crumb, title=""):
    lv = key_levels(crumb)
    text = " > ".join(lv[-2:]).lower()
    ok = allowed(crumb)
    for scope in (" > ".join(lv[-1:]).lower(), text):          # most specific (last level) first
        best = None
        for i, (pat, h) in enumerate(LEAF_RULES):
            if ok is not None and int(h[:2]) not in ok: continue      # implausible under this top-level category
            for m in re.finditer(r"\b(?:" + pat + ")", scope):
                if best is None or m.end() > best[0]: best = (m.end(), h, m.group(0))   # head noun = right-most match
        if best: return best[1], best[2]
    return None, None
