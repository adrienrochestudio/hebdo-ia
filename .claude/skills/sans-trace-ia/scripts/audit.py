#!/usr/bin/env python3
"""Audit d'un texte pour les marqueurs d'écriture IA.

Usage : python3 audit.py fichier.txt [--lang fr|en|pt] [--json]
        cat texte.txt | python3 audit.py - --lang fr
Lit les lexiques dans ../references/lexique-{lang}.md.
Code de sortie : 0 si aucune alerte rouge, 1 sinon.
"""
import argparse, json, re, statistics, sys
from pathlib import Path

REF = Path(__file__).resolve().parent.parent / "references"
STOP_FR = {"le", "la", "les", "des", "est", "une", "et", "du", "que", "qui", "dans", "pour", "pas", "sur"}
STOP_EN = {"the", "is", "and", "of", "to", "that", "with", "for", "this", "are", "not", "on", "it"}
STOP_PT = {"não", "uma", "os", "com", "para", "em", "da", "das", "dos", "na", "nas", "ao", "pelo", "pela", "é", "são", "também", "mas", "foi"}


def detect_lang(text):
    words = re.findall(r"[a-zA-Zéèàùâêîôûç']+", text.lower())
    fr = sum(w in STOP_FR for w in words)
    en = sum(w in STOP_EN for w in words)
    pt = sum(w in STOP_PT for w in re.findall(r"[a-zA-Zéèàùâêîôûçáíóúãõ']+", text.lower()))
    if pt > fr and pt > en:
        return "pt"
    return "fr" if fr >= en else "en"


def load_lexicon(lang):
    entries, level = [], "orange"
    for line in (REF / f"lexique-{lang}.md").read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            level = "rouge" if "[rouge]" in line else "orange"
            continue
        if not line.startswith("- ") or " | " not in line:
            continue
        term, repl = [p.strip() for p in line[2:].rsplit(" | ", 1)]
        if term.startswith("re:"):
            pat = term[3:]
        else:
            pat = r"(?<![\w])" + re.escape(term) + r"(?![\w])"
        try:
            entries.append((re.compile(pat, re.IGNORECASE), term, repl, level))
        except re.error as e:
            print(f"lexique : motif invalide {term!r} ({e})", file=sys.stderr)
    return entries


def line_of(text, pos):
    return text.count("\n", 0, pos) + 1


def sentences(text):
    clean = re.sub(r"^\s*[-*#>]+\s*", "", text, flags=re.M)
    parts = re.split(r"(?<=[.!?…])\s+|\n{2,}", clean)
    return [p for p in parts if len(p.split()) >= 2]


