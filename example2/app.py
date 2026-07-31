import os
from crewai import Agent, Crew, LLM, Process, Task
from crewai.tools import tool
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

# 2. Definim una "Eina" que permet al Director crear un Agent Especialitzat a mida
@tool("Crear i Executar Agent Especialitzat")
def crear_i_executar_agent(rol: str, objectiu: str, instruccions_tasca: str) -> str:
    """Crea un nou agent especialitzat a mesura amb un rol i objectiu concrets,
    li assigna una tasca i retorna el resultat."""
    
    # Es crea l'agent dinàmicament
    agent_dinamic = Agent(
        role=rol,
        goal=objectiu,
        backstory=f"Ets un expert creat específicament per a la feina de: {rol}.",
        llm=llm_local,
        verbose=True
    )
    
    # Es crea la tasca per a aquest agent
    tasca_dinamica = Task(
        description=instruccions_tasca,
        expected_output="Un resultat detallat i d'alta qualitat basat en la petició.",
        agent=agent_dinamic
    )
    
    # S'executa un mini-equip d'un sol agent de forma immediata
    sub_crew = Crew(
        agents=[agent_dinamic],
        tasks=[tasca_dinamica],
        verbose=True
    )
    
    return str(sub_crew.kickoff())

# 3. Agent Director / Coordenador
director = Agent(
    role="Director d'Operacions i Projectes",
    goal="Analitzar problemes complexos, decidir quins perfils d'experts es necessiten i delegar-los la feina.",
    backstory="""Ets un gestor de projectes d'elit. Mai fas la feina directament. 
    En comptes d'això, crees agents especialitzats utilitzant la teva eina 'Crear i Executar Agent Especialitzat' 
    per a cada part del problema.""",
    tools=[crear_i_executar_agent],
    llm=llm_local,
    verbose=True
)

# 4. Tasca principal oberta
tasca_principal = Task(
    description="""Necessito un informe d'auditoria sobre la seguretat d'un servidor web Linux. 
    Analitza quins perfils d'experts necessites per fer aquesta auditoria (p. ex. un expert en xarxes, un expert en permisos de fitxers, etc.), 
    crea'ls dinàmicament utilitzant l'eina disponible i recopila les seves respostes en un informe final.""",
    expected_output="Un informe d'auditoria global basat en la feina dels experts creats.",
    agent=director
)

# 5. Execució
equip_director = Crew(
    agents=[director],
    tasks=[tasca_principal],
    process=Process.sequential,
    verbose=True
)

print("\n=== INICI DE L'ORQUESTRACIÓ DINÀMICA ===\n")
resultat = equip_director.kickoff()
print("\n=== RESULTAT FINAL DE L'INFORME ===\n")
print(resultat)