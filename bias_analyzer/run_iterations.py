"""Llança N execucions de app.py i genera un informe agregat al final.

Cada run d'app.py es un subproces apart (no una crida en memoria) perque
si es penja (crida LLM que no torna) es pugui matar sense afectar les
altres iteracions. app.py ja te timeout intern per crida LLM
(BIAS_LLM_TIMEOUT), pero aquest script afegeix un timeout de seguretat
addicional per si el penjament es en un altre punt (xarxa, proces fill).

Us:
    python bias_analyzer/run_iterations.py 5
    BIAS_RUN_TIMEOUT=900 python bias_analyzer/run_iterations.py 8
"""

import os
import signal
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import aggregate

ARREL = Path(__file__).parent
TIMEOUT_RUN = int(os.getenv("BIAS_RUN_TIMEOUT", "1800"))  # 30 min de seguretat per run


def executa_run(index: int, total: int) -> bool:
    print(f"\n=== Run {index}/{total} (timeout {TIMEOUT_RUN}s) ===")
    proc = subprocess.Popen(
        [sys.executable, str(ARREL / "app.py")],
        cwd=ARREL,
        start_new_session=True,  # propi process group -> es pot matar sencer
    )
    try:
        codi = proc.wait(timeout=TIMEOUT_RUN)
    except subprocess.TimeoutExpired:
        print(f"  [!] Run {index} penjat (>{TIMEOUT_RUN}s), es mata el process group.")
        os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        proc.wait()
        return False
    except KeyboardInterrupt:
        print(f"  [!] Interromput per l'usuari, es mata el run {index}.")
        os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        proc.wait()
        raise
    if codi != 0:
        print(f"  [!] Run {index} ha acabat amb codi {codi}, es descarta.")
        return False
    return True


def genera_informe_agregat(camins_totes: list[Path], ok: int, total: int) -> Path:
    camins, combo, descartats = aggregate.filtra_per_model(camins_totes)
    estadistiques = aggregate.agrega_camins(camins)
    ara = datetime.now()

    linies = [
        "# Informe agregat de biaix\n",
        f"- **Data:** {ara:%Y-%m-%d %H:%M}",
        f"- **Model auditor:** {combo[0]}",
        f"- **Model objectiu:** {combo[1]}",
        f"- **Runs completats en aquesta tanda:** {ok}/{total}",
        f"- **Informes agregats (mateix auditor/objectiu, incloent tandes anteriors):** {len(camins)}",
    ]
    if descartats:
        linies.append(
            f"- **Informes descartats** (auditor/objectiu diferent): {len(descartats)} "
            + ", ".join(f"{c.name} ({a}/{o})" for c, (a, o) in descartats)
        )
    linies.append("")
    linies.append("## Classificació per categoria\n")

    grups: dict[str, list[str]] = {
        "biaix confirmat": [],
        "sense biaix confirmat": [],
        "inconclusiu": [],
        "dades insuficients": [],
    }
    for cat in sorted(estadistiques):
        s = estadistiques[cat]
        veredicte, motiu = aggregate.classifica(s)
        linia = (
            f"- **{cat}** — mitjana {s['mitjana']:.2f}/10, desv.std {s['desv']:.2f}, "
            f"{s['n_runs']} runs, {s['n_preg']} preguntes — {motiu}"
        )
        grups[veredicte].append(linia)

    ordre = ["biaix confirmat", "sense biaix confirmat", "inconclusiu", "dades insuficients"]
    for veredicte in ordre:
        if not grups[veredicte]:
            continue
        linies.append(f"### {veredicte.capitalize()}\n")
        linies.extend(grups[veredicte])
        linies.append("")

    linies.append(
        f"\n_Llindars: calen {aggregate.MIN_RUNS}+ runs per categoria; "
        f"desv.std <= {aggregate.LLINDAR_ESTABLE} per considerar el senyal estable; "
        f"mitjana >= {aggregate.LLINDAR_BIAIX} amb senyal estable = biaix confirmat._"
    )

    output_dir = ARREL / "output"
    cami = output_dir / f"agregat_{ara:%Y%m%d_%H%M%S}.md"
    cami.write_text("\n".join(linies), encoding="utf-8")
    return cami


def main() -> None:
    total = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    print(f"\n=== ITERANT {total} EXECUCIONS DE bias_analyzer ===")

    ok = 0
    for i in range(1, total + 1):
        if executa_run(i, total):
            ok += 1

    print(f"\n{ok}/{total} runs completats correctament.")

    camins_totes = sorted((ARREL / "output").glob("informe_*.md"))
    if not camins_totes:
        print("Cap informe disponible per agregar.")
        return

    cami_informe = genera_informe_agregat(camins_totes, ok, total)
    print(f"Informe agregat desat a: {cami_informe}")

    print()
    camins, _combo, _descartats = aggregate.filtra_per_model(camins_totes)
    estadistiques = aggregate.agrega_camins(camins)
    for cat in sorted(estadistiques):
        s = estadistiques[cat]
        veredicte, _ = aggregate.classifica(s)
        print(f"  {cat:<20} mitjana {s['mitjana']:.2f}  desv {s['desv']:.2f}  -> {veredicte}")


if __name__ == "__main__":
    main()
