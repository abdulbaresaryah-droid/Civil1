import streamlit as st
import pandas as pd
import math

# Page configuration
st.set_page_config(
    page_title="RC Section Design - ACI",
    page_icon="🏗️",
    layout="wide"
)

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
    .stMetric {
        background-color: #f8f9fa;
        padding: 10px;
        border-radius: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.markdown('<h1 class="main-header">🏗️ Reinforced Concrete Section Design (ACI)</h1>', unsafe_allow_html=True)

# Sidebar for inputs
st.sidebar.header("📊 Input Parameters")

# Input method selection
input_method = st.sidebar.radio("Input Method", ["Sliders", "Manual Input"])

st.sidebar.markdown("---")
st.sidebar.subheader("Material Properties")

# Material properties inputs
if input_method == "Sliders":
    col1, col2 = st.sidebar.columns([3, 1])
    with col1:
        fy_slider = st.slider("Steel Yield Strength, fy (MPa)", 
                             min_value=200.0, max_value=600.0, value=420.0, step=10.0)
    with col2:
        fy = st.number_input("fy", value=fy_slider, label_visibility="collapsed", key="fy_manual")
    
    col1, col2 = st.sidebar.columns([3, 1])
    with col1:
        fcu_slider = st.slider("Concrete Strength, f'c (MPa)", 
                              min_value=15.0, max_value=50.0, value=25.0, step=2.5)
    with col2:
        fcu = st.number_input("fcu", value=fcu_slider, label_visibility="collapsed", key="fcu_manual")
else:
    fy = st.sidebar.number_input("Steel Yield Strength, fy (MPa)", value=420.0, min_value=200.0, max_value=600.0)
    fcu = st.sidebar.number_input("Concrete Strength, f'c (MPa)", value=25.0, min_value=15.0, max_value=50.0)

st.sidebar.markdown("---")
st.sidebar.subheader("Loading")

if input_method == "Sliders":
    col1, col2 = st.sidebar.columns([3, 1])
    with col1:
        Mu_slider = st.slider("Ultimate Moment, Mu (kN.m)", 
                             min_value=0.0, max_value=200.0, value=13.7, step=0.1)
    with col2:
        Mu = st.number_input("Mu", value=Mu_slider, label_visibility="collapsed", key="Mu_manual")
else:
    Mu = st.sidebar.number_input("Ultimate Moment, Mu (kN.m)", value=13.7, min_value=0.0)

st.sidebar.markdown("---")
st.sidebar.subheader("Section Dimensions")

if input_method == "Sliders":
    col1, col2 = st.sidebar.columns([3, 1])
    with col1:
        b_slider = st.slider("Width, b (mm)", 
                            min_value=100.0, max_value=2000.0, value=1000.0, step=50.0)
    with col2:
        b = st.number_input("b", value=b_slider, label_visibility="collapsed", key="b_manual")
    
    col1, col2 = st.sidebar.columns([3, 1])
    with col1:
        h_slider = st.slider("Height, h (mm)", 
                            min_value=100.0, max_value=500.0, value=150.0, step=10.0)
    with col2:
        h = st.number_input("h", value=h_slider, label_visibility="collapsed", key="h_manual")
else:
    b = st.sidebar.number_input("Width, b (mm)", value=1000.0, min_value=100.0)
    h = st.sidebar.number_input("Height, h (mm)", value=150.0, min_value=100.0)

cover = st.sidebar.number_input("Cover (mm)", value=20.0, min_value=15.0, max_value=75.0)

st.sidebar.markdown("---")
st.sidebar.subheader("Design Parameters")

phi = st.sidebar.number_input("Strength Reduction Factor, φ", value=0.9, min_value=0.65, max_value=0.9, step=0.05)
jd = st.sidebar.number_input("Moment Arm Factor, jd", value=0.95, min_value=0.85, max_value=0.95, step=0.01)
beta1 = st.sidebar.number_input("β₁ Factor", value=0.85, min_value=0.65, max_value=0.85, step=0.05)

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

# Create DataFrame for calculations
calc_data = {
    'Parameter': [],
    'Formula': [],
    'Substitution': [],
    'Result': []
}

# Row 1: d
calc_data['Parameter'].append('d')
calc_data['Formula'].append('d = h - cover')
calc_data['Substitution'].append(f'd = {h} - {cover}')
calc_data['Result'].append(f'{d:.1f} mm')

# Row 2: As initial
calc_data['Parameter'].append('As initial')
calc_data['Formula'].append('As = Mu / (φ × fy × jd × d)')
calc_data['Substitution'].append(f'As = {Mu*1e6:.2e} / ({phi} × {fy} × {jd} × {d})')
calc_data['Result'].append(f'{As_initial:.2f} mm²')

# Row 3: a
calc_data['Parameter'].append('a')
calc_data['Formula'].append("a = (As × fy) / (0.85 × f'c × b)")
calc_data['Substitution'].append(f'a = ({As_initial:.2f} × {fy}) / (0.85 × {fcu} × {b})')
calc_data['Result'].append(f'{a_initial:.2f} mm')

# Row 4: As
calc_data['Parameter'].append('As')
calc_data['Formula'].append('As = Mu / (φ × fy × (d - a/2))')
calc_data['Substitution'].append(f'As = {Mu*1e6:.2e} / ({phi} × {fy} × {d - a_initial/2:.2f})')
calc_data['Result'].append(f'{As_calculated:.2f} mm²')

# Row 5: As min
calc_data['Parameter'].append('As min')
calc_data['Formula'].append('As,min = (1.4 × b × d) / fy')
calc_data['Substitution'].append(f'As,min = (1.4 × {b} × {d}) / {fy}')
calc_data['Result'].append(f'{As_min:.2f} mm²')

# Row 6: Check As
governing = "As min" if As_required == As_min else "As calculated"
calc_data['Parameter'].append('Check As')
calc_data['Formula'].append('As,req = max(As, As,min)')
calc_data['Substitution'].append(f'As,req = max({As_calculated:.2f}, {As_min:.2f})')
calc_data['Result'].append(f'{As_required:.2f} mm² ({governing})')

# Row 7: c
calc_data['Parameter'].append('c')
calc_data['Formula'].append('c = a / β₁')
calc_data['Substitution'].append(f'c = {a_final:.2f} / {beta1}')
calc_data['Result'].append(f'{c:.2f} mm')

# Row 8: εs
calc_data['Parameter'].append('εs')
calc_data['Formula'].append('εs = ((d - c) / c) × 0.003')
calc_data['Substitution'].append(f'εs = ({d} - {c:.2f}) / {c:.2f} × 0.003')
calc_data['Result'].append(f'{es:.5f}')

# Row 9: Check εs
strain_check_result = "✓ OK" if es >= 0.002 else "✗ FAIL"
strain_status = "Tension" if es >= 0.005 else ("Transition" if es >= 0.002 else "Compression")
calc_data['Parameter'].append('Check εs')
calc_data['Formula'].append('εs ≥ 0.002')
calc_data['Substitution'].append(f'{es:.5f} ≥ 0.002')
calc_data['Result'].append(f'{strain_check_result} ({strain_status})')

# Row 10: φMn
calc_data['Parameter'].append('φMn')
calc_data['Formula'].append('φMn = φ × As × fy × (d - a/2)')
calc_data['Substitution'].append(f'φMn = {phi} × {As_required:.2f} × {fy} × {d - a_final/2:.2f}')
calc_data['Result'].append(f'{phi_Mn:.2f} kN.m')

# Row 11: Check φMn
capacity_check_result = "✓ SAFE" if phi_Mn >= Mu else "✗ UNSAFE"
calc_data['Parameter'].append('Check φMn')
calc_data['Formula'].append('φMn ≥ Mu')
calc_data['Substitution'].append(f'{phi_Mn:.2f} ≥ {Mu}')
calc_data['Result'].append(f'{capacity_check_result}')

# Create and style DataFrame
df = pd.DataFrame(calc_data)

# Apply styling
def highlight_result(row):
    if 'SAFE' in str(row['Result']):
        return ['background-color: #d4edda'] * len(row)
    elif 'UNSAFE' in str(row['Result']) or 'FAIL' in str(row['Result']):
        return ['background-color: #f8d7da'] * len(row)
    elif 'OK' in str(row['Result']):
        return ['background-color: #d4edda'] * len(row)
    else:
        return [''] * len(row)

styled_df = df.style.apply(highlight_result, axis=1)\
    .set_properties(**{
        'text-align': 'left',
        'font-size': '14px',
        'border': '1px solid #ddd'
    })\
    .set_table_styles([
        {'selector': 'th', 'props': [('background-color', '#1f77b4'), 
                                      ('color', 'white'), 
                                      ('font-weight', 'bold'),
                                      ('text-align', 'left'),
                                      ('padding', '12px')]},
        {'selector': 'td', 'props': [('padding', '10px')]},
        {'selector': '.col0', 'props': [('font-weight', 'bold')]},
        {'selector': '.col1', 'props': [('background-color', '#e3f2fd'), 
                                         ('font-family', 'monospace')]},
        {'selector': '.col2', 'props': [('background-color', '#fff3e0'), 
                                         ('font-family', 'monospace')]},
        {'selector': '.col3', 'props': [('background-color', '#e8f5e9'), 
                                         ('font-weight', 'bold'),
                                         ('text-align', 'center')]}
    ])

st.dataframe(styled_df, use_container_width=True, height=500)

# Final Summary
st.markdown('<h2 class="section-header">✅ Design Summary</h2>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Required Reinforcement")
    st.metric("As required", f"{As_required:.2f} mm²", delta=f"{As_required - As_min:.2f} mm² over minimum")
    
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
    strain_safe = es >= 0.002
    capacity_safe = phi_Mn >= Mu
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
    st.metric("Design Moment Capacity", f"{phi_Mn:.2f} kN.m", delta=f"{phi_Mn - Mu:.2f} kN.m")
    st.metric("Utilization Ratio", f"{(Mu/phi_Mn)*100:.1f}%")

# Footer
st.markdown("---")
st.markdown('<p style="text-align: center; color: #7f8c8d; font-size: 0.9rem;">ACI 318 Code | Developed for Educational Purposes</p>', unsafe_allow_html=True)
