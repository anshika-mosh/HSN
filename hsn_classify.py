"""Shared classification logic used by the Streamlit app (same rules as build_final.py)."""
import json, os, re
import hsn_chapter as C, hsn_code as K
import leaf_rules as LR

def _jload(*names):
    for n in names:
        if os.path.exists(n): return json.load(open(n, encoding="utf-8"))
    raise FileNotFoundError(names[0])

def key_of(crumb):
    lv = [x.strip() for x in crumb.split(">") if x.strip()]
    return " > ".join(lv[-2:]).lower()

class Classifier:
    def __init__(self):
        self.tariff = _jload("hsn_intelligence_hsn_tariff_items.json", "hsn_intelligence.hsn_tariff_items.json")
        self.chapters = _jload("hsn_intelligence_hsn_chapters.json", "hsn_intelligence.hsn_chapters.json")
        self.gst = _jload("hsn_intelligence_hsn_gst_rates.json", "hsn_intelligence.hsn_gst_rates.json")
        self.ci = C.build_index(self.tariff, self.chapters)
        self.cidx = K.build_code_index(self.tariff, self.gst)
        self.rules = json.load(open("category_rules.json", encoding="utf-8"))
        self.chname = {str(c["chapter_code"]).zfill(2): c.get("chapter_name", "") for c in self.chapters}
        self.hdesc = {}
        for t in self.tariff:
            self.hdesc.setdefault(str(t.get("heading_no")), t.get("heading_description", ""))

    @staticmethod
    def details(title, crumb, bullets=(), description="", specs=None):
        lv = [x.strip() for x in crumb.split(">") if x.strip()]
        mats = []
        for k, v in (specs or {}).items():
            if re.search(r"material|fabric|composition", k, re.I): mats.append(str(v))
        return dict(title=title, item_shape=None, materials_found_in_text=mats,
                    bullet_points=list(bullets), description=description or "",
                    leaf_category=lv[-1] if lv else None, product_type=lv[-2] if len(lv) > 1 else None)

    def classify(self, title, crumb="", bullets=(), description="", specs=None, top=5):
        d = self.details(title, crumb, bullets, description, specs)
        rule = self.rules.get(key_of(crumb)) if crumb else None
        flags, rule_used = [], None
        if rule:
            heading = rule["heading"]; tl = " " + title.lower() + " "
            for o in rule["rules"]:
                if any(w in tl for w in o["words"]): heading = o["heading"]; rule_used = o["words"]; break
            conf = "Review" if rule["uncertain"] else "High"
            if rule["uncertain"]: flags.append("Category is mixed/ambiguous - CA to confirm" + (f": {rule['note']}" if rule["note"] else ""))
            res = [r for r in K.score_items(self.cidx, K.build_query(d, crumb), [heading[:2]], K.title_phrases(title))
                   if r[1]["heading"] == heading]
            if not res:
                its = [i for i in self.cidx["by_chapter"].get(heading[:2], []) if i["heading"] == heading]
                res = [(1.0, i, []) for i in its[:1]]
                flags.append("No word match inside heading - first code taken, check"); conf = "Review"
            source = "Category rule"
        else:
            kwh, kw = LR.leaf_heading(crumb) if crumb else (None, None)
            res = []
            if kwh:                                   # keyword fallback on the category name
                res = [r for r in K.score_items(self.cidx, K.build_query(d, crumb), [kwh[:2]], K.title_phrases(title))
                       if r[1]["heading"] == kwh]
                if not res:
                    its = [i for i in self.cidx["by_chapter"].get(kwh[:2], []) if i["heading"] == kwh]
                    res = [(1.0, i, []) for i in its[:1]]
                conf = "Review"; source = f"Category keyword '{kw}'"
                flags.append(f"Chapter/heading chosen from the category name ('{kw}') - not a reviewed category, verify")
            else:                                     # automatic match, limited to plausible chapters
                conf = "Unreviewed"; source = "Automatic word-match"
                flags.append("Automatic suggestion - category not reviewed" if crumb else "No breadcrumb - description-only suggestion")
                ok = LR.allowed(crumb) if crumb else None
                chs = C.find_chapters(self.ci, d, crumb)
                pick = next((c["chapter"] for c in chs if ok is None or int(c["chapter"]) in ok), None)
                if pick:
                    res = K.score_items(self.cidx, K.build_query(d, crumb), [pick], K.title_phrases(title))
                elif ok:
                    res = K.score_items(self.cidx, K.build_query(d, crumb), [f"{c:02d}" for c in sorted(ok)], K.title_phrases(title))
                    flags.append("Automatic match limited to plausible chapters for this category")
        if not res: return None
        best = res[0][0]; cands = []
        for i, (s, it, _) in enumerate(res[:top]):
            rates, label, hr = K.rate_for(self.cidx, it["code"])
            conflict = K.rate_conflict(rates, hr) and not label
            cands.append(dict(code=it["code"], description=it["description"], unit=it.get("unit"),
                              heading=it["heading"], score=round(s / best, 2) if best else 1.0,
                              rate=K.fmt_rate(rates), conflict=conflict,
                              heading_rate=K.fmt_rate(hr) if conflict else None, multi_rate=len(rates) > 1))
        t = cands[0]
        if t["conflict"]:
            flags.append(f"Rate conflict: heading shows {t['heading_rate']}, code shows {t['rate']} - verify")
            if conf == "High": conf = "Review"
        if t["multi_rate"]: flags.append("Two rates (condition/price slab)")
        if len(cands) > 1 and cands[1]["score"] >= 0.93 and cands[1]["code"] != t["code"]:
            flags.append("Close call with " + cands[1]["code"]); 
            if conf == "High": conf = "Review"
        ch = t["code"][:2]
        return dict(chapter=ch, chapter_name=self.chname.get(ch, ""), heading=t["heading"],
                    heading_description=self.hdesc.get(t["heading"], ""), best=t, candidates=cands,
                    confidence=conf, flags=flags, source=source, rule_keyword=rule_used)
