#!/usr/bin/env python3
"""Compare la version produite par Claude et la version reprise par l'utilisateur.

Usage : python3 compare.py ia.txt humain.txt [--lang fr|en|pt] [--json]
Sortie : métriques avant/après, liste des écarts classés, candidats pour le lexique.
Sert d'entrée à la procédure "Apprendre d'une correction" du SKILL.md.
"""
import argparse, difflib, json, re, statistics, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import audit as A  # noqa: E402

TOKEN = re.compile(r"\w+(?:['’-]\w+)*|[^\w\s]")
CONNECT = {
    "fr": {"et", "aussi", "d'ailleurs", "d’ailleurs", "bien", "sûr", "puis", "donc", "mais", "car", "alors", "ensuite", "parce"},
    "en": {"and", "also", "of", "course", "so", "but", "then", "because", "actually"},
    "pt": {"e", "também", "aliás", "claro", "depois", "então", "mas", "porque", "afinal", "enfim"},
}
FIRST = {"fr": {"je", "j", "j'", "j’", "nous", "on", "mon", "ma", "mes", "notre", "nos"},
         "en": {"i", "we", "my", "our", "me", "us"},
         "pt": {"eu", "nós", "a gente", "meu", "minha", "meus", "minhas", "nosso", "nossa", "nossos", "nossas", "me", "nos"}}
PUNCT = {"tiret cadratin": "—", "tiret demi-cadratin": "–", "deux-points": ":", "point-virgule": ";",
         "parenthèse": "(", "guillemet français": "«", "point d'exclamation": "!"}


def detok(tokens):
    s = " ".join(tokens)
    s = re.sub(r"\s+([,.)…])", r"\1", s)
    s = re.sub(r"\(\s+", "(", s)
    return s.strip()


def metrics(text, lang):
    r = A.audit(text, lang)
    sents = A.sentences(text)
    lens = [len(s.split()) for s in sents] or [0]
    mean = statistics.mean(lens)
    words = [w.lower() for w in re.findall(r"\w+(?:['’]\w+)*", text)]
    first = sum(1 for w in words if w in FIRST[lang] or w.split("'")[0].split("’")[0] in FIRST[lang])
    m = {
        "mots": len(words),
        "phrases": len(sents),
        "longueur_moyenne": round(mean, 1),
        "coef_variation": round(statistics.pstdev(lens) / mean, 2) if mean and len(lens) > 1 else 0,
        "phrases_<=5_mots": sum(1 for n in lens if n <= 5),
        "lignes_de_liste": len(re.findall(r"^\s*[-*•]\s", text, flags=re.M)),
        "premiere_personne": first,
        "score_audit": r["score"], "alertes_rouges": r["rouge"], "alertes_orange": r["orange"],
    }
    for name, ch in PUNCT.items():
        m[name] = text.count(ch)
    return m, r


def split_sents(text):
    clean = re.sub(r"^\s*[-*•#>]+\s*", "", text, flags=re.M)
    parts = re.split(r"(?<=[.!?…])\s+|\n+", clean)
    return [p.strip() for p in parts if p.strip()]


def words_of(s):
    return [w.lower().replace("’", "'") for w in re.findall(r"\w+(?:['’-]\w+)*", s)]


def sim(x, y):
    return difflib.SequenceMatcher(None, words_of(x), words_of(y), autojunk=False).ratio()


def align(A_, B_, seuil=0.3):
    """Alignement monotone des phrases (programmation dynamique sur la similarité)."""
    n, m = len(A_), len(B_)
    S = [[0.0] * (m + 1) for _ in range(n + 1)]
    sims = [[sim(a, b) for b in B_] for a in A_]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            best = max(S[i - 1][j], S[i][j - 1])
            if sims[i - 1][j - 1] >= seuil:
                best = max(best, S[i - 1][j - 1] + sims[i - 1][j - 1])
            S[i][j] = best
    pairs, i, j = [], n, m
    while i > 0 and j > 0:
        if sims[i - 1][j - 1] >= seuil and abs(S[i][j] - (S[i - 1][j - 1] + sims[i - 1][j - 1])) < 1e-9:
            pairs.append((i - 1, j - 1)); i -= 1; j -= 1
        elif S[i - 1][j] >= S[i][j - 1]:
            i -= 1
        else:
            j -= 1
    return pairs[::-1], sims


