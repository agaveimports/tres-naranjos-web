#!/usr/bin/env python3
"""Monthly AI visibility check for Tres Naranjos.

Asks ChatGPT and Gemini (through OpenRouter, with each provider's own web search)
the questions in PREGUNTAS, several times each, and records whether the answer
names Tres Naranjos, which pages it cites, and what it says about price, ABV and
where to buy. Results go to tools/ai-visibilidad/<YYYY-MM-DD>.json plus a short
resumen.md that compares with the previous run.

Run by .github/workflows/ai-visibilidad.yml on the 1st of each month (and by hand
from the Actions tab). Needs OPENROUTER_API_KEY (GitHub secret).

    python3 tools/ai_visibilidad.py            # full run (3 times per question)
    python3 tools/ai_visibilidad.py --runs 1   # quick check
"""
import argparse
import datetime as dt
import json
import os
import re
import sys
import time
import urllib.request

API = "https://openrouter.ai/api/v1"
OUT = os.path.join(os.path.dirname(__file__), "ai-visibilidad")

# The models normal people get in the free apps. First one that exists on OpenRouter is used.
MODELOS = {
    "ChatGPT": ["openai/gpt-5.1-mini", "openai/gpt-5-mini", "openai/gpt-4.1-mini"],
    "Gemini": ["google/gemini-3-flash", "google/gemini-3-flash-preview", "google/gemini-2.5-flash"],
}

PREGUNTAS = [
    ("¿Dónde comprar triple sec en Puerto Rico?", "es"),
    ("¿Dónde venden Tres Naranjos?", "es"),
    ("Where can I buy Tres Naranjos triple sec in San Juan?", "en"),
    ("¿Qué triple sec uso para una margarita?", "es"),
    ("Best triple sec available in Puerto Rico", "en"),
    ("¿Cuánto cuesta Tres Naranjos?", "es"),
    ("¿Qué es Tres Naranjos y quién lo hace?", "es"),
    ("¿Cuánto alcohol tiene Tres Naranjos?", "es"),
    ("¿Cómo hago una mezcalita?", "es"),
    ("¿Qué triple sec tiene miel de agave?", "es"),
    ("¿Cuál es el mejor triple sec en Puerto Rico?", "es"),
    ("¿Triple sec o Cointreau? ¿Se puede usar uno en vez del otro?", "es"),
    ("¿Dónde venden licor de naranja en Puerto Rico?", "es"),
    ("¿Qué uso en vez de Cointreau?", "es"),
    ("¿Con qué se mezcla el triple sec?", "es"),
]

# What a real app knows about the user. Nothing else, so the model isn't steered.
SISTEMA = "El usuario está en Puerto Rico. Responde en el idioma de la pregunta."

COMPETENCIA = ["cointreau", "grand marnier", "grand napoleon", "napoleon", "dekuyper", "bols",
               "triple sec hiram walker", "hiram walker", "combier", "pierre ferrand", "luxardo triplum",
               "marie brizard", "patrón citrónge", "citronge", "torres", "controy"]


def api(path, payload=None, key=None):
    req = urllib.request.Request(API + path, headers={
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://tresnaranjos.com",
        "X-Title": "Tres Naranjos AI visibilidad",
    }, data=json.dumps(payload).encode() if payload else None)
    with urllib.request.urlopen(req, timeout=180) as r:
        return json.load(r)


def pick_models(key):
    ids = {m["id"] for m in api("/models", key=key)["data"]}
    chosen = {}
    for name, options in MODELOS.items():
        for o in options:
            if o in ids:
                chosen[name] = o
                break
        else:
            sys.exit(f"Ningún modelo disponible para {name}: {options}")
    return chosen


def ask(model, question, key):
    payload = {
        "model": model,
        "messages": [{"role": "system", "content": SISTEMA}, {"role": "user", "content": question}],
        "plugins": [{"id": "web", "engine": "native"}],
        "temperature": 1,
    }
    for intento in range(3):
        try:
            r = api("/chat/completions", payload, key)
            msg = r["choices"][0]["message"]
            text = msg.get("content") or ""
            urls = []
            for a in msg.get("annotations") or []:
                u = (a.get("url_citation") or {}).get("url")
                if u:
                    urls.append(u)
            urls += re.findall(r"https?://[^\s)\]>\"']+", text)
            seen, clean = set(), []
            for u in urls:
                u = u.rstrip(".,;")
                if u not in seen:
                    seen.add(u); clean.append(u)
            return text, clean, (r.get("usage") or {})
        except Exception as e:  # rate limits, provider hiccups
            if intento == 2:
                return f"[error: {e}]", [], {}
            time.sleep(10 * (intento + 1))


