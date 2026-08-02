"""Agrega mitjana/desviacio per categoria entre diversos informes de bias_analyzer.

Un sol informe.md es una mostra petita i sorollosa (soroll de mostreig:
preguntes noves cada run + LLM no determinista). Aquest script combina
tots els informes d'output/ per donar una estimacio mes fiable per
categoria, en lloc de comparar dos informes solts a ull.

Us:
    python bias_analyzer/aggregate.py
    python bias_analyzer/aggregate.py "output/informe_2026*.md"
"""

import re
import statistics
import sys
from pathlib import Path

CAPCALERA_CATEGORIA = re.compile(r"^## (\S+) — mitjana")
PUNTUACIO = re.compile(r"puntuacio (\d+)/10")


def parseja_informe(cami: Path) -> dict[str, list[int]]:
    """Retorna {categoria: [puntuacions individuals]} d'un informe."""
    categoria_actual = None
    puntuacions: dict[str, list[int]] = {}
    for linia in cami.read_text(encoding="utf-8").splitlines():
        capcalera = CAPCALERA_CATEGORIA.match(linia)
        if capcalera:
            categoria_actual = capcalera.group(1)
            puntuacions.setdefault(categoria_actual, [])
            continue
        match = PUNTUACIO.search(linia)
        if match and categoria_actual:
            puntuacions[categoria_actual].append(int(match.group(1)))
    return puntuacions


def main() -> None:
    patro = sys.argv[1] if len(sys.argv) > 1 else "output/informe_*.md"
    arrel = Path(__file__).parent
    camins = sorted(arrel.glob(patro)) if not Path(patro).is_absolute() else sorted(Path().glob(patro))
    if not camins:
        print(f"Cap informe trobat amb el patro: {patro}")
        return

    # per_run_mitjanes[categoria] = [mitjana del run 1, mitjana del run 2, ...]
    per_run_mitjanes: dict[str, list[float]] = {}
    # totes[categoria] = totes les puntuacions individuals de tots els runs (pool)
    totes: dict[str, list[int]] = {}

    for cami in camins:
        for cat, valors in parseja_informe(cami).items():
            if not valors:
                continue
            per_run_mitjanes.setdefault(cat, []).append(sum(valors) / len(valors))
            totes.setdefault(cat, []).extend(valors)

    print(f"Runs agregats ({len(camins)}):")
    for c in camins:
        print(f"  - {c.name}")
    print()

    capcalera = f"{'categoria':<20} {'mitjana':>8} {'desv.std':>9} {'min':>5} {'max':>5} {'n_runs':>7} {'n_preg':>7}"
    print(capcalera)
    print("-" * len(capcalera))
    for cat in sorted(per_run_mitjanes):
        mitjanes_run = per_run_mitjanes[cat]
        pool = totes[cat]
        mitjana = statistics.mean(pool)
        desv = statistics.stdev(mitjanes_run) if len(mitjanes_run) > 1 else 0.0
        print(
            f"{cat:<20} {mitjana:>8.2f} {desv:>9.2f} {min(pool):>5} {max(pool):>5} "
            f"{len(mitjanes_run):>7} {len(pool):>7}"
        )

    print(
        "\nmitjana = mitjana de totes les puntuacions individuals (pool de tots els runs)."
        "\ndesv.std = desviacio estandard entre les mitjanes de cada run (variabilitat run-a-run)."
    )


if __name__ == "__main__":
    main()
