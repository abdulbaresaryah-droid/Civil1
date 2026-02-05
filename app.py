import streamlit as st
import pandas as pd
import numpy as np
import math

# Page configuration
st.set_page_config(
    page_title="RC Section Design - Multi-Code",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 0.5rem;
        margin-top: -2rem;
        font-weight: bold;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #555;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    .section-header {
        font-size: 1.5rem;
        color: #2c3e50;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
        border-bottom: 2px solid #1f77b4;
        padding-bottom: 0.3rem;
    }
    .code-badge {
        display: inline-block;
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.9rem;
    }
    .aci-badge {
        background-color: #3498db;
        color: white;
    }
    .ecp-badge {
        background-color: #e74c3c;
        color: white;
    }
    .stMetric {
        background-color: #f8f9fa;
        padding: 5px;
        border-radius: 5px;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.1rem;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 0.85rem;
    }
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    div[data-testid="column"] {
        padding: 2px 5px !important;
    }
    .element-container {
        margin-bottom: 0px !important;
    }
    .katex {
        font-size: 0.95em;
    }
    /* Unified input styling */
    .unified-input {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 15px;
    }
    .unified-input label {
        color: white;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# Rebar data table (mm²)
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
    32: [804.2, 1609, 2413, 3217, 4021, 4826, 5630, 6434, 7238],
    36: [1017.9, 2036, 3054, 4072, 5089, 6107, 7125, 8143, 9161],
    40: [1256.6, 2513, 3770, 5027, 6283, 7540, 8796, 10053, 11310],
    50: [1963.5, 3928, 5892, 7856, 9820, 11784, 13748, 15712, 17676]
}

# Initialize session state
if 'code_standard' not in st.session_state:
    st.session_state.code_standard = 'ACI 318'
if 'initialized' not in st.session_state:
    st.session_state.initialized = True

# Reset function
def clear_all_inputs():
    keys_to_delete = ['fy', 'fcu', 'Mu', 'b', 'h', 'cover']
    for key in keys_to_delete:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

# Unified input component (Number + Slider synchronized)
def unified_input(label, min_val, max_val, default_val, step, key, unit=""):
    """Creates a unified input with number input and slider synchronized"""
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        number_value = st.number_input(
            f"{label} ({unit})" if unit else label,
            min_value=min_val,
            max_value=max_val,
            value=st.session_state.get(key, default_val),
            step=step,
            key=f"{key}_number",
            label_visibility="visible"
        )
    
    with col2:
        slider_value = st.slider(
            f"slider_{label}",
            min_value=min_val,
            max_value=max_val,
            value=st.session_state.get(key, default_val),
            step=step,
            key=f"{key}_slider",
            label_visibility="collapsed"
        )
    
    # Synchronize values
    if number_value != slider_value:
        if st.session_state.get(f"{key}_number") != st.session_state.get(f"prev_{key}_number", default_val):
            final_value = number_value
        else:
            final_value = slider_value
    else:
        final_value = number_value
    
    st.session_state[key] = final_value
    st.session_state[f"prev_{key}_number"] = number_value
    
    return final_value

# Title and Code Selection
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown('<h1 class="main-header">🏗️ RC Section Design</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Multi-Code Reinforced Concrete Design Tool</p>', unsafe_allow_html=True)

# Code Standard Selection
st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    code_standard = st.radio(
        "**Select Design Code Standard:**",
        options=['ACI 318', 'ECP 203'],
        horizontal=True,
        key='code_standard'
    )
    
    if code_standard == 'ACI 318':
        st.markdown('<span class="code-badge aci-badge">🇺🇸 ACI 318 - American Concrete Institute</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="code-badge ecp-badge">🇪🇬 ECP 203 - Egyptian Code of Practice</span>', unsafe_allow_html=True)

# Sidebar
st.sidebar.header("📊 Input Parameters")

# Clear button
if st.sidebar.button("🗑️ Clear All Inputs", type="secondary", use_container_width=True):
    clear_all_inputs()

st.sidebar.markdown("---")

# Material Properties
st.sidebar.subheader("🔬 Material Properties")

if code_standard == 'ACI 318':
    fy = unified_input("Steel Yield Strength, fy", 0.0, 600.0, 420.0, 10.0, 'fy', "MPa")
    fcu = unified_input("Concrete Strength, f'c", 0.0, 50.0, 25.0, 2.5, 'fcu', "MPa")
