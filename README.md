# ILP Hazard Simulator

Tugas kelompok mata kuliah Arsitektur Komputer: mengimplementasikan deteksi dan penanganan **RAW**, **WAR**, dan **WAW** hazard pada simulator Instruction-Level Parallelism (ILP), lengkap dengan dependency graph untuk tiap hazard.

## Anggota Kelompok

| Anggota | GitHub | Bagian |
|---|---|---|
| Siti Rohmayanti (owner) | [@rohmayanti-2266](https://github.com/rohmayanti-2266) | RAW, setup repo, penggabungan akhir |
| Ulfah Baroroh | (isi username) | WAR |
| Rani Muslimah | (isi username) | WAW |

## Struktur Repo

```
ilp-hazard-simulator/
├── README.md
├── simulator.ipynb          Simulator ILP dasar (dari Colab)
├── raw/
│   ├── raw_hazard.py
│   └── dependency_raw.png
├── war/
│   ├── war_hazard.py
│   ├── test_war.py
│   ├── README_war.md
│   └── dependency_war.png
└── waw/
    ├── waw_hazard.py
    ├── test_waw.py
    ├── README_waw.md
    └── dependency_waw.png
```

## Ringkasan Hazard

Misalkan instruksi **i** muncul lebih dulu daripada instruksi **j**.

| Hazard | Nama lain | Kondisi | Kode deteksi |
|---|---|---|---|
| **RAW** (Read After Write) | True dependency | j **membaca** register yang **ditulis** i | `i.destination in j.sources` |
| **WAR** (Write After Read) | Anti-dependency | j **menulis** register yang **dibaca** i | `j.destination in i.sources` |
| **WAW** (Write After Write) | Output dependency | i dan j sama-sama **menulis** register yang sama | `i.destination == j.destination` |

### RAW (Read After Write)

RAW adalah ketergantungan data yang sebenarnya (*true dependency*). Instruksi j membutuhkan hasil dari instruksi i, jadi j tidak boleh dijalankan sebelum i selesai menulis hasilnya.

```
I1: R1 = R2 + R3
I3: R7 = R1 + R4     # I3 membaca R1 yang ditulis I1 -> RAW
```

Penanganan: instruksi pembaca ditunda sampai semua instruksi penulis register yang dibacanya selesai. RAW tidak bisa dihilangkan, hanya bisa dijadwalkan dengan benar.

### WAR (Write After Read)

WAR adalah ketergantungan semu (*anti-dependency*). Instruksi j menulis register yang masih perlu dibaca instruksi i. Jika j mendahului i, nilai lama register tertimpa sebelum sempat dibaca.

```
I1: R1 = R2 + R3
I3: R2 = R6 + R7     # I3 menulis R2 yang dibaca I1 -> WAR
```

Penanganan: instruksi penulis ditunda sampai instruksi pembaca selesai. Pada hardware nyata, WAR dapat dihilangkan dengan *register renaming*.

### WAW (Write After Write)

WAW adalah ketergantungan keluaran (*output dependency*). Dua instruksi menulis ke register yang sama. Jika urutan penulisannya tertukar, register berakhir dengan nilai yang salah.

```
I1: R1 = R2 + R3
I3: R1 = R7 + R8     # I3 menulis R1 yang juga ditulis I1 -> WAW
```

Penanganan: penulisan kedua ditunda sampai penulisan pertama selesai. Seperti WAR, WAW juga dapat dihilangkan dengan *register renaming*.

## Hasil Implementasi

Hasil berikut berasal dari instruksi contoh di masing-masing file. Angka bisa berbeda bila instruksi contohnya diubah.

| Hazard | Hazard terdeteksi | Cycle sekuensial | Cycle ILP | Speedup | Graph |
|---|---|---|---|---|---|
| RAW | 4 | 6 | 3 | 2.00x | [dependency_raw.png](raw/dependency_raw.png) |
| WAR | 2 | 6 | 2 | 3.00x | [dependency_war.png](war/dependency_war.png) |
| WAW | 4 | 6 | 3 | 2.00x | [dependency_waw.png](waw/dependency_waw.png) |

Pada dependency graph, **node** adalah instruksi, **panah** adalah dependensi (arah dari instruksi lebih awal ke lebih akhir), dan **label** menunjukkan jenis hazard beserta register penyebabnya. Node disusun per kolom sesuai cycle eksekusinya.

## Alur Kode

Ketiga file (`raw_hazard.py`, `war_hazard.py`, `waw_hazard.py`) memiliki alur yang sama. Hanya kondisi deteksinya yang berbeda.

1. **Representasi instruksi.** Kelas `Instruction` menyimpan `name`, `destination`, dan `sources`.
2. **Deteksi.** Fungsi `has_*` mengecek satu pasang instruksi, lalu `detect_*` memeriksa semua pasangan (i sebelum j) dan mengumpulkan hazard yang ditemukan.
3. **Penjadwalan.** `schedule_with_*` menentukan cycle tiap instruksi: satu cycle setelah instruksi terakhir yang harus mendahuluinya, atau cycle 1 bila tidak ada.
4. **Eksekusi ILP.** `*_parallel_execution` mengelompokkan instruksi per cycle, mencetaknya, lalu menghitung speedup (cycle sekuensial dibagi cycle ILP).
5. **Dependency graph.** `build_*_graph` membuat graph dari hasil deteksi dan `draw_*_graph` menggambarnya dengan `networkx` dan `matplotlib`, lalu menyimpannya sebagai PNG.

## Cara Menjalankan

Pastikan Python 3 terpasang, lalu:

```
pip install networkx matplotlib
python raw/raw_hazard.py
python war/war_hazard.py
python waw/waw_hazard.py
```

Setiap program mencetak hasil deteksi dan jadwal eksekusi, lalu membuka jendela dependency graph. Tutup jendela gambar agar program selesai. File PNG tersimpan otomatis di folder masing-masing.

## Kontribusi

Tiap anggota bekerja di branch sendiri (`feature-raw`, `feature-war`, `feature-waw`), lalu digabung ke `main` lewat Pull Request.