def overlap(x, y):
    wx = {w for w in words_of(x) if len(w) > 3}
    return len(wx & set(words_of(y))) / len(wx) if wx else 0


def tag_change(av, ap, window, lex, lang):
    tags = []
    wa = [t for t in av if re.match(r"\w", t)]
    wb = [t for t in ap if re.match(r"\w", t)]
    if not wa and not wb:
        tags.append("ponctuation")
    elif [t.lower().replace("’", "'") for t in wa] == [t.lower().replace("’", "'") for t in wb]:
        tags.append("casse ou apostrophe")
    known = sorted({term for rx, term, _, _ in lex if av and rx.search(window)})
    if known:
        tags.append("déjà au lexique : " + ", ".join(known[:3]))
    if any(t.lower() in CONNECT[lang] for t in ap) and not any(t.lower() in CONNECT[lang] for t in av):
        tags.append("connecteur ajouté")
    if any(t.lower() in FIRST[lang] for t in ap) and not any(t.lower() in FIRST[lang] for t in av):
        tags.append("première personne ajoutée")
    if "—" in av and "—" not in ap:
        tags.append("tiret cadratin retiré")
    if len(wb) > len(wa) + 3:
        tags.append("allongé")
    elif len(wa) > len(wb) + 3:
        tags.append("raccourci")
    return tags, wa, wb, bool(known)


def changes(a_txt, b_txt, lang):
    A_, B_ = split_sents(a_txt), split_sents(b_txt)
    pairs, sims = align(A_, B_)
    lex = A.load_lexicon(lang)
    out, done_a, done_b = [], {i for i, _ in pairs}, {j for _, j in pairs}
    for i, j in pairs:
        if A_[i] == B_[j]:
            continue
        a, b = TOKEN.findall(A_[i]), TOKEN.findall(B_[j])
        for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
            if tag == "equal":
                continue
            av, ap = a[i1:i2], b[j1:j2]
            window = detok(a[max(0, i1 - 3):min(len(a), i2 + 3)])
            tags, wa, wb, known = tag_change(av, ap, window, lex, lang)
            out.append({"phrase": i + 1, "type": "remplacement" if av and ap else ("suppression" if av else "ajout"),
                        "contexte": detok(a[max(0, i1 - 4):i1]), "avant": detok(av), "apres": detok(ap),
                        "indices": tags, "_wa": wa, "_wb": wb, "_known": known})
    # Phrases réécrites en profondeur : sous le seuil d'alignement, mais même contenu.
    for i, s in enumerate(A_):
        if i in done_a:
            continue
        free = [j for j in range(len(B_)) if j not in done_b]
        best = max(free, key=lambda j: overlap(s, B_[j]), default=None)
        if best is not None and overlap(s, B_[best]) >= 0.5:
            done_a.add(i); done_b.add(best)
            tags, wa, wb, known = tag_change(TOKEN.findall(s), TOKEN.findall(B_[best]), s, lex, lang)
            out.append({"phrase": i + 1, "type": "phrase réécrite", "contexte": "", "avant": s, "apres": B_[best],
                        "indices": tags, "_wa": wa, "_wb": wb, "_known": True})
    for i, s in enumerate(A_):
        if i in done_a:
            continue
        near = [B_[j] for k, j in pairs if abs(k - i) == 1]
        merged = any(overlap(s, b) >= 0.5 for b in near)
        tags, wa, _, known = tag_change(TOKEN.findall(s), [], s, lex, lang)
        tags = [t for t in tags if t != "raccourci"] + (["fusionnée avec une phrase voisine"] if merged else [])
        out.append({"phrase": i + 1, "type": "phrase supprimée", "contexte": "", "avant": s, "apres": "",
                    "indices": tags, "_wa": wa, "_wb": [], "_known": known})
    for j, s in enumerate(B_):
        if j in done_b:
            continue
        near = [A_[i] for i, k in pairs if abs(k - j) == 1]
        split = any(overlap(s, a) >= 0.5 for a in near)
        tags, _, wb, _ = tag_change([], TOKEN.findall(s), "", lex, lang)
        tags = [t for t in tags if t != "allongé"] + (["issue d'une phrase scindée"] if split else [])
        out.append({"phrase": None, "type": "phrase ajoutée", "contexte": "", "avant": "", "apres": s,
                    "indices": tags, "_wa": [], "_wb": wb, "_known": False})
    ratio = round(difflib.SequenceMatcher(None, words_of(a_txt), words_of(b_txt), autojunk=False).ratio(), 2)
    stats = {"phrases_ia": len(A_), "inchangées": sum(1 for i, j in pairs if A_[i] == B_[j]),
             "retouchées": sum(1 for i, j in pairs if A_[i] != B_[j]),
             "réécrites": sum(1 for c in out if c["type"] == "phrase réécrite"),
             "supprimées": len(A_) - len(done_a), "ajoutées": len(B_) - len(done_b)}
    return out, ratio, stats


