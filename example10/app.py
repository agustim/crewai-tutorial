import os
import time
from crewai import Agent, Crew, LLM, Process, Task
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

analista_vendes = Agent(
    role="Analista de Vendes",
    goal="Analitzar tendències de vendes.",
    backstory="Ets un analista financer especialitzat en dades de vendes.",
    llm=llm_local,
    verbose=True,
)

analista_clients = Agent(
    role="Analista de Clients",
    goal="Analitzar el comportament dels clients.",
    backstory="Ets un analista especialitzat en satisfacció i retenció de clients.",
    llm=llm_local,
    verbose=True,
)

redactor = Agent(
    role="Redactor d'Informes",
    goal="Consolidar anàlisis en un informe final.",
    backstory="Ets un redactor tècnic que combina dades de diverses fonts en un sol informe.",
    llm=llm_local,
    verbose=True,
)

# async_execution=True: aquestes dues tasques es llancen alhora (fils
# separats) enlloc d'esperar que una acabi per començar l'altra. Com que
# no depenen l'una de l'altra, no hi ha guany fer-les seqüencials.
tasca_vendes = Task(
    description="Analitza en 2 frases la tendència de vendes del darrer trimestre (dades fictícies raonables).",
    expected_output="2 frases sobre tendència de vendes.",
    agent=analista_vendes,
    async_execution=True,
)

tasca_clients = Task(
    description="Analitza en 2 frases el comportament de clients del darrer trimestre (dades fictícies raonables).",
    expected_output="2 frases sobre comportament de clients.",
    agent=analista_clients,
    async_execution=True,
)

# Aquesta tasca NO és async: depèn de les dues anteriors via `context`,
# per tant CrewAI espera que ambdues acabin abans d'executar-la.
tasca_informe = Task(
    description="Combina les dues anàlisis anteriors en un informe únic de 4 frases.",
    expected_output="Informe de 4 frases combinant vendes i clients.",
    agent=redactor,
    context=[tasca_vendes, tasca_clients],
)

equip = Crew(
    agents=[analista_vendes, analista_clients, redactor],
    tasks=[tasca_vendes, tasca_clients, tasca_informe],
    process=Process.sequential,
    verbose=True,
)

if __name__ == "__main__":
    inici = time.time()
    print("\n=== INICI (tasques 1 i 2 en paral·lel) ===\n")
    resultat = equip.kickoff()
    print(f"\n=== RESULTAT FINAL (temps total: {time.time() - inici:.1f}s) ===\n")
    print(resultat)
