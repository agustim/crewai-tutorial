# Orquestador d'agents (CrewAI)

Sèrie d'exemples progressius per aprendre orquestració multi-agent amb [CrewAI](https://docs.crewai.com/). Testejat amb `crewai==1.15.9`.

## Índex

| # | Exemple | Concepte |
|---|---------|----------|
| 1 | [example1](example1/app.py) | Crew estàtica seqüencial |
| 2 | [example2](example2/app.py) | Creació dinàmica d'agents |
| 3 | [example3](example3/app.py) | Memòria persistent i context selectiu |
| 4 | [example4](example4/app.py) | Eina real (cerca a internet) |
| 5 | [example5](example5/app.py) | `Process.hierarchical` |
| 6 | [example6](example6/app.py) | Output estructurat (Pydantic) |
| 7 | [example7](example7/app.py) | Human-in-the-loop |
| 8 | [example8](example8/app.py) | CrewAI Flow |
| 9 | [example9](example9/app.py) | Guardrails |
| 10 | [example10](example10/app.py) | Tasques asíncrones/paral·leles |
| 11 | [example11](example11/app.py) | Config YAML (`@CrewBase`) |
| 12 | [example12](example12/app.py) | Knowledge / RAG |
| 13 | [example13](example13/app.py) | Custom Tool (`args_schema`) |

## Apps

Fora de la sèrie `exampleN` (aprenentatge d'un concepte aïllat): eines completes que combinen diversos conceptes per fer alguna cosa útil.

| App | Concepte |
|---|---|
| [bias_analyzer](bias_analyzer/app.py) | Auditoria de biaix d'un LLM (Flow amb bucle generar→preguntar→analitzar→decidir) |

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

```
python example1/app.py
```

### example2 — Director amb creació dinàmica d'agents
Un sol agent "Director" no fa la feina ell mateix: té una tool (`crear_i_executar_agent`) que li permet crear agents especialitzats a mida (rol, objectiu, tasca) en temps d'execució i llançar un mini-Crew per cadascun. Mostra orquestració dinàmica controlada per un LLM enlloc d'una topologia fixa de codi.

```
python example2/app.py
```

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

```
python example5/app.py
```

### example6 — Output estructurat (Pydantic)
Una `Task` amb `output_pydantic=InformeRisc` força l'LLM a retornar JSON vàlid segons un schema Pydantic (`nivell`, `riscos`, `recomanacions`) enlloc de text lliure. `resultat.pydantic` dona directament l'objecte tipat, sense parsejar text a mà. Útil quan el resultat d'un Crew ha d'alimentar altre codi.

```
python example6/app.py
```

### example7 — Human-in-the-loop
Una `Task` amb `human_input=True`: en acabar, CrewAI pregunta per terminal si el resultat és correcte. Si es dona feedback enlloc de confirmar, l'agent repeteix la tasca incorporant-lo, fins que s'aprova. Requereix terminal interactiu.

```
python example7/app.py
```

### example8 — CrewAI Flow (orquestració per events/estat)
Diferent de Crew+Process (ex1-7): `Flow` encadena mètodes per events amb `@start`/`@router`/`@listen` sobre un estat tipat (Pydantic). `triar_urgencia` fa servir un mini-Crew per classificar una incidència i `@router` bifurca cap a `gestionar_urgent` o `gestionar_normal` segons el resultat, en lloc de seguir sempre la mateixa seqüència fixa.

```
python example8/app.py
```

### example9 — Guardrails
Una `Task` amb `guardrail=validar_slogan`: funció Python (no un altre LLM) que rep el `TaskOutput` i retorna `(True, resultat)` o `(False, missatge_error)`. Si falla, CrewAI reexecuta la tasca passant l'error a l'agent, fins a `guardrail_max_retries`. Aquí valida que el slogan tingui 8 paraules o menys.

```
python example9/app.py
```

### example10 — Tasques asíncrones/paral·leles
Dues tasques independents (`tasca_vendes`, `tasca_clients`) amb `async_execution=True` s'executen alhora enlloc de seqüencialment. Una tercera tasca (`tasca_informe`) depèn de totes dues via `context=[...]`, per tant espera que ambdues acabin abans de començar.

```
python example10/app.py
```

### example11 — Config YAML (`@CrewBase`)
Mateix Crew que example4 (`investigador_web` + `guionista` + eina `cerca_web`), però amb `role`/`goal`/`backstory`/`description`/`expected_output` definits a `config/agents.yaml` i `config/tasks.yaml` (patró oficial de `crewai create crew`), enlloc de strings dins el Python. `@agent`/`@task` marquen els mètodes que produeixen cada peça, `@tool` (de `crewai.project`) marca la tool perquè `tools: [cerca_web]` a `agents.yaml` la resolgui pel nom, i `@crew` ensambla tot.

```
uv pip install ddgs
TEMA="el teu tema" python example11/app.py
```

### example12 — Knowledge / RAG
L'agent `assistent_rh` té una `StringKnowledgeSource` amb la política interna de vacances de l'empresa (informació que l'LLM no coneix). CrewAI la indexa (embeddings, igual que la memòria d'example3) i la injecta automàticament al context quan és rellevant. Diferència amb example4: aquí no hi ha una tool de cerca activa, el coneixement ja està "adjuntat" a l'agent. Requereix `sentence-transformers` (ja instal·lat per example3).

```
python example12/app.py
```

### example13 — Custom Tool (`BaseTool` + `args_schema`)
`CalculadoraDescompte` és una classe `BaseTool` (enlloc del decorador `@tool` d'example2/4) amb `args_schema` en Pydantic (`preu: float`, `percentatge: int` amb `ge=0, le=100`). CrewAI valida els arguments que proposa l'LLM contra aquest schema abans d'executar `_run()`.

```
python example13/app.py
```
