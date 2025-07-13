import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="BB84 Protokoll", layout="wide")
st.title("🔐 BB84 Protokoll – Interaktive Demonstration")

# --- Parameter
num_bits = st.slider("Anzahl der Bits", min_value=1, max_value=1000, value=1)
eve_active = st.toggle("Eve ist aktiv")

# --- Zufällige Bitfolge und Basen
bits_alice = np.random.randint(0, 2, num_bits)
basis_alice = np.random.choice(["+", "x"], num_bits)

# --- Eve (optional aktiv)
if eve_active:
    basis_eve = np.random.choice(["+", "x"], num_bits)
    bits_eve = []

    for i in range(num_bits):
        if basis_alice[i] == basis_eve[i]:
            eve_bit = bits_alice[i]
        else:
            eve_bit = np.random.randint(0, 2)
        bits_eve.append(eve_bit)
else:
    basis_eve = ["-" for _ in range(num_bits)]
    bits_eve = ["-" for _ in range(num_bits)]

# --- Bob misst das Photon, das von Eve (falls aktiv) oder Alice kommt
basis_bob = np.random.choice(["+", "x"], num_bits)
bits_bob = []

for i in range(num_bits):
    if eve_active:
        send_basis = basis_eve[i]
        send_bit = bits_eve[i]
    else:
        send_basis = basis_alice[i]
        send_bit = bits_alice[i]

    if send_basis == basis_bob[i]:
        bits_bob.append(send_bit)
    else:
        bits_bob.append(np.random.randint(0, 2))

# --- Tabelle mit Übertragungsverlauf
df = pd.DataFrame({
    "Alice Basis": basis_alice,
    "Alice Bit": bits_alice,
    "Eve Basis": basis_eve,
    "Eve Bit": bits_eve,
    "Bob Basis": basis_bob,
    "Bob Bit": bits_bob,
})

st.subheader("📋 Übertragungsverlauf")
st.dataframe(df)

# --- Fehleranalyse (zwischen Alice und Bob bei gleicher Basis)
matching_indices = basis_alice == basis_bob
key_alice = bits_alice[matching_indices]
key_bob = np.array(bits_bob)[matching_indices]

errors = np.sum(key_alice != key_bob)
total_matching = len(key_alice)
error_rate = errors / total_matching if total_matching > 0 else 0

st.subheader("📊 Fehleranalyse (Alice → Bob)")

col1, col2 = st.columns(2)
with col1:
    st.metric("Gemeinsame Basen (Alice = Bob)", total_matching)
    st.metric("Fehlerhafte Bits", errors)
with col2:
    st.metric("Fehlerrate", f"{error_rate:.2%}")

# --- Eves Informationsgewinn (nur bei gleichen Basen von Alice, Bob und Eve und korrektem Bit)
if eve_active:
    eve_bits_array = np.array(bits_eve)
    
    # Indices, wo Alice, Bob und Eve die gleiche Basis haben
    triple_match = (basis_alice == basis_bob) & (basis_alice == basis_eve)
    
    # Eve hat hier sicher das korrekte Bit abgefangen
    eve_sure_indices = triple_match & (eve_bits_array == bits_alice)
    eve_sure_bits = np.sum(eve_sure_indices)
    
    eve_info_rate = eve_sure_bits / total_matching if total_matching > 0 else 0

    st.subheader("🕵️‍♀️ Eves Informationsgewinn (sicher erkannt)")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Sicher abgefangene Schlüsselbits", eve_sure_bits)
    with col2:
        st.metric("Informationsrate", f"{eve_info_rate:.2%}")

    # --- Neue Berechnung für das Kreisdiagramm mit 3 Kategorien ---
    bob_bits_array = np.array(bits_bob)

    # Gemeinsame Basen Alice=Bob
    cond_alice_bob = basis_alice == basis_bob

    # Eve gleiche Basis wie Alice und Bob
    cond_eve_same = (basis_alice == basis_eve) & cond_alice_bob

    # Eve andere Basis als Alice/Bob bei gemeinsamer Alice-Bob-Basis
    cond_eve_diff = (basis_alice != basis_eve) & cond_alice_bob

    # Kategorie 1: Eve gleiche Basis, Eve richtig, Bob richtig (unerkannt gestohlen)
    cat1 = np.sum(cond_eve_same & (eve_bits_array == bits_alice) & (bob_bits_array == bits_alice))

    # Kategorie 2: Eve andere Basis, Bob richtig (kein Fehler bemerkt)
    cat2 = np.sum(cond_eve_diff & (bob_bits_array == bits_alice))

    # Kategorie 3: Eve andere Basis, Bob falsch (Fehler bemerkt)
    cat3 = np.sum(cond_eve_diff & (bob_bits_array != bits_alice))

    labels = [
        "Eve hat in gleicher Basis gemessen und unerkannt gestohlen",
        "Alice & Bob gleiche Basis, Eve andere Basis, Bob hat nichts bemerkt",
        "Alice & Bob gleiche Basis, Eve andere Basis, Bob hat Fehler bemerkt"
    ]
    values = [cat1, cat2, cat3]
    colors = ["#4CAF50", "#8BC34A", "#F44336"]

    fig, ax = plt.subplots()
    ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
    ax.axis('equal')
    st.pyplot(fig)
