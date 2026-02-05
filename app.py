import streamlit as st
import math

# --- 1. Page Configuration ---
st.set_page_config(
    page_title="RC Slab/Beam Designer",
    page_icon="🏗️",
    layout="wide"
)

# --- 2. Custom CSS for Professional UI ---
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .equation-box {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #1E88E5;
        margin-bottom: 20px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    .success-box {
        background-color: #d4edda;
        padding: 15px;
        border-radius: 8px;
        color: #155724;
        font-weight: bold;
        text-align: center;
        border: 1px solid #c3e6cb;
    }
    .fail-box {
        background-color: #f8d7da;
        padding: 15px;
        border-radius: 8px;
        color: #721c24;
        font-weight: bold;
        text-align: center;
        border: 1px solid #f5c6cb;
    }
</style>
""", unsafe_allow_html=True)

# --- Main Title ---
st.markdown('<div class="main-header">🏗️ Reinforced Concrete Design (ACI 318)</div>', unsafe_allow_html=True)
st.markdown("---")

# --- 3. Sidebar Inputs ---
st.sidebar.header("1. Material Properties")

# Concrete Strength (f'c)
fc = st.sidebar.slider(
    "Concrete Compressive Strength (f'c) [MPa]",
    min_value=20, max_value=80, value=25, step=1,
    help="Specified compressive strength of concrete at 28 days."
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

# Total Depth (h)
h = st.sidebar.slider(
    "Section Total Depth (h) [mm]",
    min_value=100, max_value=1500, value=150, step=10
)

# Concrete Cover
cover = st.sidebar.slider(
    "Concrete Cover [mm]",
    min_value=10, max_value=100, value=20, step=5
)

st.sidebar.header("3. Loads & Factors")

# Ultimate Moment (Mu)
mu_val = st.sidebar.slider(
    "Ultimate Moment (Mu) [kN.m]",
    min_value=1.0, max_value=1000.0, value=13.7, step=0.1
)

# Initial j-factor (for estimation only)
jd_init_factor = st.sidebar.slider(
    "Initial j-factor assumption (default 0.95 for slabs)",
    min_value=0.85, max_value=0.99, value=0.95, step=0.01
)

# --- 4. Calculation Engine ---

# Calculate Effective Depth (d)
d = h - cover

# Calculate Beta1 (ACI 318)
if fc <= 28:
    beta1 = 0.85
else:
    beta1 = 0.85 - 0.05 * ((fc - 28) / 7)
    if beta1 < 0.65: beta1 = 0.65

# Layout: Split into two columns
col1, col2 = st.columns([1, 1.3])

with col1:
    st.subheader("📊 Design Parameters")
    st.write(f"**Effective Depth ($d$):** {d} mm")
    st.write(f"**Width ($b$):** {b} mm")
    st.write(f"**Materials:** $f'_c={fc}$ MPa | $f_y={fy}$ MPa")
    st.write(f"**Design Moment ($M_u$):** {mu_val} kN.m")
    
    st.info("Calculation follows ACI 318 Ultimate Strength Design Method.")

with col2:
    st.subheader("🧮 Step-by-Step Calculation")

    # --- Step 1: Initial Estimation ---
    st.markdown("#### Step 1: Initial Steel Estimate")
    st.write("Assuming tension-controlled section ($\phi=0.9$) and initial lever arm:")
    
    st.latex(r"A_{s,approx} = \frac{M_u \times 10^6}{\phi f_y (j_{coeff} \cdot d)}")
    
    # Define variables before display
    phi_assume = 0.9
    # Calculate As initial (Moment converted to N.mm)
    as_initial = (mu_val * 1e6) / (phi_assume * fy * (jd_init_factor * d))
    
    st.markdown(f"""
    <div class="equation-box">
    Using assumed $j \approx {jd_init_factor}$: <br>
    $A_{s,approx} = {as_initial:.2f} \ mm^2$
    </div>
    """, unsafe_allow_html=True)

    # --- Step 2: Calculate Equivalent Stress Block (a) ---
    st.markdown("#### Step 2: Calculate Stress Block Depth ($a$)")
    st.latex(r"a = \frac{A_{s,approx} f_y}{0.85 f'_c b}")
    
    a_calc = (as_initial * fy) / (0.85 * fc * b)
    
    st.markdown(f"""
    <div class="equation-box">
    $a = {a_calc:.2f} \ mm$
    </div>
    """, unsafe_allow_html=True)

    # --- Step 3: Refine As ---
    st.markdown("#### Step 3: Required Steel Area ($A_{s, req}$)")
    st.latex(r"A_{s,req} = \frac{M_u \times 10^6}{\phi f_y (d - a/2)}")
    
    as_req = (mu_val * 1e6) / (phi_assume * fy * (d - (a_calc / 2)))
    
    st.markdown(f"""
    <div class="equation-box">
    $A_{s,req} = \mathbf{{{as_req:.2f}}} \ mm^2$
    </div>
    """, unsafe_allow_html=True)

    # --- Step 4: Minimum Reinforcement (ACI 318) ---
    st.markdown("#### Step 4: Minimum Reinforcement Check ($A_{s, min}$)")
    st.write("According to ACI 318, $A_{s,min}$ is the greater of:")
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

    # --- Final Selection ---
    st.markdown("### ✅ Final Design Steel Area ($A_s$)")
    as_final = max(as_req, as_min)
    
    st.success(f"Required As = {as_final:.2f} mm²")
    
    if as_final == as_min:
        st.caption("⚠️ Governed by Minimum Reinforcement Requirements.")
    else:
        st.caption("Governed by Flexural Strength Requirements.")

# --- 5. Analysis & Safety Check ---
st.markdown("---")
st.header("🛡️ Safety & Strain Analysis Check")

col_check1, col_check2, col_check3 = st.columns(3)

with col_check1:
    st.markdown("**1. Neutral Axis Depth ($c$)**")
    # Recalculate 'a' based on FINAL As (in case As_min governed)
    a_final = (as_final * fy) / (0.85 * fc * b)
    c_depth = a_final / beta1
    
    st.latex(r"c = a_{final} / \beta_1")
    st.write(f"$c = {c_depth:.2f}$ mm")
    st.caption(f"Using $\\beta_1 = {beta1:.2f}$")

with col_check2:
    st.markdown("**2. Net Tensile Strain ($\epsilon_t$)**")
    st.latex(r"\epsilon_t = \frac{d-c}{c} \times 0.003")
    
    epsilon_t = ((d - c_depth) / c_depth) * 0.003
    st.write(f"$\epsilon_t = {epsilon_t:.5f}$")
    
    # Determine Strength Reduction Factor (phi) based on strain
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
        
    st.markdown(f"<span style='color:{color}; font-weight:bold'>{status}</span>", unsafe_allow_html=True)

with col_check3:
    st.markdown("**3. Moment Capacity ($\phi M_n$)**")
    
    # Calculate Final Moment Capacity
    mn = as_final * fy * (d - a_final/2) * 1e-6 # Convert to kN.m
    phi_mn = phi_actual * mn
    
    st.latex(r"\phi M_n = \phi A_s f_y (d - a/2)")
    st.write(f"Capacity = **{phi_mn:.2f} kN.m**")

# --- Final Conclusion ---
st.markdown("### Conclusion")
if phi_mn >= mu_val:
    st.markdown(f"""
    <div class="success-box">
    ✅ SECTION IS SAFE <br>
    Capacity ({phi_mn:.2f} kN.m) > Demand ({mu_val} kN.m)
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div class="fail-box">
    ❌ SECTION IS UNSAFE <br>
    Capacity ({phi_mn:.2f} kN.m) < Demand ({mu_val} kN.m) <br>
    Recommendation: Increase Depth (h) or Concrete Strength.
    </div>
    """, unsafe_allow_html=True)
    
# --- Footer ---
st.markdown("---")
st.caption("Developed with Streamlit & Python | ACI 318 Standard")