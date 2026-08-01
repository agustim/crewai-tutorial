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
    default_headers={"User-Agent": "curl/8.0"},
)

redactor = Agent(
    role="Redactor de Comunicats",
    goal="Redactar comunicats interns clars i concisos.",
    backstory="Ets un redactor corporatiu que sempre accepta feedback per millorar el text.",
    llm=llm_local,
    verbose=True,
)

# human_input=True: en acabar la tasca, CrewAI atura l'execució i pregunta
# per terminal si el resultat és correcte. Si es respon amb feedback
# (enlloc de confirmar), l'agent torna a executar la tasca incorporant-lo,
# i repeteix el cicle fins que el humà l'aprova. Requereix terminal
# interactiu (no funciona en un script totalment desatès).
tasca_comunicat = Task(
    description=(
        "Redacta un comunicat intern breu anunciant que demà hi haurà "
        "manteniment del servidor de correu entre les 22h i les 24h."
    ),
    expected_output="Un comunicat de 3-4 frases, to professional.",
    agent=redactor,
    human_input=True,
)

equip = Crew(
    agents=[redactor],
    tasks=[tasca_comunicat],
    process=Process.sequential,
    verbose=True,
)

if __name__ == "__main__":
    print("\n=== INICI (revisió humana activada) ===\n")
    resultat = equip.kickoff()
    print("\n=== RESULTAT FINAL APROVAT ===\n")
    print(resultat)
