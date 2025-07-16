import streamlit as st
import math
import cmath
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Qubit initialzustand
if 'state' not in st.session_state:
    st.session_state.state = [1+0j, 0+0j]

def get_bloch_coords(state):
    alpha, beta = state
    norm = math.sqrt(abs(alpha)**2 + abs(beta)**2)
    alpha /= norm
    beta /= norm
    theta = 2 * math.acos(abs(alpha))
    phi = cmath.phase(beta) - cmath.phase(alpha) if abs(alpha) > 0 else 0
    x = math.sin(theta) * math.cos(phi)
    y = math.sin(theta) * math.sin(phi)
    z = math.cos(theta)
    return (x, y, z)

def apply_gate(gate):
    a, b = st.session_state.state
    if gate == "X":
        st.session_state.state = [b, a]
    elif gate == "Y":
        st.session_state.state = [-1j*b, 1j*a]
    elif gate == "Z":
        st.session_state.state = [a, -b]
    elif gate == "H":
        factor = 1 / math.sqrt(2)
        st.session_state.state = [
            factor * (a + b),
            factor * (a - b)
        ]
    elif gate == "Reset":
        st.session_state.state = [1+0j, 0+0j]

st.title("🌀 3D Bloch-Vektor Simulator")

alpha, beta = st.session_state.state
x, y, z = get_bloch_coords(st.session_state.state)

st.subheader("🧮 Qubit-Zustand")
st.write(f"|ψ⟩ = {alpha:.2f} |0⟩ + {beta:.2f} |1⟩")
st.write(f"**Bloch-Koordinaten:** x = {x:.2f}, y = {y:.2f}, z = {z:.2f}")

st.subheader("🎛️ Gates anwenden:")
cols = st.columns(5)
for i, gate in enumerate(["X", "Y", "Z", "H", "Reset"]):
    if cols[i].button(gate):
        apply_gate(gate)

st.subheader("🌐 3D-Bloch-Kugel")

fig = plt.figure(figsize=(6, 6))
ax = fig.add_subplot(111, projection='3d')

# Bloch sphere
u = [i * math.pi / 50 for i in range(51)]
v = [i * 2 * math.pi / 50 for i in range(51)]
for i in u:
    x_sphere = [math.sin(i) * math.cos(j) for j in v]
    y_sphere = [math.sin(i) * math.sin(j) for j in v]
    z_sphere = [math.cos(i) for j in v]
    ax.plot(x_sphere, y_sphere, z_sphere, color='lightgray', linewidth=0.5)

# Axes
ax.quiver(0, 0, 0, 1, 0, 0, color='red', arrow_length_ratio=0.1)
ax.quiver(0, 0, 0, 0, 1, 0, color='green', arrow_length_ratio=0.1)
ax.quiver(0, 0, 0, 0, 0, 1, color='blue', arrow_length_ratio=0.1)

# Bloch vector
ax.quiver(0, 0, 0, x, y, z, color='black', linewidth=2, arrow_length_ratio=0.1)

# Format
ax.set_xlim([-1, 1])
ax.set_ylim([-1, 1])
ax.set_zlim([-1, 1])
ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.set_zlabel("Z")
ax.set_title("Bloch-Sphäre")

st.pyplot(fig)
