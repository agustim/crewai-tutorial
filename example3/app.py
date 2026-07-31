import os
import sys
from crewai import Agent, Crew, LLM, Process, Task
from dotenv import load_dotenv

load_dotenv()

# Nom fix de la carpeta d'emmagatzematge de CrewAI (SQLite + Chroma).
# En fixar-lo, la memòria persisteix entre execucions diferents d'aquest script.
os.environ["CREWAI_STORAGE_DIR"] = "orquestador-agents-memoria"

# Configurar el LLM local amb la classe nativa de CrewAI
llm_local = LLM(
    model=os.getenv("MODEL"),
    base_url=os.getenv("OPENAI_BASE"),
    api_key=os.getenv("OPENAI_APIKEY"),
    temperature=0.2,
    default_headers={"User-Agent": "curl/8.0"},
)

# CrewAI necessita un model d'embeddings per a la memòria (short-term/entity).
# sentence-transformer corre 100% local en CPU: no cal API key ni servei extern.
embedder_config = {
    "provider": "sentence-transformer",
    "config": {
        "model_name": os.getenv("EMBED_MODEL", "all-MiniLM-L6-v2"),
        "device": "cpu",
    },
}

cronista = Agent(
    role="Cronista del Projecte",
    goal="Registrar i recordar decisions tècniques preses sobre els projectes.",
    backstory="Ets la memòria viva de l'equip: recordes cada decisió sense que ningú l'hagi de repetir.",
    llm=llm_local,
    verbose=True,
)


def registra():
    """Crew A: desa un fet a la memòria persistent de CrewAI."""
    tasca = Task(
        description=(
            "Registra aquesta decisió: el projecte 'Apolo' fa servir PostgreSQL 15 "
            "com a base de dades principal i Redis com a capa de cache."
        ),
        expected_output="Confirmació breu del fet registrat.",
        agent=cronista,
    )
    crew = Crew(agents=[cronista], tasks=[tasca], memory=True, embedder=embedder_config, verbose=True)
    return crew.kickoff()


def consulta():
    """Crew B: nova instància de Crew, sense context explícit.
    Ha de respondre nomes gràcies a la memòria persistida per registra()."""
    tasca = Task(
        description="Quina base de dades i quina cache fa servir el projecte 'Apolo'?",
        expected_output="El nom de la base de dades i de la cache del projecte 'Apolo'.",
        agent=cronista,
    )
    crew = Crew(agents=[cronista], tasks=[tasca], memory=True, embedder=embedder_config, verbose=True)
    return crew.kickoff()


def cadena():
    """Un sol Crew amb 3 tasques: mostra context selectiu entre tasques
    (t3 només depèn de t1, encara que t2 s'executa entremig)."""
    t1 = Task(
        description="Defineix en una frase els requisits tècnics del projecte 'Apolo'.",
        expected_output="Una frase amb els requisits tècnics.",
        agent=cronista,
    )
    t2 = Task(
        description="Tradueix el nom 'Apolo' a l'anglès. (Tasca independent, no la necessitem després.)",
        expected_output="El nom traduït.",
        agent=cronista,
    )
    t3 = Task(
        description="A partir només dels requisits tècnics definits, escriu el títol d'una fitxa de projecte.",
        expected_output="Un títol curt de fitxa de projecte.",
        agent=cronista,
        context=[t1],  # ignora deliberadament el resultat de t2
    )
    crew = Crew(agents=[cronista], tasks=[t1, t2, t3], process=Process.sequential, verbose=True)
    return crew.kickoff()


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "registra"

    accions = {"registra": registra, "consulta": consulta, "cadena": cadena}
    if mode not in accions:
        print(f"Mode desconegut: {mode}. Opcions: {list(accions)}")
        sys.exit(1)

    print(f"\n=== EXECUTANT MODE: {mode} ===\n")
    resultat = accions[mode]()
    print(f"\n=== RESULTAT ({mode}) ===\n")
    print(resultat)