STRUCT = {
    "fr": [
        (r"\bce n'est pas\b[^.!?]{0,80}?,\s*c'est\b", "parallélisme négatif (ce n'est pas X, c'est Y)", "rouge"),
        (r"\bnon seulement\b[^.!?]{0,120}\bmais\b", "parallélisme négatif (non seulement... mais)", "rouge"),
        (r"\bplutôt que de\b", "Y plutôt que X", "orange"),
        (r",\s*(?:renforçant|soulignant|illustrant|témoignant|marquant|confirmant|reflétant|contribuant|permettant|offrant)\b", "participe présent final qui commente", "rouge"),
        (r"\bmalgré (?:ses|son|sa|leurs?)\b[^.]{0,80}\b(?:défis|enjeux)\b", "conclusion défis/perspectives", "rouge"),
        (r"\b(?:les experts|de nombreux (?:observateurs|experts|spécialistes)|selon certaines sources|des études montrent)\b", "attribution vague", "rouge"),
        (r"(?:^|[.!?:]\s+)Ce (?:qui|que) [^.!?]{0,80},\s*c'est\b", "phrase pseudo-clivée (ce qui X, c'est Y)", "rouge"),
        (r"\bc'est (?:là )?(?:à quoi|ce à quoi|pour cela|pour ça) que\b", "renvoi pseudo-clivé (c'est à quoi sert X)", "orange"),
    ],
    "en": [
        (r"\b(?:it's|it is|this is|that's) not\b[^.!?]{0,80}?[,;]\s*(?:it's|it is|but)\b", "negative parallelism (not X, it's Y)", "rouge"),
        (r"\bnot only\b[^.!?]{0,120}\bbut\b", "negative parallelism (not only... but)", "rouge"),
        (r",\s*(?:highlighting|underscoring|showcasing|emphasizing|reflecting|marking|fostering|contributing|ensuring)\b", "trailing -ing commentary", "rouge"),
        (r"\bdespite (?:its|their)\b[^.]{0,80}\bchallenges\b", "challenges/future prospects formula", "rouge"),
        (r"\b(?:experts (?:say|believe|argue)|many observers|studies show|some critics)\b", "vague attribution", "rouge"),
        (r"(?:^|[.!?:]\s+)What (?!is\b|are\b|do\b|does\b|did\b|if\b)[^.!?]{0,60}\b(?:is|are|was)\b[^?]*?[.!]", "pseudo-cleft (What X is, is Y)", "rouge"),
        (r"(?:^|[.!?]\s+)(?:That|This) is (?:what|why|how|where|the date|the moment|the point)\b", "pseudo-cleft back-reference (That is what...)", "rouge"),
    ],
    "pt": [
        (r"\bnão (?:é|são|foi|se trata de)\b[^.!?]{0,80}?[,;]\s*(?:é|são|foi|mas)\b", "parallélisme négatif (não é X, é Y)", "rouge"),
        (r"\bnão (?:apenas|só|somente)\b[^.!?]{0,120}\bmas (?:também|sim)\b", "parallélisme négatif (não apenas... mas também)", "rouge"),
        (r",\s*(?:destacando|ressaltando|reforçando|evidenciando|refletindo|marcando|consolidando|contribuindo|permitindo|oferecendo|demonstrando|sublinhando|garantindo)\b", "gérondif final qui commente", "rouge"),
        (r"\bapesar d(?:e|os|as) (?:seus|suas|os|as)?\s?[^.]{0,80}\bdesafios\b", "conclusion desafios/perspectivas", "rouge"),
        (r"\b(?:especialistas (?:dizem|afirmam|apontam|acreditam)|(?:muitos|diversos) (?:observadores|especialistas|analistas)|estudos (?:mostram|apontam|indicam)|segundo algumas fontes)\b", "attribution vague", "rouge"),
        (r"(?:^|[.!?:]\s+)O que [^.!?]{0,80},\s*(?:é|são|foi)\b", "phrase pseudo-clivée (o que X, é Y)", "rouge"),
        (r"(?:^|[.!?]\s+)(?:É|Foi|São|Foram) (?:em|por|com|a|ao|para|nesse|neste|nessa|nesta|assim|aqui|ali|lá|desde|graças a|sobre)\b[^.!?,]{0,60}?\bque\b", "gallicisme é... que (c'est... que)", "orange"),
        (r"\b(?:em vez|ao invés) de\b", "Y em vez de X", "orange"),
    ],
}

# Passif analytique pt (foi decidido, são feitos) : compté pour repérer le passif de traduction.
PASSIVE_PT = r"\b(?:é|são|foi|foram|será|serão|seria|seriam|era|eram|tem sido|têm sido|foi sendo)\s+(?:\w+mente\s+)?\w+(?:ado|ada|ados|adas|ido|ida|idos|idas|ído|ída|ídos|ídas|ito|ita|itos|itas|osto|osta|ostos|ostas)\b"


