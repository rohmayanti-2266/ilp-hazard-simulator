"""
war/war_hazard.py
Implementasi WAR (Write After Read) hazard pada simulator ILP.
 
WAR (anti-dependency): instruksi j MENULIS register yang DIBACA
instruksi i sebelumnya (i muncul lebih dulu dari j).
 
Cara pakai:
    pip install networkx matplotlib
    python war/war_hazard.py
"""
 
import os
from dataclasses import dataclass
 
import matplotlib.pyplot as plt
import networkx as nx
 
 
@dataclass
class Instruction:
    name: str
    destination: str
    sources: list
 
 
# Instruksi contoh yang memuat WAR:
# I3 menulis R2 yang dibaca I1, dan I4 menulis R5 yang dibaca I2
instructions = [
    Instruction("I1", "R1", ["R2", "R3"]),
    Instruction("I2", "R4", ["R1", "R5"]),
    Instruction("I3", "R2", ["R6", "R7"]),
    Instruction("I4", "R5", ["R8", "R9"]),
    Instruction("I5", "R10", ["R4", "R2"]),
    Instruction("I6", "R11", ["R12", "R13"]),
]
 
 
# -------------------------------------------------
# Deteksi WAR
# -------------------------------------------------
def has_war(inst1, inst2):
    """True jika inst2 menulis register yang dibaca inst1 (WAR)."""
    return inst2.destination in inst1.sources
 
 
def detect_war(instrs):
    """Mengembalikan list (instruksi_pembaca, instruksi_penulis, register)."""
    hazards = []
    for i in range(len(instrs)):
        for j in range(i + 1, len(instrs)):
            if has_war(instrs[i], instrs[j]):
                hazards.append((instrs[i].name, instrs[j].name, instrs[j].destination))
    return hazards
 
 
def show_war_hazards(instrs):
    print("\n" + "=" * 50)
    print("WAR HAZARD DETECTION")
    print("=" * 50)
 
    hazards = detect_war(instrs)
    if not hazards:
        print("Tidak ada WAR hazard.")
        return hazards
 
    for reader, writer, reg in hazards:
        print(f"WAR: {writer} menulis {reg} yang dibaca {reader}")
    return hazards
 
 
# -------------------------------------------------
# Penjadwalan ILP yang menghormati WAR
# -------------------------------------------------
def schedule_with_war(instrs):
    """
    Instruksi penulis tidak boleh dieksekusi sebelum instruksi pembaca
    selesai (supaya nilai lama tidak tertimpa). Mengembalikan dict
    nama_instruksi -> nomor cycle.
    """
    level = {}
    for j, inst in enumerate(instrs):
        readers = [level[instrs[i].name] for i in range(j) if has_war(instrs[i], inst)]
        level[inst.name] = 1 + max(readers) if readers else 1
    return level
 
 
def war_parallel_execution(instrs):
    print("\n" + "=" * 50)
    print("ILP EXECUTION (DENGAN PENANGANAN WAR)")
    print("=" * 50)
 
    level = schedule_with_war(instrs)
    total_cycles = max(level.values())
 
    for cycle in range(1, total_cycles + 1):
        print(f"\nCycle {cycle}:")
        for inst in instrs:
            if level[inst.name] == cycle:
                print(f"  -> {inst.name}: {inst.destination} = {' + '.join(inst.sources)}")
 
    print(f"\nTotal Sequential Cycles : {len(instrs)}")
    print(f"Total ILP Cycles (WAR)  : {total_cycles}")
    print(f"Speedup                 : {len(instrs) / total_cycles:.2f}x")
    return total_cycles
 
 
# -------------------------------------------------
# Dependency graph WAR
# -------------------------------------------------
def build_war_graph(instrs):
    G = nx.DiGraph()
    for inst in instrs:
        G.add_node(inst.name)
    for reader, writer, reg in detect_war(instrs):
        G.add_edge(reader, writer, label=f"WAR ({reg})")
    return G
 
 
def draw_war_graph(instrs, filename="dependency_war.png"):
    G = build_war_graph(instrs)
    level = schedule_with_war(instrs)
 
    columns = {}
    for name, lv in level.items():
        columns.setdefault(lv, []).append(name)
 
    pos = {}
    for lv, names in columns.items():
        for k, name in enumerate(names):
            pos[name] = (lv * 3, -k * 2 + (len(names) - 1))
 
    plt.figure(figsize=(10, 6))
    nx.draw_networkx_nodes(G, pos, node_size=2200, node_color="#a1d99b", edgecolors="black")
    nx.draw_networkx_labels(G, pos, font_weight="bold")
    nx.draw_networkx_edges(
        G, pos, arrows=True, arrowsize=25, node_size=2200, edge_color="#e6550d", width=2
    )
    nx.draw_networkx_edge_labels(
        G, pos, edge_labels=nx.get_edge_attributes(G, "label"), font_size=9, label_pos=0.4
    )
    plt.title("Dependency Graph WAR (Write After Read)")
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
 
    show_war_hazards(instructions)
    war_parallel_execution(instructions)
    draw_war_graph(instructions)
 
 
if __name__ == "__main__":
    main()
