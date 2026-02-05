import streamlit as st
import pandas as pd
import math

# Page configuration
st.set_page_config(
    page_title="RC Section Design - ACI",
    page_icon="🏗️",
    layout="wide"
)

# Initialize session state
if 'reset' not in st.session_state:
    st.session_state.reset = False

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

# Reset function
def reset_values():
    for key in default_values:
        st.session_state[key] = default_values[key]
    st.session_state.reset = True

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.8rem;
        color: #2c3e50;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        border-bottom: 3px solid #1f77b4;
        padding-bottom: 0.5rem;
    }
    .formula-box {
        background-color: #e3f2fd;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
        border-left: 4px solid #1f77b4;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.markdown('<h1 class="main-header">🏗️ Reinforced Concrete Section Design (ACI)</h1>', unsafe_allow_html=True)

# Sidebar for inputs
st.sidebar.header("📊 Input Parameters")

# Reset button at the top
if st.sidebar.button("🔄 Reset All Values", type="primary", use_container_width=True):
    reset_values()
    st.rerun()

st.sidebar.markdown("---")

# Input method selection
input_method = st.sidebar.radio("Input Method", ["Sliders", "Manual Input"])

st.sidebar.markdown("---")
st.sidebar.subheader("Material Properties")

# Initialize values in session state if not exists
for key, value in default_values.items():
    if key not in st.session_state:
        st.session_state[key] = value

# Material properties inputs
if input_method == "Sliders":
    fy = st.sidebar.slider("Steel Yield Strength, fy (MPa)", 
                          min_value=200.0, max_value=600.0, 
                          value=st.session_state.fy, step=10.0, key='fy')
    
    fcu = st.sidebar.slider("Concrete Strength, f'c (MPa)", 
                           min_value=15.0, max_value=50.0, 
                           value=st.session_state.fcu, step=2.5, key='fcu')
else:
    fy = st.sidebar.number_input("Steel Yield Strength, fy (MPa)", 
                                value=st.session_state.fy, 
                                min_value=200.0, max_value=600.0, key='fy')
    fcu = st.sidebar.number_input("Concrete Strength, f'c (MPa)", 
                                 value=st.session_state.fcu, 
                                 min_value=15.0, max_value=50.0, key='fcu')

st.sidebar.markdown("---")
st.sidebar.subheader("Loading")

if input_method == "Sliders":
    Mu = st.sidebar.slider("Ultimate Moment, Mu (kN.m)", 
                          min_value=0.0, max_value=200.0, 
                          value=st.session_state.Mu, step=0.1, key='Mu')
else:
    Mu = st.sidebar.number_input("Ultimate Moment, Mu (kN.m)", 
                                value=st.session_state.Mu, 
                                min_value=0.0, key='Mu')

st.sidebar.markdown("---")
st.sidebar.subheader("Section Dimensions")

if input_method == "Sliders":
    b = st.sidebar.slider("Width, b (mm)", 
                         min_value=100.0, max_value=2000.0, 
                         value=st.session_state.b, step=50.0, key='b')
    
    h = st.sidebar.slider("Height, h (mm)", 
                         min_value=100.0, max_value=500.0, 
                         value=st.session_state.h, step=10.0, key='h')
else:
    b = st.sidebar.number_input("Width, b (mm)", 
                               value=st.session_state.b, 
                               min_value=100.0, key='b')
    h = st.sidebar.number_input("Height, h (mm)", 
                               value=st.session_state.h, 
                               min_value=100.0, key='h')

cover = st.sidebar.number_input("Cover (mm)", 
                               value=st.session_state.cover, 
                               min_value=15.0, max_value=75.0, key='cover')

st.sidebar.markdown("---")
st.sidebar.subheader("Design Parameters")

phi = st.sidebar.number_input("Strength Reduction Factor, φ", 
                             value=st.session_state.phi, 
                             min_value=0.65, max_value=0.9, step=0.05, key='phi')
jd = st.sidebar.number_input("Moment Arm Factor, jd", 
                            value=st.session_state.jd, 
                            min_value=0.85, max_value=0.95, step=0.01, key='jd')
beta1 = st.sidebar.number_input("β₁ Factor", 
                               value=st.session_state.beta1, 
                               min_value=0.65, max_value=0.85, step=0.05, key='beta1')

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
    st.metric("Cover", f"{cover} mm")
with col3:
    st.metric("fy", f"{fy} MPa")
    st.metric("f'c", f"{fcu} MPa")
with col4:
    st.metric("φ", f"{phi}")
    st.metric("jd", f"{jd}")

# Design Calculations
st.markdown('<h2 class="section-header">🔢 Design Calculations</h2>', unsafe_allow_html=True)

# Create three columns for the table
col_formula, col_sub, col_result = st.columns([2, 2, 1])

with col_formula:
    st.markdown("### Formula")
with col_sub:
    st.markdown("### Substitution")
with col_result:
    st.markdown("### Result")

st.markdown("---")

# Step 1: d
col_formula, col_sub, col_result = st.columns([2, 2, 1])
with col_formula:
    st.markdown("**1. Effective Depth (d)**")
    st.latex(r'd = h - \text{cover}')
with col_sub:
    st.code(f'd = {h} - {cover}')
with col_result:
    st.metric("", f"{d:.1f} mm")

st.markdown("---")

# Step 2: As initial
col_formula, col_sub, col_result = st.columns([2, 2, 1])
with col_formula:
    st.markdown("**2. Initial Steel Area**")
    st.latex(r'A_s = \frac{M_u}{\phi \cdot f_y \cdot jd \cdot d}')
with col_sub:
    st.code(f'As = {Mu*1e6:.2e} / ({phi} × {fy} × {jd} × {d})')
with col_result:
    st.metric("", f"{As_initial:.2f} mm²")

st.markdown("---")

# Step 3: a
col_formula, col_sub, col_result = st.columns([2, 2, 1])
with col_formula:
    st.markdown("**3. Depth of Compression Block (a)**")
    st.latex(r"a = \frac{A_s \cdot f_y}{0.85 \cdot f'_c \cdot b}")
with col_sub:
    st.code(f'a = ({As_initial:.2f} × {fy}) / (0.85 × {fcu} × {b})')
with col_result:
    st.metric("", f"{a_initial:.2f} mm")

st.markdown("---")

# Step 4: As
col_formula, col_sub, col_result = st.columns([2, 2, 1])
with col_formula:
    st.markdown("**4. Accurate Steel Area**")
    st.latex(r'A_s = \frac{M_u}{\phi \cdot f_y \cdot \left(d - \frac{a}{2}\right)}')
with col_sub:
    st.code(f'As = {Mu*1e6:.2e} / ({phi} × {fy} × {d - a_initial/2:.2f})')
with col_result:
    st.metric("", f"{As_calculated:.2f} mm²")

st.markdown("---")

# Step 5: As min
col_formula, col_sub, col_result = st.columns([2, 2, 1])
with col_formula:
    st.markdown("**5. Minimum Steel Area**")
    st.latex(r'A_{s,min} = \frac{1.4 \cdot b \cdot d}{f_y}')
with col_sub:
    st.code(f'As,min = (1.4 × {b} × {d}) / {fy}')
with col_result:
    st.metric("", f"{As_min:.2f} mm²")

st.markdown("---")

# Step 6: Check As
col_formula, col_sub, col_result = st.columns([2, 2, 1])
governing = "As min" if As_required == As_min else "As calculated"
with col_formula:
    st.markdown("**6. Required Steel Area**")
    st.latex(r'A_{s,req} = \max(A_s, A_{s,min})')
with col_sub:
    st.code(f'As,req = max({As_calculated:.2f}, {As_min:.2f})')
with col_result:
    st.metric("", f"{As_required:.2f} mm²")
    st.caption(f"({governing} governs)")

st.markdown("---")

# Step 7: c
col_formula, col_sub, col_result = st.columns([2, 2, 1])
with col_formula:
    st.markdown("**7. Neutral Axis Depth (c)**")
    st.latex(r'c = \frac{a}{\beta_1}')
with col_sub:
    st.code(f'c = {a_final:.2f} / {beta1}')
with col_result:
    st.metric("", f"{c:.2f} mm")

st.markdown("---")

# Step 8: εs
col_formula, col_sub, col_result = st.columns([2, 2, 1])
with col_formula:
    st.markdown("**8. Steel Strain (εs)**")
    st.latex(r'\varepsilon_s = \frac{d - c}{c} \times 0.003')
with col_sub:
    st.code(f'εs = ({d} - {c:.2f}) / {c:.2f} × 0.003')
with col_result:
    st.metric("", f"{es:.5f}")

st.markdown("---")

# Step 9: Check εs
col_formula, col_sub, col_result = st.columns([2, 2, 1])
strain_safe = es >= 0.002
strain_status = "Tension" if es >= 0.005 else ("Transition" if es >= 0.002 else "Compression")
with col_formula:
    st.markdown("**9. Strain Check**")
    st.latex(r'\varepsilon_s \geq 0.002')
with col_sub:
    st.code(f'{es:.5f} ≥ 0.002')
with col_result:
    if strain_safe:
        st.success("✓ OK")
    else:
        st.error("✗ FAIL")
    st.caption(f"{strain_status}")

st.markdown("---")

# Step 10: φMn
col_formula, col_sub, col_result = st.columns([2, 2, 1])
with col_formula:
    st.markdown("**10. Design Moment Capacity**")
    st.latex(r'\phi M_n = \phi \cdot A_s \cdot f_y \cdot \left(d - \frac{a}{2}\right)')
with col_sub:
    st.code(f'φMn = {phi} × {As_required:.2f} × {fy} × {d - a_final/2:.2f}')
with col_result:
    st.metric("", f"{phi_Mn:.2f} kN.m")

st.markdown("---")

# Step 11: Check φMn
col_formula, col_sub, col_result = st.columns([2, 2, 1])
capacity_safe = phi_Mn >= Mu
with col_formula:
    st.markdown("**11. Capacity Check**")
    st.latex(r'\phi M_n \geq M_u')
with col_sub:
    st.code(f'{phi_Mn:.2f} ≥ {Mu}')
with col_result:
    if capacity_safe:
        st.success("✓ SAFE")
    else:
        st.error("✗ UNSAFE")

st.markdown("---")

# Final Summary
st.markdown('<h2 class="section-header">✅ Design Summary</h2>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Required Reinforcement")
    st.metric("As required", f"{As_required:.2f} mm²", 
             delta=f"{As_required - As_min:.2f} mm² over minimum")
    
    # Rebar suggestions
    st.subheader("Rebar Suggestions")
    rebar_data = {
        'Configuration': [],
        'Provided Area': [],
        'Over Design': []
    }
    
    rebar_sizes = [10, 12, 16, 20, 25]
    rebar_areas = [78.5, 113.1, 201.1, 314.2, 490.9]
    
    for size, area in zip(rebar_sizes, rebar_areas):
        num_bars = math.ceil(As_required / area)
        if num_bars <= 12:
            provided_area = num_bars * area
            over_design = ((provided_area - As_required) / As_required) * 100
            rebar_data['Configuration'].append(f'{num_bars}Ø{size} mm')
            rebar_data['Provided Area'].append(f'{provided_area:.1f} mm²')
            rebar_data['Over Design'].append(f'+{over_design:.1f}%')
    
    rebar_df = pd.DataFrame(rebar_data)
    st.dataframe(rebar_df, use_container_width=True, hide_index=True)

with col2:
    st.subheader("Safety Checks")
    
    # Determine overall safety
    overall_safe = strain_safe and capacity_safe
    
    if overall_safe:
        st.success("✅ DESIGN IS SAFE", icon="✅")
    else:
        st.error("❌ DESIGN IS NOT SAFE", icon="❌")
    
    st.markdown("**Check Details:**")
    
    # Strain check
    if strain_safe:
        st.success(f"✓ Strain Check: Pass (εs = {es:.5f})")
    else:
        st.error(f"✗ Strain Check: Fail (εs = {es:.5f})")
    
    # Capacity check
    capacity_ratio = phi_Mn / Mu
    if capacity_safe:
        st.success(f"✓ Capacity Check: Pass (φMn/Mu = {capacity_ratio:.3f})")
    else:
        st.error(f"✗ Capacity Check: Fail (φMn/Mu = {capacity_ratio:.3f})")
    
    # Section type
    st.info(f"Section Type: {strain_status}-controlled")
    
    # Additional metrics
    st.metric("Design Moment Capacity", f"{phi_Mn:.2f} kN.m", 
             delta=f"{phi_Mn - Mu:.2f} kN.m")
    st.metric("Utilization Ratio", f"{(Mu/phi_Mn)*100:.1f}%")

# Footer
st.markdown("---")
st.markdown('<p style="text-align: center; color: #7f8c8d; font-size: 0.9rem;">ACI 318 Code | Developed for Educational Purposes</p>', unsafe_allow_html=True)
