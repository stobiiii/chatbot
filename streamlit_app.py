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

# --- Eves Informationsgewinn (nur bei relevanten Schlüsselbits)
if eve_active:
    relevant_indices = basis_alice == basis_bob
    eve_bits_array = np.array(bits_eve)
    eve_correct_bits = np.sum((eve_bits_array == bits_alice) & relevant_indices)
    eve_info_rate = (eve_correct_bits / total_matching) if total_matching > 0 else 0

    st.subheader("🕵️‍♀️ Eves Informationsgewinn (bezogen auf den potentiellen Schlüssel)")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Richtige Schlüsselbits abgefangen", eve_correct_bits)
    with col2:
        st.metric("Informationsrate", f"{eve_info_rate:.2%}")

    # Erweiterte Einflussanalyse
    bob_bits_array = np.array(bits_bob)
    cond_key = relevant_indices
    cond_eve_right = eve_bits_array == bits_alice
    cond_bob_right = bob_bits_array == bits_alice

    cat1 = np.sum(cond_key & cond_eve_right & cond_bob_right)   # Eve richtig, Bob richtig
    cat2 = np.sum(cond_key & ~cond_eve_right & cond_bob_right)  # Eve falsch, Bob richtig
    cat3 = np.sum(cond_key & cond_eve_right & ~cond_bob_right)  # Eve richtig, Bob falsch
    cat4 = np.sum(cond_key & ~cond_eve_right & ~cond_bob_right) # Eve falsch, Bob falsch

    st.subheader("📊 Erweiterte Analyse: Eves Einfluss auf Schlüsselbits")

    # Metriken nebeneinander
    #cols = st.columns(4)
    #cols[0].metric("Eve richtig & Bob richtig", cat1)
    #cols[1].metric("Eve falsch & Bob richtig", cat2)
    #cols[2].metric("Eve richtig & Bob falsch", cat3)
    #cols[3].metric("Eve falsch & Bob falsch", cat4)

    # Kreisdiagramm (automatisch, ohne Checkbox)
    labels = [
        "Eve hat richtiges Bit unentdeckt gestohlen",
        "Eve hat falsches Bit blieb aber unentdeckt",
        "Eve hat richtiges Bit und wurde entdeckt",
        "Eve hat falsches Bit wurde aber entdeckt"
    ]
    values = [cat1, cat2, cat3, cat4]
    colors = ["#4CAF50", "#8BC34A", "#FF9800", "#F44336"]

    fig, ax = plt.subplots()
    ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
    ax.axis('equal')
    st.pyplot(fig)

