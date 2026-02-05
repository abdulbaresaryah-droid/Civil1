import streamlit as st
import pandas as pd
import math

# Page configuration
st.set_page_config(
    page_title="RC Section Design - v18",
    page_icon="🏗️",
    layout="wide"
)

# Custom CSS for Unified UI
st.markdown("""
    <style>
    .main-header {
        font-size: 2.2rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
        margin-top: -2rem;
    }
    .section-header {
        font-size: 1.5rem;
        color: #2c3e50;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
        border-bottom: 2px solid #1f77b4;
        padding-bottom: 0.3rem;
    }
    .stMetric {
        background-color: #f8f9fa;
        padding: 5px;
        border-radius: 5px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .katex { font-size: 1.0em; }
    
    /* Hide the spinner for cleaner look during state updates */
    .stSpinner { display: none; }
    </style>
""", unsafe_allow_html=True)

# Rebar data table (Standard Sizes)
rebar_data = {
    6: [28.3, 57, 85, 113, 142, 170, 198, 226, 255],
    8: [50.3, 101, 151, 201, 252, 302, 352, 402, 453],
    10: [78.5, 157, 236, 314, 393, 471, 550, 628, 707],
    12: [113.1, 226, 339, 452, 565, 678, 791, 904, 1017],
    14: [153.9, 308, 461, 615, 769, 923, 1077, 1231, 1385],
    16: [201.1, 402, 603, 804, 1005, 1206, 1407, 1608, 1809],
    18: [254.5, 509, 763, 1017, 1272, 1527, 1781, 2036, 2290],
    20: [314.2, 628, 942, 1256, 1570, 1884, 2199, 2513, 2827],
    22: [380.1, 760, 1140, 1520, 1900, 2281, 2661, 3041, 3421],
    25: [490.9, 982, 1473, 1964, 2454, 2945, 3436, 3927, 4418],
    28: [615.8, 1232, 1847, 2463, 3079, 3695, 4310, 4926, 5542],
    32: [804.2, 1609, 2413, 3217, 4021, 4826, 5630, 6434, 7238]
}

# --- Helper Function for Unified Input (Slider + Number) ---
def unified_input(label, key, min_val, max_val, default_val, step, unit=""):
    """Creates a synchronized slider and number input."""
    
    # Initialize session state if not exists
    if key not in st.session_state:
        st.session_state[key] = default_val

    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Slider controls the state
        val = st.slider(
            label, 
            min_value=float(min_val), 
            max_value=float(max_val), 
            value=float(st.session_state[key]), 
            step=float(step),
            key=f"{key}_slider",
            help=f"Adjust {label}"
        )
    
    with col2:
        # Number input also controls the state
        val_num = st.number_input(
            f"{unit}", 
            min_value=float(min_val), 
            max_value=float(max_val), 
            value=float(val), # Syncs with slider
            step=float(step),
            key=f"{key}_num",
            label_visibility="visible"
        )
        
    # Update state if changed
    if val_num != st.session_state[key]:
        st.session_state[key] = val_num
        st.rerun() # Rerun to update slider position
    
    if val != st.session_state[key]:
        st.session_state[key] = val
        # No rerun needed here as slider drives the flow usually
        
    return st.session_state[key]

# --- Main Application ---

st.markdown('<h1 class="main-header">🏗️ RC Section Design v18</h1>', unsafe_allow_html=True)

# Top Bar: Code Selection
col_code, col_reset = st.columns([3, 1])
with col_code:
    design_code = st.selectbox("📘 Design Code / كود التصميم", ["ACI 318 (American)", "ECP 203 (Egyptian)"])
with col_reset:
    if st.button("🗑️ Reset", use_container_width=True):
        for key in st.session_state.keys():
            del st.session_state[key]
        st.rerun()

st.markdown("---")

# --- Inputs Section ---
st.sidebar.title("⚙️ Parameters")
st.sidebar.markdown("Use the main panel inputs for better control.")

# Organize inputs in columns
col_mat, col_geom, col_load = st.columns(3)

with col_mat:
    st.subheader("🧱 Materials")
    fy = unified_input("Yield Strength (fy)", "fy", 240, 600, 400, 10, "MPa")
    
    if "ACI" in design_code:
        f_concrete = unified_input("Concrete (f'c)", "fc", 20, 60, 28, 1, "MPa")
        fcu = None
    else:
        f_concrete = unified_input("Concrete (fcu)", "fcu", 20, 60, 30, 1, "MPa")
        fcu = f_concrete # Assign for ECP logic

with col_geom:
    st.subheader("📏 Dimensions")
    b = unified_input("Width (b)", "b", 100, 1000, 250, 50, "mm")
    h = unified_input("Height (h)", "h", 200, 2000, 600, 50, "mm")
    cover = unified_input("Cover", "cover", 20, 100, 40, 5, "mm")

with col_load:
    st.subheader("weight Load")
    Mu = unified_input("Moment (Mu)", "Mu", 10, 1000, 150, 1, "kN.m")