else:  # ECP 203
    fy = unified_input("Steel Yield Strength, fy", 0.0, 600.0, 360.0, 10.0, 'fy', "MPa")
    fcu = unified_input("Concrete Cube Strength, fcu", 0.0, 60.0, 25.0, 2.5, 'fcu', "MPa")

st.sidebar.markdown("---")

# Loading
st.sidebar.subheader("⚡ Loading")
Mu = unified_input("Ultimate Moment, Mu", 0.0, 500.0, 100.0, 5.0, 'Mu', "kN.m")

st.sidebar.markdown("---")

# Section Dimensions
st.sidebar.subheader("📐 Section Dimensions")
b = unified_input("Width, b", 100.0, 2000.0, 250.0, 50.0, 'b', "mm")
h = unified_input("Height, h", 100.0, 1000.0, 500.0, 10.0, 'h', "mm")
cover = unified_input("Cover", 15.0, 75.0, 40.0, 5.0, 'cover', "mm")

st.sidebar.markdown("---")

# Code-specific parameters
st.sidebar.subheader("⚙️ Design Parameters")

if code_standard == 'ACI 318':
    phi = unified_input("Strength Reduction Factor, φ", 0.65, 0.90, 0.90, 0.05, 'phi', "")
    beta1_default = 0.85 if fcu <= 28 else max(0.65, 0.85 - 0.05 * (fcu - 28) / 7)
    beta1 = unified_input("β₁ Factor", 0.65, 0.85, beta1_default, 0.05, 'beta1', "")
else:  # ECP 203
    # For ECP, gamma_c = 1.5, gamma_s = 1.15
    st.sidebar.info("**ECP Parameters:**\n- γc = 1.5\n- γs = 1.15")

# Validation
if code_standard == 'ACI 318':
    all_inputs_valid = all([
        fy > 0, fcu > 0, Mu > 0, b > 0, h > 0,
        cover >= 0, h > cover, phi > 0, beta1 > 0
    ])
else:  # ECP 203
    all_inputs_valid = all([
        fy > 0, fcu > 0, Mu > 0, b > 0, h > 0,
        cover >= 0, h > cover
    ])

if not all_inputs_valid:
    st.warning("⚠️ Please enter all input values to proceed with calculations")
    st.info("💡 Fill in all required parameters in the sidebar")
    st.stop()

# ============================================
# CALCULATIONS
# ============================================

