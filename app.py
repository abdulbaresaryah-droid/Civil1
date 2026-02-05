import streamlit as st
import pandas as pd
import math

# Page configuration
st.set_page_config(
    page_title="RC Section Design - ACI",
    page_icon="🏗️",
    layout="wide"
)

# Custom CSS للتقليل من المسافات
st.markdown("""
    <style>
    .main-header {
        font-size: 2.2rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 0.5rem;
        margin-top: -2rem;
    }
    .section-header {
        font-size: 1.5rem;
        color: #2c3e50;
        margin-top: 0.5rem;
        margin-bottom: 0.3rem;
        border-bottom: 2px solid #1f77b4;
        padding-bottom: 0.3rem;
    }
    .stMetric {
        background-color: #f8f9fa;
        padding: 5px;
        border-radius: 3px;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.2rem;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 0.9rem;
    }
    .row-widget {
        margin-top: 0.2rem;
        margin-bottom: 0.2rem;
    }
    div[data-testid="column"] {
        padding: 0.3rem;
    }
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    hr {
        margin-top: 0.3rem;
        margin-bottom: 0.3rem;
    }
    .katex {
        font-size: 1.1em;
    }
    </style>
""", unsafe_allow_html=True)

# Default values
default_values = {
    'fy': 420.0,
    'fcu': 25.0,
    'Mu': 13.7,
    'b': 1000.0,
    'h': 150.0,
    'cover': 20.0,
    'phi': 0.9,
    'jd': 0.95,
    'beta1': 0.85
}

# Initialize session state with default values
for key, value in default_values.items():
    if key not in st.session_state:
        st.session_state[key] = value

# Reset function
def reset_values():
    for key, value in default_values.items():
        st.session_state[key] = value
    st.rerun()

# Title
st.markdown('<h1 class="main-header">🏗️ RC Section Design (ACI)</h1>', unsafe_allow_html=True)

# Sidebar for inputs
st.sidebar.header("📊 Input Parameters")

# Reset button
if st.sidebar.button("🗑️ Clear All Inputs", type="secondary", use_container_width=True):
    reset_values()

st.sidebar.markdown("---")

# Input method selection
input_method = st.sidebar.radio("Input Method", ["Sliders", "Manual Input"])

st.sidebar.markdown("---")
st.sidebar.subheader("Material Properties")

# Material properties inputs
if input_method == "Sliders":
    fy = st.sidebar.slider("Steel Yield Strength, fy (MPa)", 
                          min_value=200.0, max_value=600.0, 
                          value=st.session_state.fy,
                          step=10.0, key='fy')
    
    fcu = st.sidebar.slider("Concrete Strength, f'c (MPa)", 
                           min_value=15.0, max_value=50.0, 
                           value=st.session_state.fcu,
                           step=2.5, key='fcu')
else:
    fy = st.sidebar.number_input("Steel Yield Strength, fy (MPa)", 
                                value=st.session_state.fy,
                                min_value=0.0, max_value=600.0, 
                                step=10.0, key='fy',
                                help="Enter value > 0")
    fcu = st.sidebar.number_input("Concrete Strength, f'c (MPa)", 
                                 value=st.session_state.fcu,
                                 min_value=0.0, max_value=50.0, 
                                 step=2.5, key='fcu',
                                 help="Enter value > 0")

st.sidebar.markdown("---")
st.sidebar.subheader("Loading")

if input_method == "Sliders":
    Mu = st.sidebar.slider("Ultimate Moment, Mu (kN.m)", 
                          min_value=0.0, max_value=200.0, 
                          value=st.session_state.Mu,
                          step=0.1, key='Mu')
else:
    Mu = st.sidebar.number_input("Ultimate Moment, Mu (kN.m)", 
                                value=st.session_state.Mu,
                                min_value=0.0, 
                                step=0.1, key='Mu',
                                help="Enter value > 0")

st.sidebar.markdown("---")
st.sidebar.subheader("Section Dimensions")

