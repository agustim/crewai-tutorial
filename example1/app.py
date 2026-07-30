import os
from crewai import Agent, Crew, LLM, Process, Task
from dotenv import load_dotenv

load_dotenv()

# Configurar el LLM local amb la classe nativa de CrewAI
llm_local = LLM(
    model=os.getenv("MODEL"),
    base_url=os.getenv("OPENAI_BASE"),
    api_key=os.getenv("OPENAI_APIKEY"),
    temperature=0.2,
)

# 2. Definir els agents amb rols específics
investigador = Agent(
    role="Investigador de Mercat",
    goal="Trobar les tendències principals sobre el futbol",
    backstory="Ets un analista de dades expert a identificar patrons i resums clau.",
    verbose=True,
    llm=llm_local,
)

redactor = Agent(
    role="Redactor Tècnic",
    goal="Convertir resums d'investigació en articles clars i estructurats",
    backstory="Ets un escriptor especialitzat a explicar conceptes complexos de forma senzilla.",
    verbose=True,
    llm=llm_local,
)

# 3. Definir les tasques
tasca_investigacio = Task(
    description="Analitza els beneficis principals de les estructures de defensa i atac del futbol.",
    expected_output="Una llista amb 3 punts clau i explicació de cadascun.",
    agent=investigador,
)

tasca_redaccio = Task(
    description="Escriu una breu publicació de blog a partir dels punts de l'investigador.",
    expected_output="Un article de 3 paràgrafs en format Markdown.",
    agent=redactor,
)

# 4. Orquestrar l'equip (Crew)
equip = Crew(
    agents=[investigador, redactor],
    tasks=[tasca_investigacio, tasca_redaccio],
    process=Process.sequential,
    verbose=True,
)

# 5. Executar i veure el resultat
resultat = equip.kickoff()
print("\n=== RESULTAT FINAL ===\n")
print(resultat)