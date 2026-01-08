import streamlit as st
import math
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="SPK Konservasi Mangrove", layout="wide")

# ===============================
# HEADER
# ===============================
st.markdown("<h1 style='text-align: center; color: green;'>SPK Konservasi Mangrove</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Bobot dihitung dari DATA (dinamis) + TOPSIS</p>", unsafe_allow_html=True)
st.markdown("---")

# ===============================
# DATA
# ===============================
kriteria = [
    "Paparan Gelombang",
    "Kedalaman Perairan",
    "Jenis Sedimen",
    "Salinitas",
    "Tingkat Abrasi",
    "Aktivitas Manusia"
]

alternatif = [
    "Pulau Pari",
    "Pulau Tidung",
    "Pulau Pramuka",
    "Pulau Untung Jawa"
]

tipe = ["cost", "cost", "benefit", "cost", "cost", "cost"]

# ===============================
# INPUT DATA
# ===============================
st.sidebar.header("Input Nilai Alternatif (1–5)")
use_paper = st.sidebar.checkbox("Gunakan Data Paper")

X = []

for i, alt in enumerate(alternatif):
    st.sidebar.markdown(f"### {alt}")
    row = []
    for j, kri in enumerate(kriteria):
        if use_paper:
            data_paper = [
                [4, 4, 4, 3, 3, 2],
                [3, 3, 3, 3, 2, 1],
                [4, 4, 4, 4, 3, 3],
                [5, 4, 5, 4, 4, 3],
            ]
            val = data_paper[i][j]
            st.sidebar.text(f"{kri}: {val}")
        else:
            val = st.sidebar.number_input(
                f"{alt} - {kri}",
                min_value=1,
                max_value=5,
                value=3,
                step=1,
                key=f"{alt}_{j}"
            )
        row.append(val)
    X.append(row)

df = pd.DataFrame(X, columns=kriteria)

# ===============================
# HITUNG BOBOT DINAMIS (VARIANCE)
# ===============================
variansi = df.var()            # variasi data
bobot = variansi / variansi.sum()

bobot_df = pd.DataFrame({
    "Kriteria": kriteria,
    "Jenis Kriteria": ["Cost" if t == "cost" else "Benefit" for t in tipe],
    "Bobot": bobot.values
})

st.subheader("Bobot Kriteria (Berubah Sesuai Data)")
st.table(bobot_df)

# ===============================
# TOPSIS
# ===============================
if st.button("Hitung Ranking"):

    m, n = len(alternatif), len(kriteria)

    # Normalisasi
    R = np.zeros((m, n))
    for j in range(n):
        pembagi = math.sqrt(sum(df.iloc[i, j]**2 for i in range(m)))
        R[:, j] = df.iloc[:, j] / pembagi

    # Normalisasi terbobot
    Y = R * bobot.values

    # Solusi ideal
    A_plus, A_min = [], []
    for j in range(n):
        if tipe[j] == "benefit":
            A_plus.append(Y[:, j].max())
            A_min.append(Y[:, j].min())
        else:
            A_plus.append(Y[:, j].min())
            A_min.append(Y[:, j].max())

    # Preferensi
    V = []
    for i in range(m):
        d_plus = math.sqrt(sum((Y[i, j] - A_plus[j])**2 for j in range(n)))
        d_min  = math.sqrt(sum((Y[i, j] - A_min[j])**2 for j in range(n)))
        V.append(d_min / (d_plus + d_min))

    hasil = pd.DataFrame({
        "Alternatif": alternatif,
        "Nilai Preferensi": V
    }).sort_values("Nilai Preferensi", ascending=False).reset_index(drop=True)

    hasil.index += 1
    hasil.rename_axis("Ranking", inplace=True)

    st.subheader("Hasil Perangkingan")
    st.table(hasil)

    st.success(f"Lokasi terbaik adalah **{hasil.iloc[0]['Alternatif']}**")

    fig, ax = plt.subplots()
    ax.bar(hasil["Alternatif"], hasil["Nilai Preferensi"])
    ax.set_ylim(0, 1)
    ax.set_ylabel("Nilai Preferensi")
    st.pyplot(fig)
