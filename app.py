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
    /* جدول مضغوط */
    .calculation-table {
        width: 100%;
        border-collapse: collapse;
        margin: 10px 0;
        font-size: 0.95rem;
    }
    .calculation-table th {
        background-color: #1f77b4;
        color: white;
        padding: 8px;
        text-align: left;
        border: 1px solid #ddd;
    }
    .calculation-table td {
        padding: 6px 8px;
        border: 1px solid #ddd;
        vertical-align: middle;
    }
    .calculation-table tr:nth-child(even) {
        background-color: #f8f9fa;
    }
    .step-number {
        font-weight: bold;
        color: #1f77b4;
        min-width: 30px;
    }
    .formula-cell {
        min-width: 200px;
    }
    .substitution-cell {
        min-width: 250px;
        font-family: 'Courier New', monospace;
        color: #2c3e50;
    }
    .result-cell {
        min-width: 150px;
        font-weight: bold;
        color: #27ae60;
    }
    .status-pass {
        color: #27ae60;
        font-weight: bold;
    }
    .status-fail {
        color: #e74c3c;
        font-weight: bold;
    }
    /* تقليل المسافات */
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
    </style>
""", unsafe_allow_html=True)

# Initialize session state - بدون قيم افتراضية
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    # لا نضع قيم افتراضية

# Reset function - يحذف كل القيم
def clear_all_inputs():
    keys_to_delete = ['fy', 'fcu', 'Mu', 'b', 'h', 'cover', 'phi', 'jd', 'beta1']
    for key in keys_to_delete:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

# Title
st.markdown('<h1 class="main-header">🏗️ RC Section Design (ACI)</h1>', unsafe_allow_html=True)

# Sidebar
st.sidebar.header("📊 Input Parameters")

# Clear button
if st.sidebar.button("🗑️ Clear All Inputs", type="secondary", use_container_width=True):
    clear_all_inputs()

st.sidebar.markdown("---")

# Input method
input_method = st.sidebar.radio("Input Method", ["Sliders", "Manual Input"])

st.sidebar.markdown("---")
st.sidebar.subheader("Material Properties")

# Material properties
if input_method == "Sliders":
    fy = st.sidebar.slider("Steel Yield Strength, fy (MPa)", 
                          min_value=200.0, max_value=600.0, 
                          value=420.0, step=10.0, key='fy')
    fcu = st.sidebar.slider("Concrete Strength, f'c (MPa)", 
                           min_value=15.0, max_value=50.0, 
                           value=25.0, step=2.5, key='fcu')
else:
    fy = st.sidebar.number_input("Steel Yield Strength, fy (MPa)", 
                                value=None, min_value=0.0, max_value=600.0, 
                                step=10.0, key='fy', placeholder="Enter fy")
    fcu = st.sidebar.number_input("Concrete Strength, f'c (MPa)", 
                                 value=None, min_value=0.0, max_value=50.0, 
                                 step=2.5, key='fcu', placeholder="Enter f'c")

st.sidebar.markdown("---")
st.sidebar.subheader("Loading")

if input_method == "Sliders":
    Mu = st.sidebar.slider("Ultimate Moment, Mu (kN.m)", 
                          min_value=0.0, max_value=200.0, 
                          value=13.7, step=0.1, key='Mu')
else:
    Mu = st.sidebar.number_input("Ultimate Moment, Mu (kN.m)", 
                                value=None, min_value=0.0, 
                                step=0.1, key='Mu', placeholder="Enter Mu")

st.sidebar.markdown("---")
st.sidebar.subheader("Section Dimensions")

if input_method == "Sliders":
    b = st.sidebar.slider("Width, b (mm)", 
                         min_value=100.0, max_value=2000.0, 
                         value=1000.0, step=50.0, key='b')
    h = st.sidebar.slider("Height, h (mm)", 
                         min_value=100.0, max_value=500.0, 
                         value=150.0, step=10.0, key='h')
    cover = st.sidebar.slider("Cover (mm)", 
                             min_value=15.0, max_value=75.0,
                             value=20.0, step=5.0, key='cover')
else:
    b = st.sidebar.number_input("Width, b (mm)", 
                               value=None, min_value=0.0, 
                               step=50.0, key='b', placeholder="Enter b")
    h = st.sidebar.number_input("Height, h (mm)", 
                               value=None, min_value=0.0, 
                               step=10.0, key='h', placeholder="Enter h")
    cover = st.sidebar.number_input("Cover (mm)", 
                                   value=None, min_value=0.0, max_value=75.0, 
                                   step=5.0, key='cover', placeholder="Enter cover")

st.sidebar.markdown("---")
st.sidebar.subheader("Design Parameters")

if input_method == "Sliders":
    phi = st.sidebar.slider("Strength Reduction Factor, φ", 
                           min_value=0.65, max_value=0.9,
                           value=0.9, step=0.05, key='phi')
    jd = st.sidebar.slider("Moment Arm Factor, jd", 
                          min_value=0.85, max_value=0.95,
                          value=0.95, step=0.01, key='jd')
    beta1 = st.sidebar.slider("β₁ Factor", 
                             min_value=0.65, max_value=0.85,
                             value=0.85, step=0.05, key='beta1')
else:
    phi = st.sidebar.number_input("Strength Reduction Factor, φ", 
                                 value=None, min_value=0.0, max_value=0.9, 
                                 step=0.05, key='phi', placeholder="Enter φ")
    jd = st.sidebar.number_input("Moment Arm Factor, jd", 
                                value=None, min_value=0.0, max_value=0.95, 
                                step=0.01, key='jd', placeholder="Enter jd")
    beta1 = st.sidebar.number_input("β₁ Factor", 
                                   value=None, min_value=0.0, max_value=0.85, 
                                   step=0.05, key='beta1', placeholder="Enter β₁")

# Validation
all_inputs_valid = all([
    fy is not None and fy > 0,
    fcu is not None and fcu > 0,
    Mu is not None and Mu > 0,
    b is not None and b > 0,
    h is not None and h > 0,
    cover is not None and cover > 0,
    phi is not None and phi > 0,
    jd is not None and jd > 0,
    beta1 is not None and beta1 > 0
])

if not all_inputs_valid:
    st.warning("⚠️ Please enter all input values to proceed with calculations")
    st.info("💡 Use the sidebar to input all required parameters")
    st.stop()

# Calculations
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

# Calculations Table
st.markdown('<h2 class="section-header">🔢 Calculations</h2>', unsafe_allow_html=True)

# Create calculation steps
calculations = []

# Step 1: d
calculations.append({
    'step': '1',
    'description': 'Effective Depth',
    'formula': r'd = h - \text{cover}',
    'substitution': rf'\frac{{{h} - {cover}}}{{1}}',
    'result': f'{d:.1f} mm',
    'variable': 'd'
})

# Step 2: As initial
calculations.append({
    'step': '2',
    'description': 'Initial As',
    'formula': r'A_s = \frac{M_u}{\phi f_y jd \cdot d}',
    'substitution': rf'\frac{{{Mu*1e6:.1e}}}{{{phi} \times {fy} \times {jd} \times {d:.1f}}}',
    'result': f'{As_initial:.1f} mm²',
    'variable': 'As,init'
})

# Step 3: a initial
calculations.append({
    'step': '3',
    'description': 'Depth of Block',
    'formula': r"a = \frac{A_s f_y}{0.85 f'_c b}",
    'substitution': rf'\frac{{{As_initial:.1f} \times {fy}}}{{0.85 \times {fcu} \times {b}}}',
    'result': f'{a_initial:.2f} mm',
    'variable': 'a'
})

# Step 4: As calculated
calculations.append({
    'step': '4',
    'description': 'Refined As',
    'formula': r'A_s = \frac{M_u}{\phi f_y (d - a/2)}',
    'substitution': rf'\frac{{{Mu*1e6:.1e}}}{{{phi} \times {fy} \times ({d:.1f} - {a_initial/2:.2f})}}',
    'result': f'{As_calculated:.1f} mm²',
    'variable': 'As,calc'
})

# Step 5: As min
calculations.append({
    'step': '5',
    'description': 'Minimum As',
    'formula': r'A_{s,min} = \frac{1.4 bd}{f_y}',
    'substitution': rf'\frac{{1.4 \times {b} \times {d:.1f}}}{{{fy}}}',
    'result': f'{As_min:.1f} mm²',
    'variable': 'As,min'
})

# Step 6: As required
governing = "minimum" if As_required == As_min else "calculated"
calculations.append({
    'step': '6',
    'description': 'Required As',
    'formula': r'A_{s,req} = \max(A_s, A_{s,min})',
    'substitution': rf'\max({As_calculated:.1f}, {As_min:.1f})',
    'result': f'{As_required:.1f} mm² ({governing})',
    'variable': 'As,req'
})

# Step 7: a final
calculations.append({
    'step': '7',
    'description': 'Final a',
    'formula': r"a = \frac{A_{s,req} f_y}{0.85 f'_c b}",
    'substitution': rf'\frac{{{As_required:.1f} \times {fy}}}{{0.85 \times {fcu} \times {b}}}',
    'result': f'{a_final:.2f} mm',
    'variable': 'a,final'
})

# Step 8: c
calculations.append({
    'step': '8',
    'description': 'Neutral Axis',
    'formula': r'c = \frac{a}{\beta_1}',
    'substitution': rf'\frac{{{a_final:.2f}}}{{{beta1}}}',
    'result': f'{c:.2f} mm',
    'variable': 'c'
})

# Step 9: εs
calculations.append({
    'step': '9',
    'description': 'Steel Strain',
    'formula': r'\varepsilon_s = \frac{d-c}{c} \times 0.003',
    'substitution': rf'\frac{{{d:.1f} - {c:.2f}}}{{{c:.2f}}} \times 0.003',
    'result': f'{es:.5f}',
    'variable': 'εs'
})

# Step 10: Check εs
strain_safe = es >= 0.002
if es >= 0.005:
    strain_status = "Tension ✓"
elif es >= 0.002:
    strain_status = "Transition ⚠"
else:
    strain_status = "Compression ✗"

calculations.append({
    'step': '10',
    'description': 'Check εs',
    'formula': r'\varepsilon_s \geq 0.002',
    'substitution': f'{es:.5f} ≥ 0.002',
    'result': f'{"PASS ✓" if strain_safe else "FAIL ✗"} ({strain_status})',
    'variable': 'Check'
})

# Step 11: φMn
calculations.append({
    'step': '11',
    'description': 'Design Capacity',
    'formula': r'\phi M_n = \phi A_{s,req} f_y (d - a/2)',
    'substitution': rf'{phi} \times {As_required:.1f} \times {fy} \times ({d:.1f} - {a_final/2:.2f})',
    'result': f'{phi_Mn:.2f} kN.m',
    'variable': 'φMn'
})

# Step 12: Check capacity
capacity_safe = phi_Mn >= Mu
utilization = (Mu / phi_Mn) * 100 if phi_Mn > 0 else 0

calculations.append({
    'step': '12',
    'description': 'Capacity Check',
    'formula': r'\phi M_n \geq M_u',
    'substitution': f'{phi_Mn:.2f} ≥ {Mu}',
    'result': f'{"SAFE ✓" if capacity_safe else "UNSAFE ✗"} ({utilization:.1f}%)',
    'variable': 'Check'
})

# Display as table using columns
for calc in calculations:
    col1, col2, col3, col4 = st.columns([0.5, 2, 2.5, 1.5])
    
    with col1:
        st.markdown(f"**{calc['step']}**")
    
    with col2:
        st.markdown(f"**{calc['description']}**")
        st.latex(calc['formula'])
    
    with col3:
        # Display substitution as LaTeX
        st.latex(calc['substitution'])
    
    with col4:
        # Check if it's a status result
        if 'PASS' in calc['result'] or 'SAFE' in calc['result']:
            st.success(calc['result'])
        elif 'FAIL' in calc['result'] or 'UNSAFE' in calc['result']:
            st.error(calc['result'])
        else:
            st.info(f"**{calc['result']}**")
    
    st.markdown("---")

# Summary
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
    st.markdown(f"{'✅' if As_required >= As_min else '❌'} Minimum Steel")
    
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
