import os
from crewai import Agent, Crew, LLM, Process, Task
from crewai.knowledge.source.string_knowledge_source import StringKnowledgeSource
from dotenv import load_dotenv

load_dotenv()

# Configurar el LLM local amb la classe nativa de CrewAI
llm_local = LLM(
    model=os.getenv("MODEL"),
    base_url=os.getenv("OPENAI_BASE"),
    api_key=os.getenv("OPENAI_APIKEY"),
    temperature=0.2,
    default_headers={"User-Agent": "curl/8.0"},
)

# Igual que example3, la memòria/knowledge necessita un embedder. Fem servir
# sentence-transformer (100% local, sense API key).
embedder_config = {
    "provider": "sentence-transformer",
    "config": {
        "model_name": os.getenv("EMBED_MODEL", "all-MiniLM-L6-v2"),
        "device": "cpu",
    },
}

# Font de coneixement: text intern de l'empresa que l'LLM NO coneix
# (no és a les seves dades d'entrenament). Diferència amb example4 (tool de
# cerca web): aquí la informació no es "cerca" activament amb una tool,
# sinó que CrewAI la indexa (embeddings) i la injecta automàticament al
# context de l'agent quan és rellevant per la tasca.
politica_vacances = StringKnowledgeSource(
    content=(
        "Política de vacances de l'empresa Nord Robotics (2026): "
        "Cada empleat té 23 dies laborables de vacances a l'any. "
        "Cal demanar-les amb un mínim de 15 dies d'antelació via el portal RH. "
        "Màxim 10 dies consecutius sense aprovació especial del responsable d'equip."
    )
)

assistent_rh = Agent(
    role="Assistent de Recursos Humans",
    goal="Respondre preguntes dels empleats basant-te única i exclusivament en la política interna coneguda.",
    backstory="Ets l'assistent de RH de Nord Robotics: només respons amb dades oficials de l'empresa.",
    llm=llm_local,
    knowledge_sources=[politica_vacances],
    embedder=embedder_config,
    verbose=True,
)

tasca_consulta = Task(
    description=(
        "Un empleat pregunta: quants dies de vacances té a l'any i amb quanta "
        "antelació les ha de demanar? Respon només amb dades de la política interna."
    ),
    expected_output="Resposta breu citant els dies exactes i l'antelació exacta.",
    agent=assistent_rh,
)

equip = Crew(
    agents=[assistent_rh],
    tasks=[tasca_consulta],
    process=Process.sequential,
    verbose=True,
)

if __name__ == "__main__":
    print("\n=== INICI (agent amb knowledge source) ===\n")
    resultat = equip.kickoff()
    print("\n=== RESULTAT FINAL ===\n")
    print(resultat)