# --- Design Parameters (Code Specific) ---
st.markdown("---")
if "ACI" in design_code:
    with st.expander("🛠️ ACI Factors", expanded=True):
        phi = unified_input("Reduction Factor (φ)", "phi", 0.65, 0.90, 0.90, 0.05)
else:
    # ECP doesn't need explicit user input for factors usually, they are embedded
    # But we can show them or add specific ECP constraints if needed
    pass

# --- Calculations ---
d = h - cover
if d <= 0:
    st.error("❌ Error: Height must be greater than cover!")
    st.stop()

Mu_Nmm = Mu * 1e6

st.markdown('<h2 class="section-header">🧮 Calculations & Analysis</h2>', unsafe_allow_html=True)

# ---------------- ACI 318 LOGIC ----------------
if "ACI" in design_code:
    try:
        # ACI Logic (Same as v17 but cleaner)
        beta1 = 0.85 if f_concrete <= 28 else max(0.65, 0.85 - 0.05 * (f_concrete - 28) / 7)
        
        # Iterative design or exact quadratic
        # Using exact quadratic for As directly is better, but let's stick to the clear steps
        # Mn_req = Mu / phi
        # Rn = Mn_req / (b * d^2)
        # rho = (0.85 * fc / fy) * (1 - sqrt(1 - 2 * Rn / (0.85 * fc)))
        
        # Simplified Steps for display
        calculations = []
        
        # 1. Assume a approx 0.9d initially for display, but calculate exact
        # Solving Quadratic: 0.5*a^2 - d*a + (Mu_Nmm)/(0.85*fc*phi*b) = 0 is wrong
        # Correct: a = d - sqrt(d^2 - (2*Mu)/(0.85*fc*phi*b))
        
        term = (2 * Mu_Nmm) / (0.85 * f_concrete * phi * b)
        under_root = d**2 - term
        
        if under_root < 0:
            st.error(f"❌ Section Too Small! (Compression Failure). Increase dimensions or f'c.")
            st.stop()
            
        a = d - math.sqrt(under_root)
        As_req = (0.85 * f_concrete * b * a) / fy
        
        c = a / beta1
        es = 0.003 * (d - c) / c
        
        # Min Steel
        As_min1 = (0.25 * math.sqrt(f_concrete) / fy) * b * d
        As_min2 = (1.4 / fy) * b * d
        As_min = max(As_min1, As_min2)
        
        As_final = max(As_req, As_min)
        
        # Display Steps
        st.latex(r"d = h - cover = " + f"{h:.0f} - {cover:.0f} = {d:.0f} mm")
        st.latex(r"a = d - \sqrt{d^2 - \frac{2 M_u}{\phi 0.85 f'_c b}} = " + f"{a:.1f} mm")
        st.latex(r"A_s = \frac{0.85 f'_c b a}{f_y} = " + f"{As_req:.1f} mm^2")
        
        if As_final == As_min:
            st.warning(f"⚠️ Governed by Minimum Steel (As_min = {As_min:.1f})")
        
        design_status = "SAFE" if es >= 0.005 else ("TRANSITION" if es >= 0.002 else "UNSAFE")
        
    except Exception as e:
        st.error(f"Calculation Error: {e}")
        st.stop()

