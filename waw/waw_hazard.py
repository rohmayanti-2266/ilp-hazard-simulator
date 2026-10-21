import os
from dataclasses import dataclass

import matplotlib.pyplot as plt
import networkx as nx


@dataclass
class Instruction:
    name: str
    destination: str
    sources: list


# Instruksi contoh yang memuat WAW:
# I3 dan I5 menulis R1 yang juga ditulis I1, dan I4 menulis R4 yang juga ditulis I2
instructions = [
    Instruction("I1", "R1", ["R2", "R3"]),
    Instruction("I2", "R4", ["R5", "R6"]),
    Instruction("I3", "R1", ["R7", "R8"]),
    Instruction("I4", "R4", ["R9", "R10"]),
    Instruction("I5", "R1", ["R11", "R12"]),
    Instruction("I6", "R13", ["R14", "R15"]),
]


# -------------------------------------------------
# Deteksi WAW
# -------------------------------------------------
def has_waw(inst1, inst2):
    """True jika inst1 dan inst2 menulis register yang sama (WAW)."""
    return inst1.destination == inst2.destination


def detect_waw(instrs):
    """Mengembalikan list (penulis_pertama, penulis_kedua, register)."""
    hazards = []
    for i in range(len(instrs)):
        for j in range(i + 1, len(instrs)):
            if has_waw(instrs[i], instrs[j]):
                hazards.append((instrs[i].name, instrs[j].name, instrs[i].destination))
    return hazards


def show_waw_hazards(instrs):
    print("\n" + "=" * 50)
    print("WAW HAZARD DETECTION")
    print("=" * 50)

    hazards = detect_waw(instrs)
    if not hazards:
        print("Tidak ada WAW hazard.")
        return hazards

    for first, second, reg in hazards:
        print(f"WAW: {second} menulis {reg} yang juga ditulis {first}")
    return hazards


# -------------------------------------------------
# Penjadwalan ILP yang menghormati WAW
# -------------------------------------------------
def schedule_with_waw(instrs):
    """
    Penulisan kedua tidak boleh mendahului penulisan pertama ke register
    yang sama (supaya nilai akhir register tetap benar). Mengembalikan dict
    nama_instruksi -> nomor cycle.
    """
    level = {}
    for j, inst in enumerate(instrs):
        earlier = [level[instrs[i].name] for i in range(j) if has_waw(instrs[i], inst)]
        level[inst.name] = 1 + max(earlier) if earlier else 1
    return level


def waw_parallel_execution(instrs):
    print("\n" + "=" * 50)
    print("ILP EXECUTION (DENGAN PENANGANAN WAW)")
    print("=" * 50)

    level = schedule_with_waw(instrs)
    total_cycles = max(level.values())

    for cycle in range(1, total_cycles + 1):
        print(f"\nCycle {cycle}:")
        for inst in instrs:
            if level[inst.name] == cycle:
                print(f"  -> {inst.name}: {inst.destination} = {' + '.join(inst.sources)}")

    print(f"\nTotal Sequential Cycles : {len(instrs)}")
    print(f"Total ILP Cycles (WAW)  : {total_cycles}")
    print(f"Speedup                 : {len(instrs) / total_cycles:.2f}x")
    return total_cycles


# -------------------------------------------------
# Dependency graph WAW
# -------------------------------------------------
def build_waw_graph(instrs):
    G = nx.DiGraph()
    for inst in instrs:
        G.add_node(inst.name)
    for first, second, reg in detect_waw(instrs):
        G.add_edge(first, second, label=f"WAW ({reg})")
    return G


def draw_waw_graph(instrs, filename="dependency_waw.png"):
    G = build_waw_graph(instrs)
    level = schedule_with_waw(instrs)

    columns = {}
    for name, lv in level.items():
        columns.setdefault(lv, []).append(name)

    pos = {}
    for lv, names in columns.items():
        for k, name in enumerate(names):
            pos[name] = (lv * 3, -k * 2 + (len(names) - 1))

    plt.figure(figsize=(10, 6))
    nx.draw_networkx_nodes(G, pos, node_size=2200, node_color="#dadaeb", edgecolors="black")
    nx.draw_networkx_labels(G, pos, font_weight="bold")
    nx.draw_networkx_edges(
        G, pos, arrows=True, arrowsize=25, node_size=2200, edge_color="#756bb1", width=2
    )
    nx.draw_networkx_edge_labels(
        G, pos, edge_labels=nx.get_edge_attributes(G, "label"), font_size=9, label_pos=0.4
    )
    plt.title("Dependency Graph WAW (Write After Write)")
    plt.axis("off")
    plt.tight_layout()

    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    plt.savefig(path, dpi=150)
    print(f"\nGraph disimpan di: {path}")
    plt.show()


# -------------------------------------------------
# Main
# -------------------------------------------------
def main():
    print("\nInstruction Set:")
    for inst in instructions:
        print(f"{inst.name}: {inst.destination} = {' + '.join(inst.sources)}")

    show_waw_hazards(instructions)
    waw_parallel_execution(instructions)
    draw_waw_graph(instructions)


if __name__ == "__main__":
    main()
