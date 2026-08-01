import os
from crewai import Agent, Crew, LLM, Process, Task
from crewai.project import CrewBase, agent, crew, task, tool as tool_method
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
    default_headers={"User-Agent": "curl/8.0"},
)


# Mateix Crew que example4 (investigador_web + guionista + eina de cerca), però
# role/goal/backstory/description/expected_output viuen a config/agents.yaml i
# config/tasks.yaml (patró oficial de `crewai create crew`), enlloc de strings
# dins el Python. @agent/@task marquen els mètodes que produeixen cada peça,
# @tool_method (crewai.project.tool) marca la tool perquè `tools: [cerca_web]`
# a agents.yaml la resolgui pel nom del mètode, i @crew ensambla tot fent
# servir self.agents/self.tasks (llistes que CrewBase omple automàticament).
@CrewBase
class InvestigacioCrew:
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    # @tool_method (crewai.project.tool) és una factory, com @agent/@task: es
    # crida sense arguments i ha de retornar la Tool ja construïda (aquí amb
    # el decorador @tool de crewai.tools, igual que example2/example4).
    @tool_method
    def cerca_web(self):
        @tool("Cerca a Internet")
        def _cerca_web(consulta: str) -> str:
            """Cerca la consulta a internet i retorna els títols, enllaços i
            fragments dels resultats més rellevants."""
            resultats = DDGS().text(consulta, max_results=5)
            if not resultats:
                return "Cap resultat trobat."
            return "\n\n".join(
                f"Títol: {r['title']}\nURL: {r['href']}\nResum: {r['body']}" for r in resultats
            )

        return _cerca_web

    @agent
    def investigador_web(self) -> Agent:
        return Agent(config=self.agents_config["investigador_web"], llm=llm_local, verbose=True)

    @agent
    def guionista(self) -> Agent:
        return Agent(config=self.agents_config["guionista"], llm=llm_local, verbose=True)

    @task
    def tasca_investigacio(self) -> Task:
        return Task(config=self.tasks_config["tasca_investigacio"])

    @task
    def tasca_guionista(self) -> Task:
        return Task(config=self.tasks_config["tasca_guionista"])

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )


if __name__ == "__main__":
    tema = os.getenv("TEMA", "les novetats de CrewAI el 2026")
    print(f"\n=== INICI (config YAML), tema: {tema} ===\n")
    resultat = InvestigacioCrew().crew().kickoff(inputs={"tema": tema})
    print("\n=== RESULTAT FINAL ===\n")
    print(resultat)
