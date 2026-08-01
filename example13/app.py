import os
from crewai import Agent, Crew, LLM, Process, Task
from crewai.tools import BaseTool
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


# Diferència amb @tool (example2/example4): una classe BaseTool permet
# definir args_schema, un schema Pydantic que valida els arguments que
# l'LLM proposa ABANS d'executar _run(). Si l'LLM envia un tipus o rang
# invàlid, falla la validació enlloc d'arribar a la lògica de la tool.
class InputCalculadoraDescompte(BaseModel):
    preu: float = Field(description="Preu original en euros, ha de ser positiu.")
    percentatge: int = Field(description="Percentatge de descompte, entre 0 i 100.", ge=0, le=100)


class CalculadoraDescompte(BaseTool):
    name: str = "Calculadora de Descompte"
    description: str = "Calcula el preu final aplicant un percentatge de descompte a un preu."
    args_schema: type[BaseModel] = InputCalculadoraDescompte

    def _run(self, preu: float, percentatge: int) -> str:
        if preu <= 0:
            return "Error: el preu ha de ser positiu."
        final = preu * (1 - percentatge / 100)
        return f"Preu final: {final:.2f}€ (descompte de {percentatge}% sobre {preu:.2f}€)"


venedor = Agent(
    role="Assessor de Vendes",
    goal="Calcular preus finals amb descompte per clients.",
    backstory="Ets un assessor comercial que sempre calcula els descomptes amb l'eina, mai de cap.",
    tools=[CalculadoraDescompte()],
    llm=llm_local,
    verbose=True,
)

tasca_descompte = Task(
    description="Un producte val 149.90€. Calcula el preu final amb un 20% de descompte.",
    expected_output="El preu final calculat amb l'eina, explicat en una frase.",
    agent=venedor,
)

equip = Crew(
    agents=[venedor],
    tasks=[tasca_descompte],
    process=Process.sequential,
    verbose=True,
)

if __name__ == "__main__":
    print("\n=== INICI (custom tool amb args_schema) ===\n")
    resultat = equip.kickoff()
    print("\n=== RESULTAT FINAL ===\n")
    print(resultat)
