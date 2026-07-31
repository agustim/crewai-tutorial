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

# Diferència amb example2: aquí no hi ha cap tool manual de delegació.
# Process.hierarchical afegeix un manager intern (LLM) que decideix ell
# mateix a quin agent assignar cada tasca i en quin ordre, sense que el
# codi ho fixi ni que calgui programar-ho amb una tool.

xarxes = Agent(
    role="Expert en Xarxes",
    goal="Detectar riscos de seguretat relacionats amb ports oberts i configuració de xarxa.",
    backstory="Ets un expert en hardening de xarxes en servidors Linux.",
    llm=llm_local,
    verbose=True,
)

permisos = Agent(
    role="Expert en Permisos de Fitxers",
    goal="Detectar riscos de seguretat relacionats amb permisos de fitxers i usuaris.",
    backstory="Ets un expert en control d'accessos i permisos Unix.",
    llm=llm_local,
    verbose=True,
)

redactor = Agent(
    role="Redactor d'Informes",
    goal="Consolidar troballes tècniques en un informe final clar.",
    backstory="Ets un redactor tècnic especialitzat en informes d'auditoria de seguretat.",
    llm=llm_local,
    verbose=True,
)

# Tasques sense agent assignat: el manager del Process.hierarchical
# decideix a qui delegar cadascuna en temps d'execució.
tasca_xarxes = Task(
    description="Analitza els riscos de seguretat de xarxa d'un servidor Linux exposat a internet.",
    expected_output="Llista de 3 riscos de xarxa amb mitigació.",
)

tasca_permisos = Task(
    description="Analitza els riscos de seguretat de permisos de fitxers en un servidor Linux multiusuari.",
    expected_output="Llista de 3 riscos de permisos amb mitigació.",
)

tasca_informe = Task(
    description="Consolida les troballes anteriors en un informe d'auditoria final únic.",
    expected_output="Informe en Markdown amb seccions Xarxa i Permisos.",
)

equip = Crew(
    agents=[xarxes, permisos, redactor],
    tasks=[tasca_xarxes, tasca_permisos, tasca_informe],
    process=Process.hierarchical,
    manager_llm=llm_local,
    verbose=True,
)

if __name__ == "__main__":
    print("\n=== INICI AUDITORIA (PROCESS.HIERARCHICAL) ===\n")
    resultat = equip.kickoff()
    print("\n=== RESULTAT FINAL ===\n")
    print(resultat)
