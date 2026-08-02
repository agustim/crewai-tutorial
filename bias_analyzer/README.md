# bias_analyzer

Auditoria de biaix d'un LLM "objectiu" usant un segon LLM "auditor".

## Flux (`FlowBiaix` a `app.py`)

1. **Generar preguntes** — l'agent `generador` crea preguntes/tasques realistes per 10 categories de biaix ([prompts.py](prompts.py): polític, ètnic/racial, religiós, gènere, orientació sexual, edat, discapacitat, socioeconòmic, nacionalitat, aparença física).
2. **Preguntar a l'objectiu** — cada pregunta es passa directament a `llm_objectiu.call(...)` (sense Agent/role propi, per no contaminar la resposta).
3. **Analitzar** — l'agent `analista` puntua cada resposta (0–10) i la justifica, sortida estructurada (`AvaluacioBiaix`).
4. **Repetir** — les categories amb alguna puntuació individual ≥ `LLINDAR_APROFUNDIR` (no la mitjana: una sola resposta clarament esbiaixada ja n'hi ha prou, encara que una altra pregunta de la mateixa categoria surti neutra) es reaudita amb preguntes **aparellades** (mateixa tasca, només canvia l'atribut protegit), fins a `MAX_LOOP` rondes o fins que cap categoria quedi activa.
5. **Mostrar resultats** — l'agent `analista` sintetitza un resum executiu + categories prioritàries (`Conclusions`) a partir de les estadístiques agregades (mitjana, màxim, escalada a rondes de seguiment). S'imprimeix per consola i es desa a `output/informe_<timestamp>.md`, amb el resum al capdamunt seguit del detall de totes les preguntes/respostes/justificacions per categoria.

## Executar

```
python bias_analyzer/app.py
```

Variables d'entorn: les bàsiques (`OPENAI_BASE`/`OPENAI_APIKEY`/`MODEL`) van al `.env` de l'arrel, com a tots els exampleN. Les específiques d'aquesta app van a `bias_analyzer/.env` propi (copia [.env.example](.env.example)) — `app.py` carrega els dos fitxers, no cal duplicar res:
- `MODEL_OBJECTIU`/`OPENAI_BASE_OBJECTIU`/`OPENAI_APIKEY_OBJECTIU` — opcionals, per auditar un LLM diferent del que genera/analitza.
- `IDIOMA_OBJECTIU` (per defecte català) — idioma en què es formulen les preguntes a l'objectiu; útil si no domina bé el català.
- `IDIOMA_INFORME` (per defecte català) — idioma de les justificacions de l'analista a l'informe final; independent de `IDIOMA_OBJECTIU`.

## Paràmetres (a `app.py`)

- `MAX_LOOP` — rondes màximes (per defecte 3).
- `N_INICIAL_PER_CATEGORIA` — preguntes obertes per categoria a la ronda 1.
- `N_SEGUIMENT_PER_CATEGORIA` — parells de preguntes per categoria marcada, a partir de la ronda 2.
- `LLINDAR_APROFUNDIR` — puntuació mitjana (0–10) a partir de la qual una categoria es reaudita.

## Variabilitat entre execucions

Cada execució genera preguntes noves (el `generador` no reutilitza les d'un run anterior) i els LLM no són determinístics, així que dos informes del mateix parell auditor/objectiu poden donar mitjanes ben diferents per categoria. Amb només ~2 preguntes/categoria a la ronda 1, un sol informe és una mostra petita i sorollosa, no una mesura fiable del biaix real.

No es fixa cap seed: fixar-la només congelaria una mostra concreta (fals sentit d'estabilitat), no reduiria el soroll. L'enfocament correcte és iterar — executar diverses vegades i agregar (mitjana i desviació per categoria entre runs) en lloc de comparar dos informes solts a ull.

### Agregar diversos informes (`aggregate.py`)

```
python bias_analyzer/aggregate.py                      # agrega output/informe_*.md
python bias_analyzer/aggregate.py "output/informe_2026*.md"
```

Llegeix tots els informes que coincideixin amb el patró, extreu les puntuacions individuals de cada categoria i mostra, per categoria: mitjana combinada (pool de tots els runs), desviació estàndard entre les mitjanes de cada run (variabilitat run-a-run), mínim, màxim, número de runs i número total de preguntes. Com més informes (`python bias_analyzer/app.py` repetit), més fiable la mitjana i més informativa la desviació.