def audit(text, lang):
    alerts = []

    def add(level, line, kind, extract, hint=""):
        alerts.append({"niveau": level, "ligne": line, "type": kind, "extrait": extract, "conseil": hint})

    for m in re.finditer("—", text):
        add("rouge", line_of(text, m.start()), "tiret cadratin", text[max(0, m.start()-25):m.end()+25].replace("\n", " "), "virgule, deux-points, parenthèses ou point")
    for m in re.finditer(r"\s–\s", text):
        add("orange", line_of(text, m.start()), "tiret demi-cadratin en incise", text[max(0, m.start()-25):m.end()+25].replace("\n", " "), "réservé aux intervalles")
    for m in re.finditer(r"\*\*[^*\n]+\*\*", text):
        add("orange", line_of(text, m.start()), "gras markdown", m.group(0))
    if "'" in text and "’" in text:
        add("orange", 0, "apostrophes mélangées", "' et ’", "uniformiser")
    for m in re.finditer(r"^#+\s.*\?\s*$", text, flags=re.M):
        add("orange", line_of(text, m.start()), "titre en question", m.group(0).strip())
    for m in re.finditer(r"^#+\s*(?:conclusion|en conclusion|héritage|legacy)\s*$", text, flags=re.M | re.I):
        add("rouge", line_of(text, m.start()), "section conclusion/héritage", m.group(0).strip())

    if lang == "fr":
        for m in re.finditer(r"\"[^\"\n]{2,}\"", text):
            add("orange", line_of(text, m.start()), "guillemets anglais", m.group(0)[:50], "« » en français")
        for m in re.finditer(r"\w[;:!?](?=\s|$)", text):
            ctx = text[max(0, m.start()-10):m.end()+5]
            if "http" in ctx or re.search(r"\d:\d", ctx):
                continue
            add("orange", line_of(text, m.start()), "espace insécable manquante", ctx.replace("\n", " "))
        for m in re.finditer(r"^#+\s+((?:[A-ZÉÈÀ][\w'’]*\s+){2,}[A-ZÉÈÀ][\w'’]*)\s*$", text, flags=re.M):
            add("orange", line_of(text, m.start()), "casse de titre à l'anglaise", m.group(1))
        for m in re.finditer(r"\b(?:impact(?:er|e|ent|é)|adress(?:er|e) (?:un|le|ce|les) (?:problème|sujet|enjeu)|fai(?:re|t) sens|en termes de)\b", text, flags=re.I):
            add("orange", line_of(text, m.start()), "calque de l'anglais", m.group(0))

    if lang == "pt":
        for m in re.finditer(r"«[^»\n]{2,}»", text):
            add("orange", line_of(text, m.start()), "guillemets français", m.group(0)[:50], "aspas “ ”")
        for m in re.finditer(r"(?<![\d.,])\d+\.\d{1,2}(?![\d.])", text):
            add("orange", line_of(text, m.start()), "point décimal", m.group(0), "vírgula decimal (3,5)")
        for m in re.finditer(r"(?<![\d.,])\d{1,3}(?:[ \u00a0\u202f]\d{3})+(?!\d)", text):
            add("orange", line_of(text, m.start()), "séparateur de milliers", m.group(0), "ponto (12.500)")
        for m in re.finditer(r"\b\d{1,2}/\d{1,2}/\d{2,4}\b", text):
            add("orange", line_of(text, m.start()), "date numérique", m.group(0), "26 de outubro de 2026")
        for m in re.finditer(r"(?:R|US)\$(?=\d)|€\s?\d", text):
            add("orange", line_of(text, m.start()), "format monétaire", text[m.start():m.end()+6], "R$ 1,5 bilhão ; 2 bilhões de euros")
        for m in re.finditer(r"(?<![\d.,])1,\d+\s+(?:milhões|bilhões|trilhões)\b", text):
            add("orange", line_of(text, m.start()), "accord milhão/bilhão", m.group(0), "singular abaixo de 2 (1,5 bilhão)")
        for m in re.finditer(r"\b(?:(?:Segunda|Terça|Quarta|Quinta|Sexta)-[Ff]eira|Sábado|Domingo|Janeiro|Fevereiro|Março|Abril|Maio|Junho|Julho|Agosto|Setembro|Outubro|Novembro|Dezembro)\b", text):
            if m.start() == 0 or re.search(r"(?:[.!?:]\s*|\n\s*|^[-*#>]\s*|[“\"(]\s*)$", text[max(0, m.start()-3):m.start()]):
                continue
            add("orange", line_of(text, m.start()), "jour ou mois en majuscule", m.group(0), "minúscula")
        for m in re.finditer(r"\b(?:tu (?:és|estás|tens|podes|vais|sabes|queres)|vós)\b", text, flags=re.I):
            add("orange", line_of(text, m.start()), "tutoiement européen", m.group(0), "você")
        eque = len(re.findall(r"\b(?:é|foi|são|foram) que\b", text, flags=re.I))
        if eque >= 2:
            add("rouge", 0, "« é que » en cascade", f"{eque} occurrences", "réécrire en phrase directe")

    for rx, term, repl, level in load_lexicon(lang):
        for m in rx.finditer(text):
            add(level, line_of(text, m.start()), "lexique", m.group(0), repl)

    for pat, kind, level in STRUCT[lang]:
        for m in re.finditer(pat, text, flags=re.I):
            add(level, line_of(text, m.start()), kind, m.group(0)[:80])

    conj = r"\s(?:et|ou)\s" if lang == "fr" else r"\s(?:e|ou)\s" if lang == "pt" else r",?\s(?:and|or)\s"
    triplets = re.findall(r"\b[\w'’-]+(?:\s[\w'’-]+){0,2},\s[\w'’-]+(?:\s[\w'’-]+){0,2}" + conj + r"[\w'’-]+", text)
    sents = sentences(text)
    n = max(len(sents), 1)
    if len(triplets) / n > 0.25 and len(triplets) >= 3:
        add("rouge", 0, "règle de trois trop fréquente", f"{len(triplets)} énumérations ternaires pour {n} phrases", "varier : un, deux ou quatre éléments")

    lengths = [len(s.split()) for s in sents]
    stats = {"phrases": len(lengths), "mots": sum(lengths)}
    if len(lengths) >= 5:
        mean = statistics.mean(lengths)
        cv = statistics.pstdev(lengths) / mean if mean else 0
        stats.update({"longueur_moyenne": round(mean, 1), "coef_variation": round(cv, 2)})
        if cv < 0.35:
            add("rouge", 0, "rythme uniforme", f"coefficient de variation {cv:.2f}", "viser > 0,45 : alterner phrases très courtes et longues")
        elif cv < 0.45:
            add("orange", 0, "rythme un peu uniforme", f"coefficient de variation {cv:.2f}")
        starts = [s.split()[0].lower() for s in sents if s.split()]
        top = max(set(starts), key=starts.count)
        if starts.count(top) / len(starts) > 0.3:
            add("orange", 0, "débuts de phrase répétés", f"« {top} » ouvre {starts.count(top)} phrases sur {len(starts)}")

    if lang == "pt" and len(sents) >= 4:
        passives = len(re.findall(PASSIVE_PT, text, flags=re.I))
        if passives / len(sents) > 0.3 and passives >= 3:
            add("orange", 0, "passif excessif", f"{passives} passifs pour {len(sents)} phrases", "voz ativa : O governo decidiu")

    words = max(stats["mots"], 1)
    lex = sum(1 for a in alerts if a["type"] == "lexique")
    stats["marqueurs_pour_100_mots"] = round(100 * lex / words, 2)
    rouge = sum(a["niveau"] == "rouge" for a in alerts)
    orange = sum(a["niveau"] == "orange" for a in alerts)
    score = max(0, 100 - 8 * rouge - 3 * orange)
    return {"langue": lang, "score": score, "rouge": rouge, "orange": orange, "stats": stats,
            "alertes": sorted(alerts, key=lambda a: (a["niveau"] != "rouge", a["ligne"]))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("fichier")
    ap.add_argument("--lang", choices=["fr", "en", "pt"])
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    text = sys.stdin.read() if a.fichier == "-" else Path(a.fichier).read_text(encoding="utf-8")
    r = audit(text, a.lang or detect_lang(text))
    if a.json:
        print(json.dumps(r, ensure_ascii=False, indent=2))
    else:
        print(f"Langue {r['langue']} | score {r['score']}/100 | rouge {r['rouge']} | orange {r['orange']}")
        print("Stats : " + ", ".join(f"{k} {v}" for k, v in r["stats"].items()))
        for al in r["alertes"]:
            loc = f"l.{al['ligne']}" if al["ligne"] else "global"
            hint = f" -> {al['conseil']}" if al["conseil"] else ""
            print(f"[{al['niveau']}] {loc} {al['type']} : {al['extrait']}{hint}")
    sys.exit(1 if r["rouge"] else 0)


if __name__ == "__main__":
    main()
