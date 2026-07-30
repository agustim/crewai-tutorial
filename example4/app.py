import os
from crewai import Agent, Crew, LLM, Process, Task
from crewai.tools import tool
from ddgs import DDGS
from dotenv import load_dotenv

load_dotenv()

# Configurar el LLM local amb la classe nativa de CrewAI
llm_local = LLM(
    model=os.getenv("MODEL"),
    base_url=os.getenv("OPENAI_BASE"),
    api_key=os.getenv("OPENAI_APIKEY"),
    temperature=0.2,
)


# Eina real: cerca a internet (DuckDuckGo, sense API key). L'agent deixa de
# "raonar de memòria" i fonamenta la resposta en dades actuals de la web.
@tool("Cerca a Internet")
def cerca_web(consulta: str) -> str:
    """Cerca la consulta a internet i retorna els títols, enllaços i
    fragments dels resultats més rellevants."""
    resultats = DDGS().text(consulta, max_results=5)
    if not resultats:
        return "Cap resultat trobat."
    return "\n\n".join(
        f"Títol: {r['title']}\nURL: {r['href']}\nResum: {r['body']}" for r in resultats
    )


investigador_web = Agent(
    role="Investigador Web",
    goal="Trobar informació actual i verificable a internet abans de respondre.",
    backstory=(
        "Ets un investigador rigorós: mai respons de memòria sobre fets recents, "
        "sempre verifiques primer amb una cerca a internet."
    ),
    tools=[cerca_web],
    llm=llm_local,
    verbose=True,
)

redactor = Agent(
    role="Redactor Tècnic",
    goal="Convertir troballes d'investigació en un resum clar i ben citat.",
    backstory="Ets un escriptor especialitzat a explicar conceptes complexos de forma senzilla, sempre citant les fonts.",
    llm=llm_local,
    verbose=True,
)

tasca_investigacio = Task(
    description=(
        "Cerca a internet informació actual sobre '{tema}'. "
        "Fes servir la teva eina de cerca abans de treure conclusions."
    ),
    expected_output="Una llista de 3-5 fets rellevants, cadascun amb la URL font.",
    agent=investigador_web,
)

tasca_redaccio = Task(
    description="Escriu un resum de 3 paràgrafs sobre '{tema}' a partir dels fets trobats, citant les fonts.",
    expected_output="Un resum en format Markdown amb els enllaços font citats.",
    agent=redactor,
    context=[tasca_investigacio],
)

equip = Crew(
    agents=[investigador_web, redactor],
    tasks=[tasca_investigacio, tasca_redaccio],
    process=Process.sequential,
    verbose=True,
)

if __name__ == "__main__":
    tema = os.getenv("TEMA", "les novetats de CrewAI el 2026")
    print(f"\n=== INICI INVESTIGACIÓ: {tema} ===\n")
    resultat = equip.kickoff(inputs={"tema": tema})
    print("\n=== RESULTAT FINAL ===\n")
    print(resultat)