try:
    # Common calculations
    d = h - cover
    
    if d <= 0:
        st.error("❌ Error: Effective depth d = h - cover must be > 0")
        st.stop()
    
    Mu_Nmm = Mu * 1e6  # kN.m to N.mm
    
    calculations = []
    
    # ============================================
    # ACI 318 CALCULATIONS
    # ============================================
    if code_standard == 'ACI 318':
        # Step 1: Effective depth
        calculations.append({
            'step': '1',
            'description': 'Effective Depth',
            'formula': r'd = h - \text{cover}',
            'substitution': f'{h:.0f} - {cover:.0f}',
            'result': f'{d:.1f} mm',
            'variable': 'd'
        })
        
        # Step 2: Assume jd
        jd = 0.9  # Initial assumption
        
        # Step 3: Initial As
        As_initial = Mu_Nmm / (phi * fy * jd * d)
        
        calculations.append({
            'step': '2',
            'description': 'Initial As (assuming jd=0.9)',
            'formula': r'A_s = \frac{M_u}{\phi f_y jd \cdot d}',
            'substitution': rf'\frac{{{Mu*1e6:.2e}}}{{{phi:.2f} \times {fy:.0f} \times {jd:.2f} \times {d:.1f}}}',
            'result': f'{As_initial:.1f} mm²',
            'variable': 'As,init'
        })
        
        # Step 4: Initial depth of compression block
        a_initial = (As_initial * fy) / (0.85 * fcu * b)
        
        calculations.append({
            'step': '3',
            'description': 'Initial Compression Block Depth',
            'formula': r"a = \frac{A_s f_y}{0.85 f'_c b}",
            'substitution': rf'\frac{{{As_initial:.1f} \times {fy:.0f}}}{{0.85 \times {fcu:.1f} \times {b:.0f}}}',
            'result': f'{a_initial:.2f} mm',
            'variable': 'a,init'
        })
        
        # Step 5: Refined As
        lever_arm = d - a_initial/2
        As_calculated = Mu_Nmm / (phi * fy * lever_arm)
        
        calculations.append({
            'step': '4',
            'description': 'Refined As',
            'formula': r'A_s = \frac{M_u}{\phi f_y (d - a/2)}',
            'substitution': rf'\frac{{{Mu*1e6:.2e}}}{{{phi:.2f} \times {fy:.0f} \times ({d:.1f} - {a_initial/2:.2f})}}',
            'result': f'{As_calculated:.1f} mm²',
            'variable': 'As,calc'
        })
        
        # Step 6: Minimum steel
        As_min_1 = (0.25 * math.sqrt(fcu) / fy) * b * d
        As_min_2 = (1.4 / fy) * b * d
        As_min = max(As_min_1, As_min_2)
        
        calculations.append({
            'step': '5',
            'description': 'Minimum As (ACI)',
            'formula': r'A_{s,min} = \max\left(\frac{0.25\sqrt{f_c^\prime}}{f_y}b_w d, \frac{1.4}{f_y}b_w d\right)',
            'substitution': rf'\max\left({As_min_1:.1f}, {As_min_2:.1f}\right)',
            'result': f'{As_min:.1f} mm²',
            'variable': 'As,min'
        })
        
        # Step 7: Required As
        As_required = max(As_calculated, As_min)
        governing = "minimum" if As_required == As_min else "calculated"
        
        calculations.append({
            'step': '6',
            'description': 'Required As',
            'formula': r'A_{s,req} = \max(A_s, A_{s,min})',
            'substitution': rf'\max({As_calculated:.1f}, {As_min:.1f})',
            'result': f'{As_required:.1f} mm² ({governing})',
            'variable': 'As,req'
        })
        
        # Step 8: Final a
        a_final = (As_required * fy) / (0.85 * fcu * b)
        
        calculations.append({
            'step': '7',
            'description': 'Final Compression Block',
            'formula': r"a = \frac{A_{s,req} f_y}{0.85 f'_c b}",
            'substitution': rf'\frac{{{As_required:.1f} \times {fy:.0f}}}{{0.85 \times {fcu:.1f} \times {b:.0f}}}',
            'result': f'{a_final:.2f} mm',
            'variable': 'a,final'
        })
        
        # Step 9: Neutral axis
        c = a_final / beta1
        
        calculations.append({
            'step': '8',
            'description': 'Neutral Axis Depth',
            'formula': r'c = \frac{a}{\beta_1}',
            'substitution': rf'\frac{{{a_final:.2f}}}{{{beta1:.2f}}}',
            'result': f'{c:.2f} mm',
            'variable': 'c'
        })
        
        # Step 10: Steel strain
        es = ((d - c) / c) * 0.003
        
        calculations.append({
            'step': '9',
            'description': 'Steel Strain',
            'formula': r'\varepsilon_s = \frac{d-c}{c} \times 0.003',
            'substitution': rf'\frac{{{d:.1f} - {c:.2f}}}{{{c:.2f}}} \times 0.003',
            'result': f'{es:.5f}',
            'variable': 'εs'
        })
        
        # Step 11: Strain check
        strain_safe = es >= 0.002
        if es >= 0.005:
            strain_status = "Tension Controlled ✓"
        elif es >= 0.002:
            strain_status = "Transition Zone ⚠"
        else:
            strain_status = "Compression Controlled ✗"
        
        calculations.append({
            'step': '10',
            'description': 'Strain Check (ACI)',
            'formula': r'\varepsilon_s \geq 0.002',
            'substitution': f'{es:.5f} ≥ 0.002',
            'result': f'{"PASS ✓" if strain_safe else "FAIL ✗"} ({strain_status})',
            'variable': 'Check'
        })
        
        # Step 12: Design capacity
        phi_Mn_Nmm = phi * As_required * fy * (d - a_final/2)
        phi_Mn = phi_Mn_Nmm / 1e6
        
        calculations.append({
            'step': '11',
            'description': 'Design Moment Capacity',
            'formula': r'\phi M_n = \phi A_{s,req} f_y (d - a/2)',
            'substitution': rf'{phi:.2f} \times {As_required:.1f} \times {fy:.0f} \times ({d:.1f} - {a_final/2:.2f})',
            'result': f'{phi_Mn:.2f} kN.m',
            'variable': 'φMn'
        })
        
        # Step 13: Capacity check
        capacity_safe = phi_Mn >= Mu
        utilization = (Mu / phi_Mn) * 100 if phi_Mn > 0 else 0
        
        calculations.append({
            'step': '12',
            'description': 'Capacity Check',
            'formula': r'\phi M_n \geq M_u',
            'substitution': f'{phi_Mn:.2f} ≥ {Mu:.2f}',
            'result': f'{"SAFE ✓" if capacity_safe else "UNSAFE ✗"} ({utilization:.1f}%)',
            'variable': 'Check'
        })
    
    # ============================================
    # ECP 203 CALCULATIONS
    # ============================================
    else:  # ECP 203
        # Material factors
        gamma_c = 1.5
        gamma_s = 1.15
        
        # Design strengths
        fcd = fcu / gamma_c  # Concrete design strength
        fyd = fy / gamma_s   # Steel design strength
        
        # Step 1: Effective depth
        calculations.append({
            'step': '1',
            'description': 'Effective Depth',
            'formula': r'd = T_s - \text{cover}',
            'substitution': f'{h:.0f} - {cover:.0f}',
            'result': f'{d:.1f} mm',
            'variable': 'd'
        })
        
        # Step 2: C1 calculation
        C1 = d / math.sqrt(fcu * b)
        
        calculations.append({
            'step': '2',
            'description': 'C1 Calculation',
            'formula': r'C_1 = \frac{d}{\sqrt{f_{cu} \times B}}',
            'substitution': rf'\frac{{{d:.1f}}}{{\sqrt{{{fcu:.1f} \times {b:.0f}}}}}',
            'result': f'{C1:.3f}',
            'variable': 'C1'
        })
        
        # Step 3: Check C1 minimum
        C1_min = 2.76
        C1_check = C1 >= C1_min
        
        calculations.append({
            'step': '3',
            'description': 'C1 Minimum Check',
            'formula': r'C_1 \geq C_{1,min} = 2.76',
            'substitution': f'{C1:.3f} ≥ {C1_min:.2f}',
            'result': f'{"PASS ✓" if C1_check else "FAIL ✗"}',
            'variable': 'Check'
        })
        
        # Step 4: J calculation
        J_calc = (1/1.15) * (0.5 + math.sqrt(0.25 - (1/(0.9 * C1**2))))
        J_max = 0.85
        J = min(J_calc, J_max)
        
        calculations.append({
            'step': '4',
            'description': 'Lever Arm Factor J',
            'formula': r'J = \frac{1}{1.15}\left(0.5 + \sqrt{0.25 - \frac{1}{0.9 \times C_1^2}}\right)',
            'substitution': rf'\frac{{1}}{{1.15}}\left(0.5 + \sqrt{{0.25 - \frac{{1}}{{0.9 \times {C1:.3f}^2}}}}\right)',
            'result': f'{J:.4f} (max={J_max})',
            'variable': 'J'
        })
        
        # Step 5: Required As
        As_required = Mu_Nmm / (fyd * J * d)
        
        calculations.append({
            'step': '5',
            'description': 'Required Steel Area',
            'formula': r'A_s = \frac{M_u}{f_{yd} \times J \times d}',
            'substitution': rf'\frac{{{Mu*1e6:.2e}}}{{{fyd:.1f} \times {J:.4f} \times {d:.1f}}}',
            'result': f'{As_required:.1f} mm²',
            'variable': 'As,req'
        })
        
        # Step 6: Minimum steel (ECP)
        rho_min = 0.6 / fy  # Minimum reinforcement ratio
        As_min = rho_min * b * d
        
        calculations.append({
            'step': '6',
            'description': 'Minimum Steel (ECP)',
            'formula': r'A_{s,min} = \frac{0.6}{f_y} \times b \times d',
            'substitution': rf'\frac{{0.6}}{{{fy:.0f}}} \times {b:.0f} \times {d:.1f}',
            'result': f'{As_min:.1f} mm²',
            'variable': 'As,min'
        })
        
        # Step 7: Final As
        As_final = max(As_required, As_min)
        governing = "minimum" if As_final == As_min else "calculated"
        
        calculations.append({
            'step': '7',
            'description': 'Final As',
            'formula': r'A_{s,final} = \max(A_s, A_{s,min})',
            'substitution': rf'\max({As_required:.1f}, {As_min:.1f})',
            'result': f'{As_final:.1f} mm² ({governing})',
            'variable': 'As,final'
        })
        
        # For compatibility with selection section
        As_required = As_final
        
        # Step 8: Neutral axis calculation
        # For ECP: x = As*fyd / (0.67*fcd*b)
        x = (As_final * fyd) / (0.67 * fcd * b)
        
        calculations.append({
            'step': '8',
            'description': 'Neutral Axis Depth',
            'formula': r'x = \frac{A_s \times f_{yd}}{0.67 \times f_{cd} \times b}',
            'substitution': rf'\frac{{{As_final:.1f} \times {fyd:.1f}}}{{0.67 \times {fcd:.1f} \times {b:.0f}}}',
            'result': f'{x:.2f} mm',
            'variable': 'x'
        })
        
        c = x  # For compatibility with later code
        
        # Step 9: x/d ratio check
        x_d_ratio = x / d
        x_d_limit = 0.45  # ECP limit
        x_d_check = x_d_ratio <= x_d_limit
        
        calculations.append({
            'step': '9',
            'description': 'x/d Ratio Check',
            'formula': r'\frac{x}{d} \leq 0.45',
            'substitution': f'{x:.2f}/{d:.1f} = {x_d_ratio:.3f}',
            'result': f'{"PASS ✓" if x_d_check else "FAIL ✗"}',
            'variable': 'Check'
        })
        
        # Step 10: Design capacity
        # Mu,design = As * fyd * (d - 0.4*x)
        Mu_design_Nmm = As_final * fyd * (d - 0.4 * x)
        Mu_design = Mu_design_Nmm / 1e6
        
        calculations.append({
            'step': '10',
            'description': 'Design Moment Capacity',
            'formula': r'M_{u,design} = A_s \times f_{yd} \times (d - 0.4x)',
            'substitution': rf'{As_final:.1f} \times {fyd:.1f} \times ({d:.1f} - 0.4 \times {x:.2f})',
            'result': f'{Mu_design:.2f} kN.m',
            'variable': 'Mu,d'
        })
        
        phi_Mn = Mu_design  # For compatibility
        
        # Step 11: Capacity check
        capacity_safe = Mu_design >= Mu
        utilization = (Mu / Mu_design) * 100 if Mu_design > 0 else 0
        
        calculations.append({
            'step': '11',
            'description': 'Capacity Check',
            'formula': r'M_{u,design} \geq M_u',
            'substitution': f'{Mu_design:.2f} ≥ {Mu:.2f}',
            'result': f'{"SAFE ✓" if capacity_safe else "UNSAFE ✗"} ({utilization:.1f}%)',
            'variable': 'Check'
        })
        
        # Calculate strain for display (approximate)
        es = 0.003 * (d - x) / x if x > 0 else 0
        strain_safe = x_d_check  # For ECP, use x/d check instead of strain
        strain_status = "Under-reinforced ✓" if x_d_check else "Over-reinforced ✗"