if input_method == "Sliders":
    b = st.sidebar.slider("Width, b (mm)", 
                         min_value=100.0, max_value=2000.0, 
                         value=st.session_state.b,
                         step=50.0, key='b')
    
    h = st.sidebar.slider("Height, h (mm)", 
                         min_value=100.0, max_value=500.0, 
                         value=st.session_state.h,
                         step=10.0, key='h')
    
    cover = st.sidebar.slider("Cover (mm)", 
                             min_value=15.0, max_value=75.0,
                             value=st.session_state.cover,
                             step=5.0, key='cover')
else:
    b = st.sidebar.number_input("Width, b (mm)", 
                               value=st.session_state.b,
                               min_value=0.0, 
                               step=50.0, key='b',
                               help="Enter value > 0")
    h = st.sidebar.number_input("Height, h (mm)", 
                               value=st.session_state.h,
                               min_value=0.0, 
                               step=10.0, key='h',
                               help="Enter value > 0")
    cover = st.sidebar.number_input("Cover (mm)", 
                                   value=st.session_state.cover,
                                   min_value=0.0, max_value=75.0, 
                                   step=5.0, key='cover',
                                   help="Enter value > 0")

st.sidebar.markdown("---")
st.sidebar.subheader("Design Parameters")

if input_method == "Sliders":
    phi = st.sidebar.slider("Strength Reduction Factor, φ", 
                           min_value=0.65, max_value=0.9,
                           value=st.session_state.phi,
                           step=0.05, key='phi')
    jd = st.sidebar.slider("Moment Arm Factor, jd", 
                          min_value=0.85, max_value=0.95,
                          value=st.session_state.jd,
                          step=0.01, key='jd')
    beta1 = st.sidebar.slider("β₁ Factor", 
                             min_value=0.65, max_value=0.85,
                             value=st.session_state.beta1,
                             step=0.05, key='beta1')
else:
    phi = st.sidebar.number_input("Strength Reduction Factor, φ", 
                                 value=st.session_state.phi,
                                 min_value=0.0, max_value=0.9, 
                                 step=0.05, key='phi')
    jd = st.sidebar.number_input("Moment Arm Factor, jd", 
                                value=st.session_state.jd,
                                min_value=0.0, max_value=0.95, 
                                step=0.01, key='jd')
    beta1 = st.sidebar.number_input("β₁ Factor", 
                                   value=st.session_state.beta1,
                                   min_value=0.0, max_value=0.85, 
                                   step=0.05, key='beta1')

# Validation
all_inputs_valid = all([
    fy and fy > 0,
    fcu and fcu > 0,
    Mu and Mu > 0,
    b and b > 0,
    h and h > 0,
    cover and cover > 0,
    phi and phi > 0,
    jd and jd > 0,
    beta1 and beta1 > 0
])

if not all_inputs_valid:
    st.warning("⚠️ Please enter all input values to proceed with calculations")
    st.info("💡 Use the sidebar to input all required parameters")
    st.stop()

# Perform calculations
d = h - cover
Mu_Nmm = Mu * 1e6
As_initial = Mu_Nmm / (phi * fy * jd * d)
a_initial = (As_initial * fy) / (0.85 * fcu * b)
As_calculated = Mu_Nmm / (phi * fy * (d - a_initial/2))
As_min = (1.4 * b * d) / fy
As_required = max(As_calculated, As_min)
a_final = (As_required * fy) / (0.85 * fcu * b)
c = a_final / beta1
es = ((d - c) / c) * 0.003
phi_Mn_Nmm = phi * As_required * fy * (d - a_final/2)
phi_Mn = phi_Mn_Nmm / 1e6

