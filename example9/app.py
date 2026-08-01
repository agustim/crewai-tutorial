import os
from typing import Any, Tuple

from crewai import Agent, Crew, LLM, Process, Task
from crewai.tasks.task_output import TaskOutput
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

generador = Agent(
    role="Generador de Slogans",
    goal="Crear slogans curts per campanyes de marketing.",
    backstory="Ets un copywriter creatiu especialitzat en frases curtes i impactants.",
    llm=llm_local,
    verbose=True,
)


# Guardrail: funció Python (no una tasca d'LLM) que valida l'output abans
# que CrewAI el doni per bo. Retorna (True, resultat_validat) si passa, o
# (False, missatge_error) si no. Si falla, CrewAI torna a executar la
# Task passant el missatge d'error a l'agent, fins a guardrail_max_retries.
def validar_slogan(output: TaskOutput) -> Tuple[bool, Any]:
    text = output.raw.strip()
    paraules = text.split()
    if len(paraules) > 8:
        return False, f"Massa llarg ({len(paraules)} paraules). Ha de tenir 8 paraules o menys."
    if not text.strip():
        return False, "El slogan no pot ser buit."
    return True, text


tasca_slogan = Task(
    description="Crea un slogan per una marca de cafè d'especialitat anomenada 'Nord'.",
    expected_output="Un slogan de màxim 8 paraules.",
    agent=generador,
    guardrail=validar_slogan,
    guardrail_max_retries=3,
)

equip = Crew(
    agents=[generador],
    tasks=[tasca_slogan],
    process=Process.sequential,
    verbose=True,
)

if __name__ == "__main__":
    print("\n=== INICI (amb guardrail de longitud) ===\n")
    resultat = equip.kickoff()
    print("\n=== SLOGAN VALIDAT ===\n")
    print(resultat)
