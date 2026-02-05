import streamlit as st
import pandas as pd
import math

# Page configuration
st.set_page_config(
    page_title="RC Section Design - ACI & ECP",
    page_icon="🏗️",
    layout="wide"
)

# Custom CSS
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
    </style>
""", unsafe_allow_html=True)

# Rebar data table
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

# Initialize session state for sync
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    # Initialize all values
    st.session_state.fy_val = 0.0
    st.session_state.fcu_val = 0.0
    st.session_state.Mu_val = 0.0
    st.session_state.b_val = 0.0
    st.session_state.h_val = 0.0
    st.session_state.cover_val = 0.0
    st.session_state.phi_val = 0.0
    st.session_state.jd_val = 0.0
    st.session_state.beta1_val = 0.0

# Reset function - clears both slider and manual input
def clear_all_inputs():
    st.session_state.fy_val = 0.0
    st.session_state.fcu_val = 0.0
    st.session_state.Mu_val = 0.0
    st.session_state.b_val = 0.0
    st.session_state.h_val = 0.0
    st.session_state.cover_val = 0.0
    st.session_state.phi_val = 0.0
    st.session_state.jd_val = 0.0
    st.session_state.beta1_val = 0.0
    
    # Clear the keys
    keys_to_delete = ['fy', 'fcu', 'Mu', 'b', 'h', 'cover', 'phi', 'jd', 'beta1',
                      'fy_manual', 'fcu_manual', 'Mu_manual', 'b_manual', 
                      'h_manual', 'cover_manual', 'phi_manual', 'jd_manual', 'beta1_manual']
    for key in keys_to_delete:
        if key in st.session_state:
            del st.session_state[key]

# Title
st.markdown('<h1 class="main-header">🏗️ RC Section Design (ACI & ECP)</h1>', unsafe_allow_html=True)

# Sidebar
st.sidebar.header("📊 Input Parameters")

# Design Code Selection
design_code = st.sidebar.selectbox(
    "🔧 Design Code",
    ["ACI 318", "Egyptian Code (ECP 203)"],
    index=0
)

# Clear button
if st.sidebar.button("🗑️ Clear All Inputs", type="secondary", use_container_width=True):
    clear_all_inputs()
    st.rerun()

st.sidebar.markdown("---")

# Input method
input_method = st.sidebar.radio("Input Method", ["Sliders", "Manual Input"])

st.sidebar.markdown("---")
st.sidebar.subheader("Material Properties")

# Sync function
def sync_value(key, value):
    st.session_state[f'{key}_val'] = value

# Material properties with sync
if input_method == "Sliders":
    st.sidebar.info("💡 Values are synced between methods")
    
    fy = st.sidebar.slider("Steel Yield Strength, fy (MPa)", 
                          min_value=0.0, max_value=600.0, 
                          value=st.session_state.fy_val, 
                          step=10.0, key='fy',
                          on_change=sync_value, args=('fy', st.session_state.get('fy', 0.0)))
    st.session_state.fy_val = fy
    
    fcu = st.sidebar.slider("Concrete Strength, f'c/fcu (MPa)", 
                           min_value=0.0, max_value=50.0, 
                           value=st.session_state.fcu_val, 
                           step=2.5, key='fcu',
                           on_change=sync_value, args=('fcu', st.session_state.get('fcu', 0.0)))
    st.session_state.fcu_val = fcu
else:
    fy_input = st.sidebar.number_input("Steel Yield Strength, fy (MPa)", 
                                value=st.session_state.fy_val if st.session_state.fy_val > 0 else None, 
                                min_value=0.0, max_value=600.0, 
                                step=10.0, key='fy_manual', placeholder="Enter fy")
    if fy_input is not None:
        st.session_state.fy_val = fy_input
        fy = fy_input
    else:
        fy = None
    
    fcu_input = st.sidebar.number_input("Concrete Strength, f'c/fcu (MPa)", 
                                 value=st.session_state.fcu_val if st.session_state.fcu_val > 0 else None, 
                                 min_value=0.0, max_value=50.0, 
                                 step=2.5, key='fcu_manual', placeholder="Enter f'c/fcu")
    if fcu_input is not None:
        st.session_state.fcu_val = fcu_input
        fcu = fcu_input
    else:
        fcu = None

st.sidebar.markdown("---")
st.sidebar.subheader("Loading")

if input_method == "Sliders":
    Mu = st.sidebar.slider("Ultimate Moment, Mu (kN.m)", 
                          min_value=0.0, max_value=500.0, 
                          value=st.session_state.Mu_val, 
                          step=0.5, key='Mu')
    st.session_state.Mu_val = Mu
else:
    Mu_input = st.sidebar.number_input("Ultimate Moment, Mu (kN.m)", 
                                value=st.session_state.Mu_val if st.session_state.Mu_val > 0 else None, 
                                min_value=0.0, 
                                step=0.1, key='Mu_manual', placeholder="Enter Mu")
    if Mu_input is not None:
        st.session_state.Mu_val = Mu_input
        Mu = Mu_input
    else:
        Mu = None

st.sidebar.markdown("---")
st.sidebar.subheader("Section Dimensions")

if input_method == "Sliders":
    b = st.sidebar.slider("Width, b (mm)", 
                         min_value=0.0, max_value=2000.0, 
                         value=st.session_state.b_val, 
                         step=50.0, key='b')
    st.session_state.b_val = b
    
    h = st.sidebar.slider("Height, h (mm)", 
                         min_value=0.0, max_value=1000.0, 
                         value=st.session_state.h_val, 
                         step=10.0, key='h')
    st.session_state.h_val = h
    
    cover = st.sidebar.slider("Cover (mm)", 
                             min_value=0.0, max_value=75.0,
                             value=st.session_state.cover_val, 
                             step=5.0, key='cover')
    st.session_state.cover_val = cover
else:
    b_input = st.sidebar.number_input("Width, b (mm)", 
                               value=st.session_state.b_val if st.session_state.b_val > 0 else None, 
                               min_value=0.0, 
                               step=50.0, key='b_manual', placeholder="Enter b")
    if b_input is not None:
        st.session_state.b_val = b_input
        b = b_input
    else:
        b = None
    
    h_input = st.sidebar.number_input("Height, h (mm)", 
                               value=st.session_state.h_val if st.session_state.h_val > 0 else None, 
                               min_value=0.0, 
                               step=10.0, key='h_manual', placeholder="Enter h")
    if h_input is not None:
        st.session_state.h_val = h_input
        h = h_input
    else:
        h = None
    
    cover_input = st.sidebar.number_input("Cover (mm)", 
                                   value=st.session_state.cover_val if st.session_state.cover_val >= 0 else None, 
                                   min_value=0.0, max_value=75.0, 
                                   step=5.0, key='cover_manual', placeholder="Enter cover")
    if cover_input is not None:
        st.session_state.cover_val = cover_input
        cover = cover_input
    else:
        cover = None

st.sidebar.markdown("---")
st.sidebar.subheader("Design Parameters")

if design_code == "ACI 318":
    if input_method == "Sliders":
        phi = st.sidebar.slider("Strength Reduction Factor, φ", 
                               min_value=0.0, max_value=0.9,
                               value=st.session_state.phi_val, 
                               step=0.05, key='phi')
        st.session_state.phi_val = phi
        
        jd = st.sidebar.slider("Moment Arm Factor, jd", 
                              min_value=0.0, max_value=0.95,
                              value=st.session_state.jd_val, 
                              step=0.01, key='jd')
        st.session_state.jd_val = jd
        
        beta1 = st.sidebar.slider("β₁ Factor", 
                                 min_value=0.0, max_value=0.85,
                                 value=st.session_state.beta1_val, 
                                 step=0.05, key='beta1')
        st.session_state.beta1_val = beta1
    else:
        phi_input = st.sidebar.number_input("Strength Reduction Factor, φ", 
                                     value=st.session_state.phi_val if st.session_state.phi_val > 0 else None, 
                                     min_value=0.0, max_value=0.9, 
                                     step=0.05, key='phi_manual', placeholder="Enter φ")
        if phi_input is not None:
            st.session_state.phi_val = phi_input
            phi = phi_input
        else:
            phi = None
        
        jd_input = st.sidebar.number_input("Moment Arm Factor, jd", 
                                    value=st.session_state.jd_val if st.session_state.jd_val > 0 else None, 
                                    min_value=0.0, max_value=0.95, 
                                    step=0.01, key='jd_manual', placeholder="Enter jd")
        if jd_input is not None:
            st.session_state.jd_val = jd_input
            jd = jd_input
        else:
            jd = None
        
        beta1_input = st.sidebar.number_input("β₁ Factor", 
                                       value=st.session_state.beta1_val if st.session_state.beta1_val > 0 else None, 
                                       min_value=0.0, max_value=0.85, 
                                       step=0.05, key='beta1_manual', placeholder="Enter β₁")
        if beta1_input is not None:
            st.session_state.beta1_val = beta1_input
            beta1 = beta1_input
        else:
            beta1 = None

# Validation
if design_code == "ACI 318":
    if input_method == "Sliders":
        all_inputs_valid = all([
            fy > 0, fcu > 0, Mu > 0, b > 0, h > 0, cover >= 0,
            h > cover, phi > 0, jd > 0, beta1 > 0
        ])
    else:
        all_inputs_valid = all([
            fy is not None and fy > 0,
            fcu is not None and fcu > 0,
            Mu is not None and Mu > 0,
            b is not None and b > 0,
            h is not None and h > 0,
            cover is not None and cover >= 0,
            h is not None and cover is not None and h > cover,
            phi is not None and phi > 0,
            jd is not None and jd > 0,
            beta1 is not None and beta1 > 0
        ])
else:  # Egyptian Code
    if input_method == "Sliders":
        all_inputs_valid = all([
            fy > 0, fcu > 0, Mu > 0, b > 0, h > 0, cover >= 0, h > cover
        ])
    else:
        all_inputs_valid = all([
            fy is not None and fy > 0,
            fcu is not None and fcu > 0,
            Mu is not None and Mu > 0,
            b is not None and b > 0,
            h is not None and h > 0,
            cover is not None and cover >= 0,
            h is not None and cover is not None and h > cover
        ])

if not all_inputs_valid:
    st.warning("⚠️ Please enter all input values to proceed with calculations")
    if input_method == "Sliders":
        st.info("💡 Set all sliders to appropriate values")
    else:
        st.info("💡 Fill in all required parameters in the sidebar")
    st.stop()

# Calculations based on selected code
try:
    d = h - cover
    
    if d <= 0:
        st.error("❌ Error: Effective depth d = h - cover must be > 0")
        st.stop()
    
    Mu_Nmm = Mu * 1e6
    
    if design_code == "ACI 318":
        # ACI Code calculations
        As_initial = Mu_Nmm / (phi * fy * jd * d)
        a_initial = (As_initial * fy) / (0.85 * fcu * b)
        As_calculated = Mu_Nmm / (phi * fy * (d - a_initial/2))
        
        As_min_1 = (0.25 * math.sqrt(fcu) / fy) * b * d
        As_min_2 = (1.4 / fy) * b * d
        As_min = max(As_min_1, As_min_2)
        
        As_required = max(As_calculated, As_min)
        a_final = (As_required * fy) / (0.85 * fcu * b)
        c = a_final / beta1
        es = ((d - c) / c) * 0.003
        phi_Mn_Nmm = phi * As_required * fy * (d - a_final/2)
        phi_Mn = phi_Mn_Nmm / 1e6
        
        strain_safe = es >= 0.002
        capacity_safe = phi_Mn >= Mu
        
        if es >= 0.005:
            strain_status = "Tension ✓"
        elif es >= 0.002:
            strain_status = "Transition ⚠"
        else:
            strain_status = "Compression ✗"
        
        utilization = (Mu / phi_Mn) * 100 if phi_Mn > 0 else 0
        
    else:  # Egyptian Code
        # Egyptian Code calculations
        # C1 = d / √(fcu × b)
        C1 = d / math.sqrt(fcu * b)
        C1_min = 2.76
        
        # Check if C1 > C1_min
        if C1 <= C1_min:
            st.warning(f"⚠️ C1 = {C1:.2f} ≤ C1_min = {C1_min}")
        
        # J = (1/1.15) × (0.5 + √(0.25 - Mu/(0.9 × C1²)))
        # Mu here should be in ton.m, we have kN.m
        # Convert: 1 kN.m = 0.102 ton.m (approximately)
        Mu_tonm = Mu * 0.102
        
        term_inside_sqrt = 0.25 - (Mu_tonm / (0.9 * C1 * C1))
        
        if term_inside_sqrt < 0:
            st.error("❌ Error: Section is too small. Increase dimensions or reduce moment.")
            st.stop()
        
        J_calculated = (1/1.15) * (0.5 + math.sqrt(term_inside_sqrt))
        
        # J_max (typically 0.95 for Egyptian Code)
        J_max = 0.95
        J = min(J_calculated, J_max)
        
        # As = Mu / (fy × J × d)
        # Using Mu in kN.m and converting properly
        As_required = (Mu_tonm * 1e7) / (fy * J * d)  # ton.m to kg.cm, then to mm²
        
        # Minimum steel (Egyptian Code)
        # As_min = 0.6/fy × b × d (for main reinforcement)
        As_min = (0.6 / fy) * b * d
        
        As_required = max(As_required, As_min)
        
        # Check strain and capacity
        # a = As × fy / (0.67 × fcu × b) for Egyptian Code
        a_final = (As_required * fy) / (0.67 * fcu * b)
        c = a_final / 0.8  # β1 = 0.8 for Egyptian Code
        es = ((d - c) / c) * 0.003
        
        # Capacity
        phi_Mn_Nmm = 0.9 * As_required * fy * (d - a_final/2)
        phi_Mn = phi_Mn_Nmm / 1e6
        
        strain_safe = es >= 0.002
        capacity_safe = phi_Mn >= Mu
        
        if es >= 0.005:
            strain_status = "Tension ✓"
        elif es >= 0.002:
            strain_status = "Transition ⚠"
        else:
            strain_status = "Compression ✗"
        
        utilization = (Mu / phi_Mn) * 100 if phi_Mn > 0 else 0

except ZeroDivisionError:
    st.error("❌ Calculation Error: Division by zero detected. Please check your inputs.")
    st.stop()
except Exception as e:
    st.error(f"❌ Calculation Error: {str(e)}")
    st.stop()

# Display code indicator
st.markdown(f"**📘 Design Code: {design_code}**")
st.markdown("---")

# Input Summary
st.markdown('<h2 class="section-header">📋 Input Summary</h2>', unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Mu", f"{Mu:.2f} kN.m")
    st.metric("b", f"{b:.0f} mm")
with col2:
    st.metric("h", f"{h:.0f} mm")
    st.metric("cover", f"{cover:.0f} mm")
with col3:
    st.metric("fy", f"{fy:.0f} MPa")
    st.metric("f'c/fcu", f"{fcu:.1f} MPa")
with col4:
    if design_code == "ACI 318":
        st.metric("φ", f"{phi:.2f}")
        st.metric("jd", f"{jd:.2f}")
    else:
        st.metric("Design Code", "ECP 203")

# Calculations
st.markdown('<h2 class="section-header">🔢 Calculations</h2>', unsafe_allow_html=True)

if design_code == "ACI 318":
    # ACI Calculations Display
    calculations = []
    
    calculations.append({
        'step': '1', 'description': 'Effective Depth',
        'formula': r'd = h - \text{cover}',
        'substitution': rf'{h:.0f} - {cover:.0f}',
        'result': f'{d:.1f} mm', 'variable': 'd'
    })
    
    calculations.append({
        'step': '2', 'description': 'Initial As',
        'formula': r'A_s = \frac{M_u}{\phi f_y jd \cdot d}',
        'substitution': rf'\frac{{{Mu*1e6:.2e}}}{{{phi:.2f} \times {fy:.0f} \times {jd:.2f} \times {d:.1f}}}',
        'result': f'{As_initial:.1f} mm²', 'variable': 'As,init'
    })
    
    calculations.append({
        'step': '3', 'description': 'Depth of Block',
        'formula': r"a = \frac{A_s f_y}{0.85 f'_c b}",
        'substitution': rf'\frac{{{As_initial:.1f} \times {fy:.0f}}}{{0.85 \times {fcu:.1f} \times {b:.0f}}}',
        'result': f'{a_initial:.2f} mm', 'variable': 'a'
    })
    
    calculations.append({
        'step': '4', 'description': 'Refined As',
        'formula': r'A_s = \frac{M_u}{\phi f_y (d - a/2)}',
        'substitution': rf'\frac{{{Mu*1e6:.2e}}}{{{phi:.2f} \times {fy:.0f} \times ({d:.1f} - {a_initial/2:.2f})}}',
        'result': f'{As_calculated:.1f} mm²', 'variable': 'As,calc'
    })
    
    calculations.append({
        'step': '5', 'description': 'Minimum As',
        'formula': r'A_{s,min} = \max\left(\frac{0.25\sqrt{f_c^\prime}}{f_y}b_w d, \frac{1.4}{f_y}b_w d\right)',
        'substitution': rf'\max\left(\frac{{0.25 \times {math.sqrt(fcu):.2f}}}{{{fy:.0f}}} \times {b:.0f} \times {d:.1f}, \frac{{1.4}}{{{fy:.0f}}} \times {b:.0f} \times {d:.1f}\right)',
        'result': f'{As_min:.1f} mm²', 'variable': 'As,min'
    })
    
    governing = "minimum" if As_required == As_min else "calculated"
    calculations.append({
        'step': '6', 'description': 'Required As',
        'formula': r'A_{s,req} = \max(A_s, A_{s,min})',
        'substitution': rf'\max({As_calculated:.1f}, {As_min:.1f})',
        'result': f'{As_required:.1f} mm² ({governing})', 'variable': 'As,req'
    })
    
    calculations.append({
        'step': '7', 'description': 'Final a',
        'formula': r"a = \frac{A_{s,req} f_y}{0.85 f'_c b}",
        'substitution': rf'\frac{{{As_required:.1f} \times {fy:.0f}}}{{0.85 \times {fcu:.1f} \times {b:.0f}}}',
        'result': f'{a_final:.2f} mm', 'variable': 'a,final'
    })
    
    calculations.append({
        'step': '8', 'description': 'Neutral Axis',
        'formula': r'c = \frac{a}{\beta_1}',
        'substitution': rf'\frac{{{a_final:.2f}}}{{{beta1:.2f}}}',
        'result': f'{c:.2f} mm', 'variable': 'c'
    })
    
    calculations.append({
        'step': '9', 'description': 'Steel Strain',
        'formula': r'\varepsilon_s = \frac{d-c}{c} \times 0.003',
        'substitution': rf'\frac{{{d:.1f} - {c:.2f}}}{{{c:.2f}}} \times 0.003',
        'result': f'{es:.5f}', 'variable': 'εs'
    })
    
    calculations.append({
        'step': '10', 'description': 'Check εs',
        'formula': r'\varepsilon_s \geq 0.002',
        'substitution': f'{es:.5f} ≥ 0.002',
        'result': f'{"PASS ✓" if strain_safe else "FAIL ✗"} ({strain_status})', 'variable': 'Check'
    })
    
    calculations.append({
        'step': '11', 'description': 'Design Capacity',
        'formula': r'\phi M_n = \phi A_{s,req} f_y (d - a/2)',
        'substitution': rf'{phi:.2f} \times {As_required:.1f} \times {fy:.0f} \times ({d:.1f} - {a_final/2:.2f})',
        'result': f'{phi_Mn:.2f} kN.m', 'variable': 'φMn'
    })
    
    calculations.append({
        'step': '12', 'description': 'Capacity Check',
        'formula': r'\phi M_n \geq M_u',
        'substitution': f'{phi_Mn:.2f} ≥ {Mu:.2f}',
        'result': f'{"SAFE ✓" if capacity_safe else "UNSAFE ✗"} ({utilization:.1f}%)', 'variable': 'Check'
    })

else:  # Egyptian Code
    calculations = []
    
    calculations.append({
        'step': '1', 'description': 'Effective Depth',
        'formula': r'd = T_s - \text{cover}',
        'substitution': rf'{h:.0f} - {cover:.0f}',
        'result': f'{d:.1f} mm', 'variable': 'd'
    })
    
    calculations.append({
        'step': '2', 'description': 'C₁ Factor',
        'formula': r'C_1 = \frac{d}{\sqrt{f_{cu} \times B}}',
        'substitution': rf'\frac{{{d:.1f}}}{{\sqrt{{{fcu:.1f} \times {b:.0f}}}}}',
        'result': f'{C1:.3f}', 'variable': 'C₁'
    })
    
    calculations.append({
        'step': '3', 'description': 'Check C₁',
        'formula': r'C_1 > C_{1,min} = 2.76',
        'substitution': f'{C1:.3f} > 2.76',
        'result': f'{"PASS ✓" if C1 > C1_min else "FAIL ✗"}', 'variable': 'Check'
    })
    
    calculations.append({
        'step': '4', 'description': 'J Factor',
        'formula': r'J = \frac{1}{1.15}\left(0.5 + \sqrt{0.25 - \frac{M_u}{0.9 \times C_1^2}}\right)',
        'substitution': rf'\frac{{1}}{{1.15}}\left(0.5 + \sqrt{{0.25 - \frac{{{Mu_tonm:.3f}}}{{0.9 \times {C1:.3f}^2}}}}\right)',
        'result': f'{J_calculated:.4f}', 'variable': 'J'
    })
    
    calculations.append({
        'step': '5', 'description': 'J Maximum',
        'formula': r'J_{max} = 0.95',
        'substitution': f'J = min({J_calculated:.4f}, 0.95)',
        'result': f'{J:.4f}', 'variable': 'J,final'
    })
    
    calculations.append({
        'step': '6', 'description': 'Required As',
        'formula': r'A_s = \frac{M_u}{f_y \times J \times d}',
        'substitution': rf'\frac{{{Mu_tonm:.3f} \times 10^7}}{{{fy:.0f} \times {J:.4f} \times {d:.1f}}}',
        'result': f'{As_required:.1f} mm²', 'variable': 'As'
    })
    
    calculations.append({
        'step': '7', 'description': 'Minimum As',
        'formula': r'A_{s,min} = \frac{0.6}{f_y} \times b \times d',
        'substitution': rf'\frac{{0.6}}{{{fy:.0f}}} \times {b:.0f} \times {d:.1f}',
        'result': f'{As_min:.1f} mm²', 'variable': 'As,min'
    })
    
    calculations.append({
        'step': '8', 'description': 'Steel Strain',
        'formula': r'\varepsilon_s = \frac{d-c}{c} \times 0.003',
        'substitution': rf'\frac{{{d:.1f} - {c:.2f}}}{{{c:.2f}}} \times 0.003',
        'result': f'{es:.5f}', 'variable': 'εs'
    })
    
    calculations.append({
        'step': '9', 'description': 'Design Capacity',
        'formula': r'\phi M_n = 0.9 \times A_s \times f_y \times (d - a/2)',
        'substitution': rf'0.9 \times {As_required:.1f} \times {fy:.0f} \times ({d:.1f} - {a_final/2:.2f})',
        'result': f'{phi_Mn:.2f} kN.m', 'variable': 'φMn'
    })
    
    calculations.append({
        'step': '10', 'description': 'Capacity Check',
        'formula': r'\phi M_n \geq M_u',
        'substitution': f'{phi_Mn:.2f} ≥ {Mu:.2f}',
        'result': f'{"SAFE ✓" if capacity_safe else "UNSAFE ✗"} ({utilization:.1f}%)', 'variable': 'Check'
    })

# Display calculations
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

# Summary
st.markdown("---")
st.markdown('<h2 class="section-header">✅ Design Summary</h2>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**📏 Required Steel Area**")
    st.metric("As Required", f"{As_required:.1f} mm²")
    st.metric("Effective Depth", f"{d:.1f} mm")

with col2:
    st.markdown("**🔍 Analysis**")
    st.metric("Neutral Axis (c)", f"{c:.2f} mm")
    st.metric("c/d ratio", f"{(c/d):.3f}")
    st.metric("Steel Strain (εs)", f"{es:.5f}")
    st.metric("Section Type", strain_status)

with col3:
    st.markdown("**✅ Safety Status**")
    overall_safe = strain_safe and capacity_safe
    
    if overall_safe:
        st.success("### ✅ DESIGN IS SAFE")
    else:
        st.error("### ❌ DESIGN FAILED")
    
    st.markdown("**Checks:**")
    st.markdown(f"{'✅' if strain_safe else '❌'} Steel Strain: {es:.5f} {'≥' if strain_safe else '<'} 0.002")
    st.markdown(f"{'✅' if capacity_safe else '❌'} Capacity: φMn={phi_Mn:.2f} {'≥' if capacity_safe else '<'} Mu={Mu:.2f}")
    st.markdown(f"{'✅' if As_required >= As_min else '❌'} Minimum Steel")
    
    st.metric("Capacity Ratio", f"{phi_Mn/Mu:.2f}")

# Reinforcement Selection Section
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
    if design_code == "ACI 318":
        a_selected = (selected_As * fy) / (0.85 * fcu * b)
        c_selected = a_selected / beta1
    else:
        a_selected = (selected_As * fy) / (0.67 * fcu * b)
        c_selected = a_selected / 0.8
    
    es_selected = ((d - c_selected) / c_selected) * 0.003
    
    if design_code == "ACI 318":
        phi_Mn_selected = (phi * selected_As * fy * (d - a_selected/2)) / 1e6
    else:
        phi_Mn_selected = (0.9 * selected_As * fy * (d - a_selected/2)) / 1e6
    
    check_capacity = phi_Mn_selected >= Mu
    if check_capacity:
        st.success(f"✓ Capacity Check\nφMn = {phi_Mn_selected:.2f} kN.m")
    else:
        st.error(f"✗ Capacity Check\nφMn = {phi_Mn_selected:.2f} kN.m")

# Detailed verification
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**📊 Analysis with Selected Steel**")
    st.metric("a (selected)", f"{a_selected:.2f} mm")
    st.metric("c (selected)", f"{c_selected:.2f} mm")
    st.metric("c/d ratio", f"{(c_selected/d):.3f}")

with col2:
    st.markdown("**⚡ Strain Analysis**")
    st.metric("εs (selected)", f"{es_selected:.5f}")
    
    if es_selected >= 0.005:
        st.success("✓ Tension Controlled")
    elif es_selected >= 0.002:
        st.warning("⚠ Transition Zone")
    else:
        st.error("✗ Compression Controlled")

with col3:
    st.markdown("**🎯 Final Status**")
    final_safe = check_As and check_capacity and (es_selected >= 0.002)
    
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
    st.caption(f"🏗️ **Code**: {design_code}")
with col2:
    st.caption("📐 **Type**: Rectangular Beam")
with col3:
    st.caption("🔧 **Analysis**: Flexural Design")
