# bias_analyzer

Auditoria de biaix d'un LLM "objectiu" usant un segon LLM "auditor".

## Flux (`FlowBiaix` a `app.py`)

1. **Generar preguntes** — l'agent `generador` crea preguntes/tasques realistes per 10 categories de biaix ([prompts.py](prompts.py): polític, ètnic/racial, religiós, gènere, orientació sexual, edat, discapacitat, socioeconòmic, nacionalitat, aparença física).
2. **Preguntar a l'objectiu** — cada pregunta es passa directament a `llm_objectiu.call(...)` (sense Agent/role propi, per no contaminar la resposta).
3. **Analitzar** — l'agent `analista` puntua cada resposta (0–10) i la justifica, sortida estructurada (`AvaluacioBiaix`).
4. **Repetir** — les categories amb puntuació mitjana ≥ `LLINDAR_APROFUNDIR` es reaudita amb preguntes **aparellades** (mateixa tasca, només canvia l'atribut protegit), fins a `MAX_LOOP` rondes o fins que cap categoria quedi activa.
5. **Mostrar resultats** — informe per consola (mitjana per categoria) + Markdown a `output/informe_<timestamp>.md` amb el detall de totes les preguntes/respostes/justificacions.

## Executar

```
python bias_analyzer/app.py
```

Variables d'entorn: veure `.env.example` a l'arrel (`MODEL_OBJECTIU`/`OPENAI_BASE_OBJECTIU`/`OPENAI_APIKEY_OBJECTIU` opcionals si vols auditar un LLM diferent del que genera/analitza).

## Paràmetres (a `app.py`)

- `MAX_LOOP` — rondes màximes (per defecte 3).
- `N_INICIAL_PER_CATEGORIA` — preguntes obertes per categoria a la ronda 1.
- `N_SEGUIMENT_PER_CATEGORIA` — parells de preguntes per categoria marcada, a partir de la ronda 2.
- `LLINDAR_APROFUNDIR` — puntuació mitjana (0–10) a partir de la qual una categoria es reaudita.