# Input Summary
st.markdown('<h2 class="section-header">📋 Input Summary</h2>', unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Mu", f"{Mu} kN.m")
    st.metric("b", f"{b} mm")
with col2:
    st.metric("h", f"{h} mm")
    st.metric("cover", f"{cover} mm")
with col3:
    st.metric("fy", f"{fy} MPa")
    st.metric("f'c", f"{fcu} MPa")
with col4:
    st.metric("φ", f"{phi}")
    st.metric("jd", f"{jd}")

# Design Calculations
st.markdown('<h2 class="section-header">🔢 Calculations</h2>', unsafe_allow_html=True)

# Headers
col1, col2, col3 = st.columns([2, 2, 1.2])
with col1:
    st.markdown("**Formula**")
with col2:
    st.markdown("**Substitution**")
with col3:
    st.markdown("**Result**")

st.markdown("---")

# Step 1: d
col1, col2, col3 = st.columns([2, 2, 1.2])
with col1:
    st.markdown("**1. Effective Depth**")
    st.latex(r'd = h - \text{cover}')
with col2:
    st.code(f'{h} - {cover}', language='python')
with col3:
    st.metric("d", f"{d:.1f} mm")

# Step 2: As initial
col1, col2, col3 = st.columns([2, 2, 1.2])
with col1:
    st.markdown("**2. Initial As**")
    st.latex(r'A_s = \frac{M_u}{\phi f_y jd \cdot d}')
with col2:
    st.code(f'{Mu*1e6:.1e}/({phi}×{fy}×{jd}×{d:.1f})', language='python')
with col3:
    st.metric("As,init", f"{As_initial:.1f} mm²")

# Step 3: a
col1, col2, col3 = st.columns([2, 2, 1.2])
with col1:
    st.markdown("**3. Depth of Block**")
    st.latex(r"a = \frac{A_s f_y}{0.85 f'_c b}")
with col2:
    st.code(f'({As_initial:.1f}×{fy})/(0.85×{fcu}×{b})', language='python')
with col3:
    st.metric("a", f"{a_initial:.2f} mm")

# Step 4: As
col1, col2, col3 = st.columns([2, 2, 1.2])
with col1:
    st.markdown("**4. Refined As**")
    st.latex(r'A_s = \frac{M_u}{\phi f_y (d - a/2)}')
with col2:
    st.code(f'{Mu*1e6:.1e}/({phi}×{fy}×{d-a_initial/2:.1f})', language='python')
with col3:
    st.metric("As,calc", f"{As_calculated:.1f} mm²")

# Step 5: As min
col1, col2, col3 = st.columns([2, 2, 1.2])
with col1:
    st.markdown("**5. Minimum As**")
    st.latex(r'A_{s,min} = \frac{1.4 bd}{f_y}')
with col2:
    st.code(f'(1.4×{b}×{d:.1f})/{fy}', language='python')
with col3:
    st.metric("As,min", f"{As_min:.1f} mm²")

# Step 6: Check As
col1, col2, col3 = st.columns([2, 2, 1.2])
governing = "minimum" if As_required == As_min else "calculated"
with col1:
    st.markdown("**6. Required As**")
    st.latex(r'A_{s,req} = \max(A_s, A_{s,min})')
with col2:
    st.code(f'max({As_calculated:.1f}, {As_min:.1f})', language='python')
with col3:
    st.metric("As,req", f"{As_required:.1f} mm²")
    st.caption(f"*({governing})*")

# Step 7: Final a
col1, col2, col3 = st.columns([2, 2, 1.2])
with col1:
    st.markdown("**7. Final a**")
    st.latex(r"a = \frac{A_{s,req} f_y}{0.85 f'_c b}")
with col2:
    st.code(f'({As_required:.1f}×{fy})/(0.85×{fcu}×{b})', language='python')
with col3:
    st.metric("a,final", f"{a_final:.2f} mm")

# Step 8: c
col1, col2, col3 = st.columns([2, 2, 1.2])
with col1:
    st.markdown("**8. Neutral Axis**")
    st.latex(r'c = \frac{a}{\beta_1}')
with col2:
    st.code(f'{a_final:.2f}/{beta1}', language='python')
with col3:
    st.metric("c", f"{c:.2f} mm")

# Step 9: εs
col1, col2, col3 = st.columns([2, 2, 1.2])
with col1:
    st.markdown("**9. Steel Strain**")
    st.latex(r'\varepsilon_s = \frac{d-c}{c} \times 0.003')
with col2:
    st.code(f'({d:.1f}-{c:.2f})/{c:.2f}×0.003', language='python')
with col3:
    st.metric("εs", f"{es:.5f}")

# Step 10: Check εs
col1, col2, col3 = st.columns([2, 2, 1.2])
strain_safe = es >= 0.002
if es >= 0.005:
    strain_status = "Tension Controlled"
    strain_color = "🟢"
elif es >= 0.002:
    strain_status = "Transition Zone"
    strain_color = "🟡"
else:
    strain_status = "Compression Controlled"
    strain_color = "🔴"

with col1:
    st.markdown("**10. Check εs**")
    st.latex(r'\varepsilon_s \geq 0.002')
with col2:
    st.code(f'{es:.5f} ≥ 0.002', language='python')
with col3:
    if strain_safe:
        st.success("✓ PASS")
    else:
        st.error("✗ FAIL")
    st.caption(f"{strain_color} {strain_status}")

# Step 11: φMn
col1, col2, col3 = st.columns([2, 2, 1.2])
with col1:
    st.markdown("**11. Design Capacity**")
    st.latex(r'\phi M_n = \phi A_{s,req} f_y (d - a/2)')
with col2:
    st.code(f'{phi}×{As_required:.1f}×{fy}×{d-a_final/2:.1f}', language='python')
with col3:
    st.metric("φMn", f"{phi_Mn:.2f} kN.m")

# Step 12: Check φMn
col1, col2, col3 = st.columns([2, 2, 1.2])
capacity_safe = phi_Mn >= Mu
utilization = (Mu / phi_Mn) * 100 if phi_Mn > 0 else 0

with col1:
    st.markdown("**12. Capacity Check**")
    st.latex(r'\phi M_n \geq M_u')
with col2:
    st.code(f'{phi_Mn:.2f} ≥ {Mu}', language='python')
with col3:
    if capacity_safe:
        st.success("✓ SAFE")
    else:
        st.error("✗ UNSAFE")
    st.caption(f"Utilization: {utilization:.1f}%")

# Summary
st.markdown("---")
st.markdown('<h2 class="section-header">✅ Design Summary</h2>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**📏 Reinforcement**")
    st.metric("As Required", f"{As_required:.1f} mm²")
    st.metric("Effective Depth", f"{d:.1f} mm")
    
    st.markdown("**💡 Bar Suggestions:**")
    rebar_sizes = [(10, 78.5), (12, 113.1), (16, 201.1), (20, 314.2), (25, 490.9)]
    suggestions_shown = 0
    for size, area in rebar_sizes:
        num_bars = math.ceil(As_required / area)
        if num_bars <= 12 and suggestions_shown < 4:
            total_area = num_bars * area
            excess = ((total_area - As_required) / As_required) * 100
            st.caption(f"• {num_bars}Ø{size} = {total_area:.0f} mm² (+{excess:.1f}%)")
            suggestions_shown += 1

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
    st.markdown(f"{'✅' if capacity_safe else '❌'} Capacity: φMn={phi_Mn:.2f} {'≥' if capacity_safe else '<'} Mu={Mu}")
    st.markdown(f"{'✅' if As_required >= As_min else '❌'} Minimum Steel: {As_required:.0f} {'≥' if As_required >= As_min else '<'} {As_min:.0f} mm²")
    
    st.metric("Capacity Ratio", f"{phi_Mn/Mu:.2f}")

# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.caption("🏗️ **Code**: ACI 318")
with col2:
    st.caption("📐 **Type**: Rectangular Beam")
with col3:
    st.caption("🔧 **Analysis**: Flexural Design")
