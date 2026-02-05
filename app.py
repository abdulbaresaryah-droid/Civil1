import streamlit as st
import math

# --- Page Configuration ---
st.set_page_config(
    page_title="RC Slab/Beam Designer",
    page_icon="🏗️",
    layout="wide"
)

# --- Custom CSS for "Senior" Look ---
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .equation-box {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #1E88E5;
        margin-bottom: 20px;
    }
    .success-box {
        background-color: #d4edda;
        padding: 10px;
        border-radius: 5px;
        color: #155724;
        font-weight: bold;
        text-align: center;
    }
    .fail-box {
        background-color: #f8d7da;
        padding: 10px;
        border-radius: 5px;
        color: #721c24;
        font-weight: bold;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# --- Title ---
st.markdown('<div class="main-header">🏗️ Reinforced Concrete Design (ACI 318)</div>', unsafe_allow_html=True)
st.markdown("---")

# --- Sidebar Inputs (The 'Volume Control' Logic) ---
st.sidebar.header("1. Material Properties")

# Concrete Strength (fc')
fc = st.sidebar.slider(
    "Concrete Compressive Strength (f'c) [MPa]",
    min_value=20, max_value=60, value=25, step=1,
    help="Cylinder strength of concrete"
)

# Steel Yield Strength (fy)
fy = st.sidebar.select_slider(
    "Steel Yield Strength (fy) [MPa]",
    options=[240, 280, 350, 400, 420, 460, 500],
    value=420
)

st.sidebar.header("2. Geometry")

# Width (b)
b = st.sidebar.slider(
    "Section Width (b) [mm]",
    min_value=100, max_value=2000, value=1000, step=50
)

# Height (h)
h = st.sidebar.slider(
    "Section Total Depth (h) [mm]",
    min_value=100, max_value=1000, value=150, step=10
)

# Cover
cover = st.sidebar.slider(
    "Concrete Cover [mm]",
    min_value=10, max_value=100, value=20, step=5
)

st.sidebar.header("3. Loads & Factors")

# Moment (Mu) - Using a slider with a float input capability via 'format'
mu_val = st.sidebar.slider(
    "Ultimate Moment (Mu) [kN.m]",
    min_value=1.0, max_value=500.0, value=13.7, step=0.1
)

# Initial guess factor (jd coefficient)
jd_init_factor = st.sidebar.slider(
    "Initial j-factor assumption (default 0.95 for slabs)",
    min_value=0.85, max_value=0.99, value=0.95, step=0.01
)

# --- Calculations Engine ---

# 1. Effective Depth (d)
d = h - cover

# 2. Beta1 Calculation (ACI 318)
if fc <= 28:
    beta1 = 0.85
else:
    beta1 = 0.85 - 0.05 * ((fc - 28) / 7)
    if beta1 < 0.65: beta1 = 0.65

# Create two columns for layout
col1, col2 = st.columns([1, 1.2])

with col1:
    st.subheader("📊 Geometry & Inputs Check")
    st.write(f"**Depth ($d$):** {d} mm")
    st.write(f"**Width ($b$):** {b} mm")
    st.write(f"**$f'_c$:** {fc} MPa | **$f_y$:** {fy} MPa")
    st.write(f"**$M_u$:** {mu_val} kN.m")
    
    # Visualization (Placeholder for a section drawing later)
    st.info("Calculation follows ACI 318 Code (Ultimate Strength Design)")

with col2:
    st.subheader("🧮 Detailed Calculations")

    # --- Step 1: Initial Estimation ---
    st.markdown("#### Step 1: Initial Requirement ($A_{s, initial}$)")
    st.write("Assuming tension controlled section initially:")
    
    # Equation display
    st.latex(r"A_{s,approx} = \frac{M_u \times 10^6}{\phi f_y (j_{coeff} \cdot d)}")
    
    # Calculation
    # Note: Mu is in kN.m, need to convert to N.mm (* 10^6)
    phi_assume = 0.9
    as_initial = (mu_val * 1e6) / (phi_assume * fy * (jd_init_factor * d))
    
    st.markdown(f"""
    <div class="equation-box">
    Using $j \approx {jd_init_factor}$: <br>
    $A_{s,approx} = {as_initial:.2f} \ mm^2$
    </div>
    """, unsafe_allow_html=True)

    # --- Step 2: Calculate 'a' (Depth of equivalent stress block) ---
    st.markdown("#### Step 2: Calculate Stress Block ($a$)")
    st.latex(r"a = \frac{A_{s,approx} f_y}{0.85 f'_c b}")
    
    a_calc = (as_initial * fy) / (0.85 * fc * b)
    
    st.markdown(f"""
    <div class="equation-box">
    $a = {a_calc:.2f} \ mm$
    </div>
    """, unsafe_allow_html=True)

    # --- Step 3: Refine As ---
    st.markdown("#### Step 3: Refine Steel Area ($A_{s, req}$)")
    st.latex(r"A_{s,req} = \frac{M_u \times 10^6}{\phi f_y (d - a/2)}")
    
    as_req = (mu_val * 1e6) / (phi_assume * fy * (d - (a_calc / 2)))
    
    st.markdown(f"""
    <div class="equation-box">
    $A_{s,req} = \mathbf{{{as_req:.2f}}} \ mm^2$
    </div>
    """, unsafe_allow_html=True)

    # --- Step 4: Minimum Reinforcement (ACI 318) ---
    st.markdown("#### Step 4: Check Minimum Reinforcement ($A_{s, min}$)")
    st.write("ACI 318 requires the maximum of:")
    st.latex(r"1) \ \frac{0.25 \sqrt{f'_c}}{f_y} b_w d \quad \text{and} \quad 2) \ \frac{1.4}{f_y} b_w d")
    
    as_min_1 = ((0.25 * math.sqrt(fc)) / fy) * b * d
    as_min_2 = (1.4 / fy) * b * d
    as_min = max(as_min_1, as_min_2)
    
    st.markdown(f"""
    <div class="equation-box">
    1) {as_min_1:.2f} $mm^2$ <br>
    2) {as_min_2:.2f} $mm^2$ <br>
    $\Rightarrow A_{s, min} = \mathbf{{{as_min:.2f}}} \ mm^2$
    </div>
    """, unsafe_allow_html=True)

    # --- Final As Selection ---
    st.markdown("### ✅ Final Design Steel ($A_s$)")
    as_final = max(as_req, as_min)
    
    st.success(f"Design As = {as_final:.2f} mm²")
    if as_final == as_min:
        st.caption("(Governed by Minimum Reinforcement)")
    else:
        st.caption("(Governed by Applied Moment)")

# --- Analysis & Safety Check Section ---
st.markdown("---")
st.header("🛡️ Safety & Analysis Check")

col_check1, col_check2, col_check3 = st.columns(3)

with col_check1:
    st.markdown("**1. Neutral Axis ($c$)**")
    st.latex(r"c = a / \beta_1")
    c_depth = a_calc / beta1
    st.write(f"$c = {c_depth:.2f}$ mm")
    st.caption(f"($\\beta_1 = {beta1:.2f}$)")

with col_check2:
    st.markdown("**2. Net Tensile Strain ($\epsilon_t$)**")
    st.latex(r"\epsilon_t = \frac{d-c}{c} \times 0.003")
    epsilon_t = ((d - c_depth) / c_depth) * 0.003
    st.write(f"$\epsilon_t = {epsilon_t:.5f}$")
    
    # Phi Calculation based on Strain
    if epsilon_t >= 0.005:
        phi_actual = 0.9
        status = "Tension Controlled (OK)"
        color = "green"
    elif epsilon_t <= 0.002:
        phi_actual = 0.65
        status = "Compression Controlled (Brittle!)"
        color = "red"
    else:
        # Transition zone
        phi_actual = 0.65 + 0.25 * ((epsilon_t - 0.002) / 0.003)
        status = "Transition Zone"
        color = "orange"
        
    st.markdown(f"<span style='color:{color}'>**{status}**</span>", unsafe_allow_html=True)

with col_check3:
    st.markdown("**3. Capacity ($\phi M_n$)**")
    # Calculate moment capacity with the actual calculated 'a' and 'phi'
    # Recalculate 'a' based on FINAL As (in case As_min governed)
    a_final = (as_final * fy) / (0.85 * fc * b)
    
    mn = as_final * fy * (d - a_final/2) * 1e-6 # Convert to kN.m
    phi_mn = phi_actual * mn
    
    st.latex(r"\phi M_n = \phi A_s f_y (d - a/2)")
    st.write(f"Capacity = **{phi_mn:.2f} kN.m**")

# --- Final Verdict ---
st.markdown("### Conclusion")
if phi_mn >= mu_val:
    st.markdown(f"""
    <div class="success-box">
    SECTION IS SAFE ✅ <br>
    Capacity ({phi_mn:.2f}) > Demand ({mu_val})
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div class="fail-box">
    SECTION IS UNSAFE ❌ <br>
    Capacity ({phi_mn:.2f}) < Demand ({mu_val}) <br>
    Increase Depth (h) or Steel Area
    </div>
    """, unsafe_allow_html=True)
    
# --- Footer ---
st.markdown("---")
st.caption("Developed with ❤️ by Your Engineering Partner using Streamlit & Python")