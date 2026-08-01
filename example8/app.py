import os
from crewai import Agent, Crew, Task, LLM
from crewai.flow.flow import Flow, listen, router, start
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

# Configurar el LLM local amb la classe nativa de CrewAI
llm_local = LLM(
    model=os.getenv("MODEL"),
    base_url=os.getenv("OPENAI_BASE"),
    api_key=os.getenv("OPENAI_APIKEY"),
    temperature=0.2,
    default_headers={"User-Agent": "curl/8.0"},
)

triador = Agent(
    role="Triador d'Incidències",
    goal="Classificar la urgència d'una incidència tècnica.",
    backstory="Ets un operador de guàrdia que classifica incidències en 'urgent' o 'normal'.",
    llm=llm_local,
    verbose=True,
)


# Diferència amb example1-7: aquí no hi ha un únic Crew amb tasques
# encadenades. Flow orquestra per events/estat: cada mètode s'executa
# quan el previ emet un resultat, i @router permet bifurcar l'execució
# segons aquest resultat (aquí: urgent vs normal), enlloc de seguir
# sempre la mateixa seqüència fixa de Process.sequential.
class EstatTriatge(BaseModel):
    incidencia: str = ""
    resultat: str = ""


class FlowTriatge(Flow[EstatTriatge]):
    @start()
    def rebre_incidencia(self):
        self.state.incidencia = (
            "El servidor de producció no respon a pings des de fa 10 minuts."
        )
        print(f"\n[Flow] Incidència rebuda: {self.state.incidencia}")

    @router(rebre_incidencia)
    def triar_urgencia(self):
        tasca = Task(
            description=(
                f"Classifica aquesta incidència com 'urgent' o 'normal': "
                f"{self.state.incidencia}"
            ),
            expected_output="Una sola paraula: 'urgent' o 'normal'.",
            agent=triador,
        )
        resposta = Crew(agents=[triador], tasks=[tasca]).kickoff()
        return "urgent" if "urgent" in str(resposta).lower() else "normal"

    @listen("urgent")
    def gestionar_urgent(self):
        self.state.resultat = "Escalat immediat a l'equip d'infraestructura (on-call)."
        print(f"[Flow] Camí URGENT: {self.state.resultat}")

    @listen("normal")
    def gestionar_normal(self):
        self.state.resultat = "Registrat al backlog per revisió en horari laboral."
        print(f"[Flow] Camí NORMAL: {self.state.resultat}")


if __name__ == "__main__":
    print("\n=== INICI FLOW DE TRIATGE ===\n")
    flow = FlowTriatge()
    flow.kickoff()
    print("\n=== ESTAT FINAL ===\n")
    print(flow.state)