except ZeroDivisionError:
    st.error("❌ Calculation Error: Division by zero detected. Please check your inputs.")
    st.stop()
except Exception as e:
    st.error(f"❌ Calculation Error: {str(e)}")
    import traceback
    st.error(traceback.format_exc())
    st.stop()

# ============================================
# DISPLAY RESULTS
# ============================================

# Input Summary
st.markdown('<h2 class="section-header">📋 Input Summary</h2>', unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Design Code", code_standard)
    st.metric("Mu", f"{Mu:.2f} kN.m")
with col2:
    st.metric("b", f"{b:.0f} mm")
    st.metric("h", f"{h:.0f} mm")
with col3:
    st.metric("cover", f"{cover:.0f} mm")
    st.metric("fy", f"{fy:.0f} MPa")
with col4:
    if code_standard == 'ACI 318':
        st.metric("f'c", f"{fcu:.1f} MPa")
        st.metric("φ", f"{phi:.2f}")
    else:
        st.metric("fcu", f"{fcu:.1f} MPa")
        st.metric("γc / γs", f"{gamma_c:.1f} / {gamma_s:.2f}")

# Calculations Display
st.markdown('<h2 class="section-header">🔢 Calculations</h2>', unsafe_allow_html=True)

for calc in calculations:
    col1, col2, col3, col4 = st.columns([0.4, 2.5, 2.5, 1.6])
    
    with col1:
        st.markdown(f"**{calc['step']}**")
    
    with col2:
        st.markdown(f"**{calc['description']}:** ${calc['formula']}$")
    
    with col3:
        st.latex(calc['substitution'])
    
    with col4:
        if 'PASS' in calc['result'] or 'SAFE' in calc['result']:
            st.success(calc['result'])
        elif 'FAIL' in calc['result'] or 'UNSAFE' in calc['result']:
            st.error(calc['result'])
        else:
            st.info(f"**{calc['result']}**")

# Design Summary
st.markdown("---")
st.markdown('<h2 class="section-header">✅ Design Summary</h2>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**📏 Required Steel Area**")
    st.metric("As Required", f"{As_required:.1f} mm²")
    st.metric("Effective Depth", f"{d:.1f} mm")

with col2:
    st.markdown("**🔍 Analysis**")
    if code_standard == 'ACI 318':
        st.metric("Neutral Axis (c)", f"{c:.2f} mm")
        st.metric("c/d ratio", f"{(c/d):.3f}")
        st.metric("Steel Strain (εs)", f"{es:.5f}")
    else:
        st.metric("Neutral Axis (x)", f"{x:.2f} mm")
        st.metric("x/d ratio", f"{x_d_ratio:.3f}")
        st.metric("Design Strength", f"fyd={fyd:.1f} MPa")
    st.metric("Section Type", strain_status)

with col3:
    st.markdown("**✅ Safety Status**")
    overall_safe = strain_safe and capacity_safe
    
    if overall_safe:
        st.success("### ✅ DESIGN IS SAFE")
    else:
        st.error("### ❌ DESIGN FAILED")
    
    st.markdown("**Checks:**")
    if code_standard == 'ACI 318':
        st.markdown(f"{'✅' if strain_safe else '❌'} Steel Strain: εs={es:.5f}")
        st.markdown(f"{'✅' if capacity_safe else '❌'} Capacity: φMn={phi_Mn:.2f} kN.m")
    else:
        st.markdown(f"{'✅' if strain_safe else '❌'} x/d={x_d_ratio:.3f} ≤ 0.45")
        st.markdown(f"{'✅' if capacity_safe else '❌'} Capacity: Mu,d={Mu_design:.2f} kN.m")
    st.markdown(f"{'✅' if As_required >= As_min else '❌'} Minimum Steel")
    
    st.metric("Capacity Ratio", f"{phi_Mn/Mu:.2f}")

# Reinforcement Selection
st.markdown("---")
st.markdown('<h2 class="section-header">🔧 Reinforcement Selection</h2>', unsafe_allow_html=True)

# Auto suggestions
st.markdown("### 💡 Automatic Suggestions")
col1, col2, col3 = st.columns(3)

suggestion_count = 0
for diameter in [10, 12, 14, 16, 18, 20, 22, 25]:
    area_per_bar = rebar_data[diameter][0]
    num_bars = math.ceil(As_required / area_per_bar)
    
    if num_bars <= 9 and suggestion_count < 6:
        total_area = rebar_data[diameter][num_bars - 1]
        excess = ((total_area - As_required) / As_required) * 100
        
        if suggestion_count % 3 == 0:
            with col1:
                st.info(f"**{num_bars}Ø{diameter}**\nAs = {total_area:.0f} mm²\n(+{excess:.1f}%)")
        elif suggestion_count % 3 == 1:
            with col2:
                st.info(f"**{num_bars}Ø{diameter}**\nAs = {total_area:.0f} mm²\n(+{excess:.1f}%)")
        else:
            with col3:
                st.info(f"**{num_bars}Ø{diameter}**\nAs = {total_area:.0f} mm²\n(+{excess:.1f}%)")
        
        suggestion_count += 1

# Manual Selection
st.markdown("---")
st.markdown("### 🎯 Manual Selection & Verification")

col1, col2, col3 = st.columns([1, 1, 2])

with col1:
    selected_diameter = st.selectbox(
        "Bar Diameter (mm)",
        options=list(rebar_data.keys()),
        index=list(rebar_data.keys()).index(16)
    )

with col2:
    selected_num_bars = st.selectbox(
        "Number of Bars",
        options=list(range(1, 10)),
        index=3
    )

# Get selected reinforcement area
selected_As = rebar_data[selected_diameter][selected_num_bars - 1]

# Verify selected reinforcement
st.markdown("---")
st.markdown("### ✅ Selected Reinforcement Verification")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Selected Config", f"{selected_num_bars}Ø{selected_diameter}")

with col2:
    st.metric("Provided As", f"{selected_As:.1f} mm²")
    excess_percentage = ((selected_As - As_required) / As_required) * 100
    st.caption(f"Excess: {excess_percentage:+.1f}%")

with col3:
    check_As = selected_As >= As_required
    if check_As:
        st.success(f"✓ As Check\n{selected_As:.0f} ≥ {As_required:.0f}")
    else:
        st.error(f"✗ As Check\n{selected_As:.0f} < {As_required:.0f}")

with col4:
    # Re-calculate capacity with selected As
    if code_standard == 'ACI 318':
        a_selected = (selected_As * fy) / (0.85 * fcu * b)
        c_selected = a_selected / beta1
        es_selected = ((d - c_selected) / c_selected) * 0.003
        phi_Mn_selected = (phi * selected_As * fy * (d - a_selected/2)) / 1e6
    else:  # ECP 203
        x_selected = (selected_As * fyd) / (0.67 * fcd * b)
        phi_Mn_selected = (selected_As * fyd * (d - 0.4 * x_selected)) / 1e6
        es_selected = 0.003 * (d - x_selected) / x_selected if x_selected > 0 else 0
    
    check_capacity = phi_Mn_selected >= Mu
    if check_capacity:
        st.success(f"✓ Capacity Check\nMn = {phi_Mn_selected:.2f} kN.m")
    else:
        st.error(f"✗ Capacity Check\nMn = {phi_Mn_selected:.2f} kN.m")

# Detailed verification
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**📊 Analysis with Selected Steel**")
    if code_standard == 'ACI 318':
        st.metric("a (selected)", f"{a_selected:.2f} mm")
        st.metric("c (selected)", f"{c_selected:.2f} mm")
        st.metric("c/d ratio", f"{(c_selected/d):.3f}")
    else:
        st.metric("x (selected)", f"{x_selected:.2f} mm")
        st.metric("x/d ratio", f"{(x_selected/d):.3f}")
        st.metric("Lever arm", f"{(d - 0.4*x_selected):.1f} mm")

with col2:
    st.markdown("**⚡ Strain Analysis**")
    st.metric("εs (selected)", f"{es_selected:.5f}")
    
    if code_standard == 'ACI 318':
        if es_selected >= 0.005:
            st.success("✓ Tension Controlled")
        elif es_selected >= 0.002:
            st.warning("⚠ Transition Zone")
        else:
            st.error("✗ Compression Controlled")
    else:
        if x_selected/d <= 0.45:
            st.success("✓ Under-reinforced")
        else:
            st.error("✗ Over-reinforced")

with col3:
    st.markdown("**🎯 Final Status**")
    if code_standard == 'ACI 318':
        final_safe = check_As and check_capacity and (es_selected >= 0.002)
    else:
        final_safe = check_As and check_capacity and (x_selected/d <= 0.45)
    
    if final_safe:
        st.success("### ✅ SELECTED CONFIG IS SAFE")
    else:
        st.error("### ❌ SELECTED CONFIG FAILED")
    
    st.metric("Utilization", f"{(Mu/phi_Mn_selected)*100:.1f}%")

# Rebar Table
st.markdown("---")
st.markdown("### 📋 Complete Rebar Area Table")

df_data = []
for diameter, areas in rebar_data.items():
    row = [diameter] + areas
    df_data.append(row)

df = pd.DataFrame(df_data, columns=['Ø (mm)', '1', '2', '3', '4', '5', '6', '7', '8', '9'])
df = df.set_index('Ø (mm)')

st.dataframe(df, use_container_width=True)
st.caption("📝 Note: All areas in mm²")

# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.caption(f"🏗️ **Code**: {code_standard}")
with col2:
    st.caption("📐 **Type**: Rectangular Beam")
with col3:
    st.caption("🔧 **Version**: v18")

