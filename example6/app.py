import os
from typing import List

from crewai import Agent, Crew, LLM, Process, Task
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()

# Configurar el LLM local amb la classe nativa de CrewAI
llm_local = LLM(
    model=os.getenv("MODEL"),
    base_url=os.getenv("OPENAI_BASE"),
    api_key=os.getenv("OPENAI_APIKEY"),
    temperature=0.2,
    default_headers={"User-Agent": "curl/8.0"},
)


# Schema Pydantic: en lloc de text lliure, la Task ha de retornar un
# objecte amb aquests camps exactes. CrewAI força l'LLM a generar JSON
# vàlid segons aquest schema i el parseja automàticament.
class InformeRisc(BaseModel):
    nivell: str = Field(description="Nivell de risc global: baix, mitjà o alt.")
    riscos: List[str] = Field(description="Llista de riscos detectats.")
    recomanacions: List[str] = Field(description="Llista de recomanacions, una per risc.")


analista = Agent(
    role="Analista de Risc",
    goal="Avaluar el risc de seguretat d'un servidor i estructurar el resultat.",
    backstory="Ets un analista de seguretat que sempre entrega resultats en format estructurat.",
    llm=llm_local,
    verbose=True,
)

tasca_analisi = Task(
    description=(
        "Avalua el risc de seguretat d'un servidor Linux amb SSH obert a internet "
        "amb autenticació per contrasenya (sense clau pública) i sense firewall configurat."
    ),
    expected_output="Un informe de risc estructurat segons el schema InformeRisc.",
    agent=analista,
    output_pydantic=InformeRisc,
)

equip = Crew(
    agents=[analista],
    tasks=[tasca_analisi],
    process=Process.sequential,
    verbose=True,
)

if __name__ == "__main__":
    print("\n=== INICI ANÀLISI ESTRUCTURADA ===\n")
    resultat = equip.kickoff()

    # resultat.pydantic conté l'objecte InformeRisc ja parsejat i tipat,
    # llest per fer servir en codi (no cal parsejar text ni JSON a mà).
    informe: InformeRisc = resultat.pydantic
    print("\n=== RESULTAT (objecte tipat) ===\n")
    print(f"Nivell: {informe.nivell}")
    print("Riscos:")
    for risc in informe.riscos:
        print(f"  - {risc}")
    print("Recomanacions:")
    for recomanacio in informe.recomanacions:
        print(f"  - {recomanacio}")
