import os
from dataclasses import dataclass

import matplotlib.pyplot as plt
import networkx as nx


@dataclass
class Instruction:
    name: str
    destination: str
    sources: list


instructions = [
    Instruction("I1", "R1", ["R2", "R3"]),
    Instruction("I2", "R4", ["R5", "R6"]),
    Instruction("I3", "R7", ["R1", "R4"]),
    Instruction("I4", "R8", ["R9", "R10"]),
    Instruction("I5", "R11", ["R7", "R8"]),
    Instruction("I6", "R12", ["R13", "R14"]),
]


def has_raw(inst1, inst2):
    """True jika inst2 membaca register yang ditulis inst1 (RAW)."""
    return inst1.destination in inst2.sources


def detect_raw(instrs):
    hazards = []
    for i in range(len(instrs)):
        for j in range(i + 1, len(instrs)):
            if has_raw(instrs[i], instrs[j]):
                hazards.append((instrs[i].name, instrs[j].name, instrs[i].destination))
    return hazards


def show_raw_hazards(instrs):
    print("\n" + "=" * 50)
    print("RAW HAZARD DETECTION")
    print("=" * 50)
    hazards = detect_raw(instrs)
    if not hazards:
        print("Tidak ada RAW hazard.")
        return hazards
    for writer, reader, reg in hazards:
        print(f"RAW: {reader} membaca {reg} yang ditulis {writer}")
    return hazards


def schedule_with_raw(instrs):
    level = {}
    for j, inst in enumerate(instrs):
        producers = [level[instrs[i].name] for i in range(j) if has_raw(instrs[i], inst)]
        level[inst.name] = 1 + max(producers) if producers else 1
    return level


def raw_parallel_execution(instrs):
    print("\n" + "=" * 50)
    print("ILP EXECUTION (DENGAN PENANGANAN RAW)")
    print("=" * 50)
    level = schedule_with_raw(instrs)
    total_cycles = max(level.values())
    for cycle in range(1, total_cycles + 1):
        print(f"\nCycle {cycle}:")
        for inst in instrs:
            if level[inst.name] == cycle:
                print(f"  -> {inst.name}: {inst.destination} = {' + '.join(inst.sources)}")
    print(f"\nTotal Sequential Cycles : {len(instrs)}")
    print(f"Total ILP Cycles (RAW)  : {total_cycles}")
    print(f"Speedup                 : {len(instrs) / total_cycles:.2f}x")
    return total_cycles


def build_raw_graph(instrs):
    G = nx.DiGraph()
    for inst in instrs:
        G.add_node(inst.name)
    for writer, reader, reg in detect_raw(instrs):
        G.add_edge(writer, reader, label=f"RAW ({reg})")
    return G


def draw_raw_graph(instrs, filename="dependency_raw.png"):
    G = build_raw_graph(instrs)
    level = schedule_with_raw(instrs)
    columns = {}
    for name, lv in level.items():
        columns.setdefault(lv, []).append(name)
    pos = {}
    for lv, names in columns.items():
        for k, name in enumerate(names):
            pos[name] = (lv * 3, -k * 2 + (len(names) - 1))

    plt.figure(figsize=(10, 6))
    nx.draw_networkx_nodes(G, pos, node_size=2200, node_color="#9ecae1", edgecolors="black")
    nx.draw_networkx_labels(G, pos, font_weight="bold")
    nx.draw_networkx_edges(G, pos, arrows=True, arrowsize=25, node_size=2200,
                           edge_color="#d62728", width=2)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=nx.get_edge_attributes(G, "label"),
                                 font_size=9, label_pos=0.4)
    plt.title("Dependency Graph RAW (Read After Write)")
    plt.axis("off")
    plt.tight_layout()

    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    plt.savefig(path, dpi=150)
    print(f"\nGraph disimpan di: {path}")
    plt.show()


def main():
    print("\nInstruction Set:")
    for inst in instructions:
        print(f"{inst.name}: {inst.destination} = {' + '.join(inst.sources)}")
    show_raw_hazards(instructions)
    raw_parallel_execution(instructions)
    draw_raw_graph(instructions)


if __name__ == "__main__":
    main()