# ---------------- ECP 203 LOGIC ----------------
else:
    try:
        st.info("🇪🇬 Designing according to ECP 203 (Limit State - C1-J Method)")
        
        calculations = []
        
        # Step 1: Effective Depth
        st.write("**1. Effective Depth (d)**")
        st.latex(rf"d = h - cover = {h:.0f} - {cover:.0f} = {d:.0f} mm")
        
        # Step 2: C1 Calculation
        # C1 = d / sqrt(Mu / (fcu * b))
        # Note: Mu in formula is usually kN.m, need to be careful with units.
        # Standard ECP: d (mm) = C1 * sqrt(Mu (kN.m) * 10^6 / (fcu (N/mm2) * b (mm)))
        
        val_under_root = Mu_Nmm / (f_concrete * b)
        C1 = d / math.sqrt(val_under_root)
        
        st.write("**2. Calculate C1**")
        st.latex(r"C_1 = \frac{d}{\sqrt{\frac{M_u}{f_{cu} \times b}}}")
        st.latex(rf"C_1 = \frac{{{d:.0f}}}{{\sqrt{{\frac{{{Mu:.1f} \times 10^6}}{{{f_concrete:.1f} \times {b:.0f}}}}}}} = \mathbf{{{C1:.3f}}}")
        
        # Step 3: Check C1
        C1_min = 2.78 # Corresponds to c/d max approx 0.45-0.5 depending on steel
        
        if C1 < C1_min:
            st.error(f"❌ Unsafe Section! C1 ({C1:.2f}) < 2.78. Section is Over-Reinforced.")
            st.write("Solutions: Increase Depth (h), Increase Width (b), or Increase fcu.")
            st.stop()
        else:
            st.success(f"✓ C1 Check: {C1:.2f} > 2.78 (Ductile Failure ensured)")
            
        # Step 4: Calculate J
        # Formula from user image
        # J = (1/1.15) * (0.5 + sqrt(0.25 - (1 / (0.9 * C1^2))))
        term_J = 1 / (0.9 * C1**2)
        inside_root = 0.25 - term_J
        
        J = (1/1.15) * (0.5 + math.sqrt(inside_root))
        J_max = 0.826 # Common upper bound for J in ECP charts
        
        if J > J_max:
            J_design = J_max
            st.info(f"ℹ️ J calculated ({J:.3f}) > J_max. Using J = {J_max}")
        else:
            J_design = J
        
        st.write("**3. Calculate J**")
        st.latex(r"J = \frac{1}{1.15} \left( 0.5 + \sqrt{0.25 - \frac{1}{0.9 C_1^2}} \right)")
        st.latex(rf"J = \mathbf{{{J_design:.3f}}}")
        
        # Step 5: Calculate As
        # Formula from image: As = Mu / (fy * J * d)
        # Note: The 'J' calculated above includes the safety factors as per the formula structure provided
        As_req = Mu_Nmm / (fy * J_design * d)
        
        st.write("**4. Calculate Required Steel (As)**")
        st.latex(r"A_s = \frac{M_u}{f_y \times J \times d}")
        st.latex(rf"A_s = \frac{{{Mu:.1f} \times 10^6}}{{{fy:.0f} \times {J_design:.3f} \times {d:.0f}}} = \mathbf{{{As_req:.1f}}} mm^2")
        
        # Step 6: Min Steel
        # ECP Min: Less of (1.1/fy * b * d) or (1.3 As_req) but not less than 0.15/100 bd...
        # Simplified ECP Beam Min: 1.1/fy * b * d
        min_coeff = 1.1 / fy
        min_coeff_2 = 0.225 * math.sqrt(f_concrete) / fy
        final_coeff = max(min_coeff, min_coeff_2)
        
        As_min = final_coeff * b * d
        
        st.write("**5. Minimum Steel Check**")
        st.latex(rf"A_{{s,min}} = \text{{max}}(\frac{{1.1}}{{f_y}}, \frac{{0.225\sqrt{{f_{{cu}}}}}}{{f_y}}) \times b \times d = {As_min:.1f} mm^2")
        
        if As_req < As_min:
            As_final = As_min
            st.warning(f"⚠️ Using Minimum Steel: {As_final:.1f} mm²")
        else:
            As_final = As_req
            
        design_status = "SAFE" # Since C1 checked out
        
    except Exception as e:
        st.error(f"ECP Calculation Error: {e}")
        st.stop()

# --- Summary & Visualization ---
st.markdown("---")
col_res1, col_res2, col_res3 = st.columns(3)

with col_res1:
    st.metric("Required Area (As)", f"{As_final:.0f} mm²", delta=f"{'ACI' if 'ACI' in design_code else 'ECP'}")

with col_res2:
    if "ACI" in design_code:
        st.metric("Strain (εs)", f"{es:.4f}", design_status)
    else:
        st.metric("C1 Factor", f"{C1:.2f}", "SAFE" if C1 > 2.78 else "UNSAFE")

with col_res3:
    utilization = (As_final / (b*d)) * 100
    st.metric("Steel Percentage (ρ)", f"{utilization:.2f}%")

# --- Reinforcement Selection (Smart) ---
st.markdown('<h2 class="section-header">🔧 Reinforcement Options</h2>', unsafe_allow_html=True)

tabs = st.tabs(["💡 Suggestions", "✍️ Manual Select"])

with tabs[0]:
    # Logic to find best combinations
    suggestions = []
    for dia, areas in rebar_data.items():
        area_1 = areas[0]
        needed = As_final / area_1
        num = math.ceil(needed)
        
        if 2 <= num <= 10: # Reasonable number of bars
            actual_area = areas[num-1]
            eff = (actual_area / As_final) * 100 - 100
            if eff < 25: # Don't waste too much steel
                suggestions.append((dia, num, actual_area, eff))
    
    if not suggestions:
        st.warning("No optimal standard combinations found. Try manual selection.")
    else:
        # Sort by efficiency (least waste)
        suggestions.sort(key=lambda x: x[3])
        
        s_col1, s_col2, s_col3 = st.columns(3)
        for i, (dia, num, area, eff) in enumerate(suggestions[:3]):
            with [s_col1, s_col2, s_col3][i]:
                st.success(f"**{num} Ø {dia}**")
                st.caption(f"Area: {area:.0f} mm²")
                st.caption(f"Excess: +{eff:.1f}%")

with tabs[1]:
    m_col1, m_col2 = st.columns(2)
    with m_col1:
        sel_dia = st.selectbox("Bar Diameter", options=list(rebar_data.keys()), index=4)
    with m_col2:
        sel_num = st.number_input("Number of Bars", min_value=1, max_value=20, value=4)
        
    sel_area = rebar_data[sel_dia][sel_num-1]
    
    if sel_area >= As_final:
        st.success(f"✅ Safe! Provided: {sel_area:.0f} mm² > Required: {As_final:.0f} mm²")
    else:
        st.error(f"❌ Unsafe! Provided: {sel_area:.0f} mm² < Required: {As_final:.0f} mm²")

# Footer
st.markdown("---")
st.caption(f"**V18 System** | Code: {design_code} | Developed for Civil Engineering")