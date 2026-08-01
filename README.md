# Orquestador d'agents (CrewAI)

Sèrie d'exemples progressius per aprendre orquestració multi-agent amb [CrewAI](https://docs.crewai.com/).

## Crear l'entorn

```
uv venv venv_crewai --python 3.12
source venv_crewai/bin/activate
uv pip install crewai langchain-openai
uv pip install python-dotenv
uv pip install sentence-transformers  # només necessari per example3 (memòria)
```

Copia `.env.example` a `.env` i omple:

- `OPENAI_BASE` — URL del proveïdor OpenAI-compatible (litellm, LM Studio, etc.)
- `OPENAI_APIKEY` — API key
- `MODEL` — model de xat (format `provider/model`)
- `EMBED_MODEL` — model d'embeddings local per la memòria de `example3` (per defecte `all-MiniLM-L6-v2`, corre en CPU via `sentence-transformers`, sense API externa)

## Exemples

### example1 — Crew estàtica seqüencial
Dos agents fixos (`investigador`, `redactor`) i dues tasques enllaçades amb `Process.sequential`. El resultat de la primera tasca s'injecta automàticament com a context de la segona. Base de tota la sèrie: com definir Agent/Task/Crew i executar-los.

### example2 — Director amb creació dinàmica d'agents
Un sol agent "Director" no fa la feina ell mateix: té una tool (`crear_i_executar_agent`) que li permet crear agents especialitzats a mida (rol, objectiu, tasca) en temps d'execució i llançar un mini-Crew per cadascun. Mostra orquestració dinàmica controlada per un LLM enlloc d'una topologia fixa de codi.

### example3 — Memòria persistent i context selectiu
Dos mecanismes de compartir informació entre execucions:
- **Memòria entre Crews**: `memory=True` + `CREWAI_STORAGE_DIR` fix fan que un Crew nou (procés diferent) recordi fets registrats per un Crew anterior, sense rebre'ls explícitament. Modes `registra` / `consulta`.
- **Context selectiu dins un Crew**: amb `Task(context=[...])` es pot triar quines tasques prèvies alimenten una tasca concreta, en lloc de dependre només de l'ordre seqüencial. Mode `cadena`.

```
python example3/app.py registra
python example3/app.py consulta
python example3/app.py cadena
```

### example4 — Eines reals (cerca a internet)
L'agent `investigador_web` té una eina real (`cerca_web`, via DuckDuckGo/`ddgs`, sense API key) i l'usa per fonamentar la resposta en dades actuals de la web, en lloc de raonar només amb el coneixement intern del LLM. El `redactor` rep el resultat com a `context` i cita les fonts. Variable `TEMA` (env) o per defecte una de fixa.

```
uv pip install ddgs
TEMA="el teu tema" python example4/app.py
```

### example5 — Process.hierarchical (manager natiu)
Tres agents (`xarxes`, `permisos`, `redactor`) i tres tasques **sense `agent=` fix**. Amb `Process.hierarchical` + `manager_llm`, CrewAI afegeix un manager intern que decideix ell mateix a qui delegar cada tasca i en quin ordre. Contrasta amb example2: allà la delegació la programa una tool manual; aquí és nativa del framework.

### example6 — Output estructurat (Pydantic)
Una `Task` amb `output_pydantic=InformeRisc` força l'LLM a retornar JSON vàlid segons un schema Pydantic (`nivell`, `riscos`, `recomanacions`) enlloc de text lliure. `resultat.pydantic` dona directament l'objecte tipat, sense parsejar text a mà. Útil quan el resultat d'un Crew ha d'alimentar altre codi.

### example7 — Human-in-the-loop
Una `Task` amb `human_input=True`: en acabar, CrewAI pregunta per terminal si el resultat és correcte. Si es dona feedback enlloc de confirmar, l'agent repeteix la tasca incorporant-lo, fins que s'aprova. Requereix terminal interactiu.

```
python example7/app.py
```

### example8 — CrewAI Flow (orquestració per events/estat)
Diferent de Crew+Process (ex1-7): `Flow` encadena mètodes per events amb `@start`/`@router`/`@listen` sobre un estat tipat (Pydantic). `triar_urgencia` fa servir un mini-Crew per classificar una incidència i `@router` bifurca cap a `gestionar_urgent` o `gestionar_normal` segons el resultat, en lloc de seguir sempre la mateixa seqüència fixa.
