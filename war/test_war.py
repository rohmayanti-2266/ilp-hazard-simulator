from war_hazard import Instruction, detect_war
 
 
def test_war_terdeteksi():
    instrs = [
        Instruction("I1", "R1", ["R2", "R3"]),
        Instruction("I2", "R2", ["R4", "R5"]),
    ]
    assert detect_war(instrs) == [("I1", "I2", "R2")]
 
 
def test_tanpa_war():
    instrs = [
        Instruction("I1", "R1", ["R2", "R3"]),
        Instruction("I2", "R4", ["R5", "R6"]),
    ]
    assert detect_war(instrs) == []
 
 
if __name__ == "__main__":
    test_war_terdeteksi()
    test_tanpa_war()
    print("Semua test WAR lulus")