def candidates(chs):
    seen, res = set(), []
    for c in chs:
        if c["type"] != "remplacement" or c["_known"]:
            continue
        if 1 <= len(c["_wa"]) <= 4 and len(c["_wb"]) <= 8 and c["avant"].lower() != c["apres"].lower():
            key = " ".join(c["_wa"]).lower()
            if key not in seen and "ponctuation" not in c["indices"] and "casse ou apostrophe" not in c["indices"]:
                seen.add(key)
                res.append(f"- {' '.join(c['_wa'])} | {' '.join(c['_wb']) or 'supprimer'}")
    for c in chs:
        if c["type"] == "suppression" and 1 <= len(c["_wa"]) <= 3 and not c["_known"]:
            key = " ".join(c["_wa"]).lower()
            if key not in seen:
                seen.add(key)
                res.append(f"- {' '.join(c['_wa'])} | supprimer")
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ia")
    ap.add_argument("humain")
    ap.add_argument("--lang", choices=["fr", "en", "pt"])
    ap.add_argument("--json", action="store_true")
    o = ap.parse_args()
    ia = Path(o.ia).read_text(encoding="utf-8")
    hu = Path(o.humain).read_text(encoding="utf-8")
    lang = o.lang or A.detect_lang(hu)
    mi, ri = metrics(ia, lang)
    mh, rh = metrics(hu, lang)
    chs, ratio, pst = changes(ia, hu, lang)
    cands = candidates(chs)
    for c in chs:
        for k in ("_wa", "_wb", "_known"):
            c.pop(k)
    regress = [al for al in rh["alertes"] if al["niveau"] == "rouge"]

    if o.json:
        print(json.dumps({"langue": lang, "similarite": ratio, "metriques": {"ia": mi, "humain": mh},
                          "phrases": pst, "ecarts": chs, "candidats_lexique": cands,
                          "alertes_rouges_sur_version_humaine": regress}, ensure_ascii=False, indent=2))
        return

    print(f"Langue {lang} | similarité {ratio} | {len(chs)} écarts")
    print("Phrases : " + ", ".join(f"{k} {v}" for k, v in pst.items()))
    print("\nMétriques (IA -> humain)")
    for k in mi:
        if mi[k] != mh[k]:
            print(f"- {k} : {mi[k]} -> {mh[k]}")
    print("\nÉcarts")
    for n, c in enumerate(chs, 1):
        tag = f" [{'; '.join(c['indices'])}]" if c["indices"] else ""
        ctx = f"…{c['contexte']} " if c["contexte"] else ""
        where = f"phrase {c['phrase']}, " if c["phrase"] else ""
        print(f"{n}. {where}{c['type']}{tag}\n   {ctx}« {c['avant']} » -> « {c['apres']} »")
    if cands:
        print("\nCandidats lexique (à juger, un seul cas ne fait pas une règle)")
        print("\n".join(cands))
    if regress:
        print("\nAlertes rouges déclenchées par la version de l'utilisateur (règle du skill peut-être trop stricte)")
        for al in regress:
            print(f"- {al['type']} : {al['extrait']}")


if __name__ == "__main__":
    main()