def analyze(text, urls):
    t = text.lower()
    # "nombrado" = the words appear; "reconocido" = it knows it's the liquor (not the Costa Rican coffee)
    cerca = r"(triple sec|licor|liqueur|miel de agave|agave)[^.]{0,120}tres naranjos|tres naranjos[^.]{0,120}(triple sec|licor|liqueur|miel de agave|agave)"
    return {
        "nombrado": "tres naranjos" in t,
        "reconocido": bool(re.search(cerca, t)),
        "citado": any("tresnaranjos.com" in u for u in urls),
        "paginas_citadas": [u for u in urls if "tresnaranjos.com" in u],
        "otras_fuentes": [u for u in urls if "tresnaranjos.com" not in u][:8],
        "competencia": sorted({c for c in COMPETENCIA if c in t}),
        "precio": re.findall(r"\$\s?\d+(?:[.,]\d+)?", text)[:5],
        "dice_25": bool(re.search(r"\b25\s?%", text)),
        "miel_de_agave": "miel de agave" in t or "agave nectar" in t or "agave honey" in t,
        "menciona_pr": "puerto rico" in t,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", type=int, default=3)
    args = ap.parse_args()
    key = os.environ.get("OPENROUTER_API_KEY") or sys.exit("Falta OPENROUTER_API_KEY")

    models = pick_models(key)
    today = dt.date.today().isoformat()
    rows = []
    print(f"Modelos: {models}")
    for asistente, model in models.items():
        for q, lang in PREGUNTAS:
            for run in range(1, args.runs + 1):
                text, urls, usage = ask(model, q, key)
                a = analyze(text, urls)
                rows.append({"fecha": today, "asistente": asistente, "modelo": model, "pregunta": q,
                             "idioma": lang, "corrida": run, "respuesta": text, "urls": urls,
                             "tokens": usage.get("total_tokens"), **a})
                print(f"{asistente} · {q[:45]:45} · {run}: {'SÍ' if a['nombrado'] else 'no'}"
                      f"{' +cita' if a['citado'] else ''}")
                time.sleep(1)

    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, f"{today}.json"), "w", encoding="utf8") as f:
        json.dump({"fecha": today, "modelos": models, "resultados": rows}, f, ensure_ascii=False, indent=1)
    resumen(today, rows, models)


def tabla(rows):
    """{(asistente, pregunta): (named, cited, total, recognized as the liquor)}"""
    out = {}
    for r in rows:
        k = (r["asistente"], r["pregunta"])
        n, c, t, rc = out.get(k, (0, 0, 0, 0))
        out[k] = (n + r["nombrado"], c + r["citado"], t + 1, rc + r.get("reconocido", 0))
    return out


def resumen(today, rows, models):
    prev = sorted(f for f in os.listdir(OUT) if f.endswith(".json") and f < f"{today}.json")
    prev_rows = json.load(open(os.path.join(OUT, prev[-1]), encoding="utf8"))["resultados"] if prev else []
    cur, old = tabla(rows), tabla(prev_rows)
    asistentes = list(models)
    L = [f"# AI visibilidad: Tres Naranjos", "", f"Última corrida: {today}. Modelos: "
         + ", ".join(f"{k} = {v}" for k, v in models.items()) + ".", ""]
    for a in asistentes:
        n = sum(cur[k][0] for k in cur if k[0] == a); t = sum(cur[k][2] for k in cur if k[0] == a)
        c = sum(cur[k][1] for k in cur if k[0] == a); rc = sum(cur[k][3] for k in cur if k[0] == a)
        line = f"- **{a}:** nombrado en {n} de {t} respuestas, reconocido como el licor en {rc}; tresnaranjos.com citado en {c}."
        if old:
            on = sum(old[k][0] for k in old if k[0] == a); ot = sum(old[k][2] for k in old if k[0] == a)
            line += f" Antes ({prev[-1][:10]}): {on} de {ot}."
        L.append(line)
    L += ["", "Celdas: respuestas que reconocen a Tres Naranjos como el licor / corridas.", "",
          "| Pregunta | " + " | ".join(asistentes) + " |", "|---|" + "---|" * len(asistentes)]
    for q, _ in PREGUNTAS:
        cells = []
        for a in asistentes:
            n, c, t, rc = cur.get((a, q), (0, 0, 0, 0))
            s = f"{rc}/{t}" + (f" (nombrado {n})" if n != rc else "") + (" · cita" if c else "")
            if old and (a, q) in old:
                s += f" (antes {old[(a, q)][3]}/{old[(a, q)][2]})"
            cells.append(s)
        L.append(f"| {q} | " + " | ".join(cells) + " |")
    comp = {}
    for r in rows:
        for c in r["competencia"]:
            comp[c] = comp.get(c, 0) + 1
    if comp:
        L += ["", "Otras marcas nombradas: " + ", ".join(f"{k} ({v})" for k, v in sorted(comp.items(), key=lambda x: -x[1])) + "."]
    precios = sorted({p for r in rows for p in r["precio"] if r["nombrado"]})
    if precios:
        L += ["", "Precios que dice la AI para Tres Naranjos: " + ", ".join(precios) + " (verificar)."]
    fuentes = {}
    for r in rows:
        for u in r["otras_fuentes"]:
            d = re.sub(r"^https?://(www\.)?", "", u).split("/")[0]
            fuentes[d] = fuentes.get(d, 0) + 1
    top = sorted(fuentes.items(), key=lambda x: -x[1])[:12]
    if top:
        L += ["", "Dónde busca la AI (dominios más citados): " + ", ".join(f"{d} ({n})" for d, n in top) + "."]
    L += ["", "Respuestas completas: tools/ai-visibilidad/" + today + ".json"]
    with open(os.path.join(OUT, "resumen.md"), "w", encoding="utf8") as f:
        f.write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
