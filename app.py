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

# Initialize session state
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.fy = 420.0
    st.session_state.fcu = 25.0
    st.session_state.Mu = 100.0
    st.session_state.b = 250.0
    st.session_state.h = 500.0
    st.session_state.cover = 40.0
    st.session_state.phi = 0.9
    st.session_state.jd = 0.9
    st.session_state.beta1 = 0.85

# Reset function
def clear_all_inputs():
    st.session_state.fy = 0.0
    st.session_state.fcu = 0.0
    st.session_state.Mu = 0.0
    st.session_state.b = 0.0
    st.session_state.h = 0.0
    st.session_state.cover = 0.0
    st.session_state.phi = 0.0
    st.session_state.jd = 0.0
    st.session_state.beta1 = 0.0

# Title
st.markdown('<h1 class="main-header">🏗️ RC Section Design (ACI & ECP)</h1>', unsafe_allow_html=True)

# Design Code Selection
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    design_code = st.selectbox(
        "🔧 Design Code",
        ["ACI 318", "Egyptian Code (ECP 203)"],
        index=0
    )
with col3:
    if st.button("🗑️ Clear All", type="secondary", use_container_width=True):
        clear_all_inputs()
        st.rerun()

st.markdown("---")

# Input Section
st.markdown('<h2 class="section-header">📋 Input Parameters</h2>', unsafe_allow_html=True)

# Material Properties
st.markdown("### Material Properties")
col1, col2 = st.columns(2)

with col1:
    st.markdown("**Steel Yield Strength, fy (MPa)**")
    col_slider, col_input = st.columns([3, 1])
    with col_slider:
        fy_slider = st.slider("fy_slider", 0.0, 600.0, st.session_state.fy, 10.0, 
                             label_visibility="collapsed", key='fy_slider_key')
    with col_input:
        fy_input = st.number_input("fy_input", value=fy_slider, min_value=0.0, max_value=600.0, 
                                  step=10.0, label_visibility="collapsed", key='fy_input_key')
    st.session_state.fy = fy_input
    fy = fy_input

with col2:
    st.markdown("**Concrete Strength, f'c/fcu (MPa)**")
    col_slider, col_input = st.columns([3, 1])
    with col_slider:
        fcu_slider = st.slider("fcu_slider", 0.0, 50.0, st.session_state.fcu, 2.5,
                              label_visibility="collapsed", key='fcu_slider_key')
    with col_input:
        fcu_input = st.number_input("fcu_input", value=fcu_slider, min_value=0.0, max_value=50.0,
                                   step=2.5, label_visibility="collapsed", key='fcu_input_key')
    st.session_state.fcu = fcu_input
    fcu = fcu_input

# Loading
st.markdown("### Loading")
col1, col2 = st.columns(2)

with col1:
    st.markdown("**Ultimate Moment, Mu (kN.m)**")
    col_slider, col_input = st.columns([3, 1])
    with col_slider:
        Mu_slider = st.slider("Mu_slider", 0.0, 500.0, st.session_state.Mu, 0.5,
                             label_visibility="collapsed", key='Mu_slider_key')
    with col_input:
        Mu_input = st.number_input("Mu_input", value=Mu_slider, min_value=0.0,
                                  step=0.1, label_visibility="collapsed", key='Mu_input_key')
    st.session_state.Mu = Mu_input
    Mu = Mu_input

# Section Dimensions
st.markdown("### Section Dimensions")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**Width, b (mm)**")
    col_slider, col_input = st.columns([3, 1])
    with col_slider:
        b_slider = st.slider("b_slider", 0.0, 2000.0, st.session_state.b, 50.0,
                            label_visibility="collapsed", key='b_slider_key')
    with col_input:
        b_input = st.number_input("b_input", value=b_slider, min_value=0.0,
                                 step=50.0, label_visibility="collapsed", key='b_input_key')
    st.session_state.b = b_input
    b = b_input

with col2:
    st.markdown("**Height, h (mm)**")
    col_slider, col_input = st.columns([3, 1])
    with col_slider:
        h_slider = st.slider("h_slider", 0.0, 1000.0, st.session_state.h, 10.0,
                            label_visibility="collapsed", key='h_slider_key')
    with col_input:
        h_input = st.number_input("h_input", value=h_slider, min_value=0.0,
                                 step=10.0, label_visibility="collapsed", key='h_input_key')
    st.session_state.h = h_input
    h = h_input

with col3:
    st.markdown("**Cover (mm)**")
    col_slider, col_input = st.columns([3, 1])
    with col_slider:
        cover_slider = st.slider("cover_slider", 0.0, 75.0, st.session_state.cover, 5.0,
                                label_visibility="collapsed", key='cover_slider_key')
    with col_input:
        cover_input = st.number_input("cover_input", value=cover_slider, min_value=0.0, max_value=75.0,
                                     step=5.0, label_visibility="collapsed", key='cover_input_key')
    st.session_state.cover = cover_input
    cover = cover_input

# Design Parameters (only for ACI)
if design_code == "ACI 318":
    st.markdown("### Design Parameters")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Reduction Factor, φ**")
        col_slider, col_input = st.columns([3, 1])
        with col_slider:
            phi_slider = st.slider("phi_slider", 0.0, 0.9, st.session_state.phi, 0.05,
                                  label_visibility="collapsed", key='phi_slider_key')
        with col_input:
            phi_input = st.number_input("phi_input", value=phi_slider, min_value=0.0, max_value=0.9,
                                       step=0.05, label_visibility="collapsed", key='phi_input_key')
        st.session_state.phi = phi_input
        phi = phi_input
    
    with col2:
        st.markdown("**Moment Arm Factor, jd**")
        col_slider, col_input = st.columns([3, 1])
        with col_slider:
            jd_slider = st.slider("jd_slider", 0.0, 0.95, st.session_state.jd, 0.01,
                                 label_visibility="collapsed", key='jd_slider_key')
        with col_input:
            jd_input = st.number_input("jd_input", value=jd_slider, min_value=0.0, max_value=0.95,
                                      step=0.01, label_visibility="collapsed", key='jd_input_key')
        st.session_state.jd = jd_input
        jd = jd_input
    
    with col3:
        st.markdown("**β₁ Factor**")
        col_slider, col_input = st.columns([3, 1])
        with col_slider:
            beta1_slider = st.slider("beta1_slider", 0.0, 0.85, st.session_state.beta1, 0.05,
                                    label_visibility="collapsed", key='beta1_slider_key')
        with col_input:
            beta1_input = st.number_input("beta1_input", value=beta1_slider, min_value=0.0, max_value=0.85,
                                         step=0.05, label_visibility="collapsed", key='beta1_input_key')
        st.session_state.beta1 = beta1_input
        beta1 = beta1_input

# Validation
if design_code == "ACI 318":
    all_inputs_valid = all([
        fy > 0, fcu > 0, Mu > 0, b > 0, h > 0, cover >= 0,
        h > cover, phi > 0, jd > 0, beta1 > 0
    ])
else:
    all_inputs_valid = all([
        fy > 0, fcu > 0, Mu > 0, b > 0, h > 0, cover >= 0, h > cover
    ])

if not all_inputs_valid:
    st.warning("⚠️ Please enter all input values to proceed with calculations")
    st.stop()

# Calculations
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
        
    else:  # Egyptian Code (ECP 203)
        # Egyptian Code - الوحدات بالسنتيمتر
        d_cm = d / 10  # تحويل من mm إلى cm
        b_cm = b / 10
        Mu_kgcm = Mu * 1e5  # kN.m to kg.cm
        fcu_kgcm2 = fcu * 10  # MPa to kg/cm²
        fy_kgcm2 = fy * 10
        
        # C1 = d / √(fcu × b) - بالسنتيمتر
        C1 = d_cm / math.sqrt(fcu_kgcm2 * b_cm)
        C1_min = 2.76
        
        # حساب J
        term_inside_sqrt = 0.25 - (Mu_kgcm / (0.9 * fcu_kgcm2 * b_cm * d_cm * d_cm))
        
        if term_inside_sqrt < 0:
            st.error("❌ Error: Section is too small. Increase dimensions or reduce moment.")
            st.stop()
        
        J_calculated = (1/1.15) * (0.5 + math.sqrt(term_inside_sqrt))
        J_max = 0.95
        J = min(J_calculated, J_max)
        
        # As = Mu / (fy × J × d)
        As_calculated_cm2 = Mu_kgcm / (fy_kgcm2 * J * d_cm)
        As_calculated = As_calculated_cm2 * 100  # cm² to mm²
        
        # Minimum steel
        As_min = (0.6 / fy) * b * d
        
        As_required = max(As_calculated, As_min)
        
        # Check strain and capacity
        a_final = (As_required * fy) / (0.67 * fcu * b)
        c = a_final / 0.8
        es = ((d - c) / c) * 0.003
        
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

# Display results
st.markdown("---")
st.markdown(f"**📘 Design Code: {design_code}**")
st.markdown("---")

# Calculations Display
st.markdown('<h2 class="section-header">🔢 Calculations</h2>', unsafe_allow_html=True)

if design_code == "ACI 318":
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
        'substitution': rf'\max({As_min_1:.1f}, {As_min_2:.1f})',
        'result': f'{As_min:.1f} mm²', 'variable': 'As,min'
    })
    
    governing = "minimum" if As_required == As_min else "calculated"
    calculations.append({
        'step': '6', 'description': 'Required As',
        'formula': r'A_{s,req} = \max(A_s, A_{s,min})',
        'substitution': rf'\max({As_calculated:.1f}, {As_min:.1f})',
        'result': f'{As_required:.1f} mm² ({governing})', 'variable': 'As,req'
    })

else:  # Egyptian Code
    calculations = []
    
    calculations.append({
        'step': '1', 'description': 'Effective Depth',
        'formula': r'd = T_s - \text{cover}',
        'substitution': rf'{h:.0f} - {cover:.0f}',
        'result': f'{d:.1f} mm = {d_cm:.2f} cm', 'variable': 'd'
    })
    
    calculations.append({
        'step': '2', 'description': 'C₁ Factor',
        'formula': r'C_1 = \frac{d}{\sqrt{f_{cu} \times B}}',
        'substitution': rf'\frac{{{d_cm:.2f}}}{{\sqrt{{{fcu_kgcm2:.0f} \times {b_cm:.1f}}}}}',
        'result': f'{C1:.3f}', 'variable': 'C₁'
    })
    
    check_c1 = C1 > C1_min
    calculations.append({
        'step': '3', 'description': 'Check C₁',
        'formula': r'C_1 > C_{1,min} = 2.76',
        'substitution': f'{C1:.3f} > 2.76',
        'result': f'{"PASS ✓" if check_c1 else "FAIL ✗"}', 'variable': 'Check'
    })
    
    calculations.append({
        'step': '4', 'description': 'J Factor',
        'formula': r'J = \frac{1}{1.15}\left(0.5 + \sqrt{0.25 - \frac{M_u}{0.9 \times f_{cu} \times B \times d^2}}\right)',
        'substitution': rf'{J_calculated:.4f}',
        'result': f'{J_calculated:.4f}', 'variable': 'J'
    })
    
    calculations.append({
        'step': '5', 'description': 'J Maximum',
        'formula': r'J = \min(J_{calc}, 0.95)',
        'substitution': f'min({J_calculated:.4f}, 0.95)',
        'result': f'{J:.4f}', 'variable': 'J,final'
    })
    
    calculations.append({
        'step': '6', 'description': 'Required As',
        'formula': r'A_s = \frac{M_u}{f_y \times J \times d}',
        'substitution': rf'\frac{{{Mu_kgcm:.2e}}}{{{fy_kgcm2:.0f} \times {J:.4f} \times {d_cm:.2f}}}',
        'result': f'{As_required:.1f} mm²', 'variable': 'As'
    })
    
    calculations.append({
        'step': '7', 'description': 'Minimum As',
        'formula': r'A_{s,min} = \frac{0.6}{f_y} \times b \times d',
        'substitution': rf'\frac{{0.6}}{{{fy:.0f}}} \times {b:.0f} \times {d:.1f}',
        'result': f'{As_min:.1f} mm²', 'variable': 'As,min'
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
    st.metric("As Minimum", f"{As_min:.1f} mm²")
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
        st.error("### ❌ DESIGN NEEDS REVISION")
    
    st.markdown("**Checks:**")
    st.markdown(f"{'✅' if strain_safe else '❌'} εs: {es:.5f} {'≥' if strain_safe else '<'} 0.002")
    st.markdown(f"{'✅' if capacity_safe else '❌'} φMn={phi_Mn:.2f} {'≥' if capacity_safe else '<'} Mu={Mu:.2f}")
    st.markdown(f"{'✅' if As_required >= As_min else '❌'} Minimum Steel")
    
    st.metric("Utilization", f"{utilization:.1f}%")
    st.metric("φMn", f"{phi_Mn:.2f} kN.m")

# Reinforcement Selection
st.markdown("---")
st.markdown('<h2 class="section-header">🔧 Reinforcement Selection</h2>', unsafe_allow_html=True)

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

selected_As = rebar_data[selected_diameter][selected_num_bars - 1]

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
    if design_code == "ACI 318":
        a_selected = (selected_As * fy) / (0.85 * fcu * b)
        c_selected = a_selected / beta1
        phi_Mn_selected = (phi * selected_As * fy * (d - a_selected/2)) / 1e6
    else:
        a_selected = (selected_As * fy) / (0.67 * fcu * b)
        c_selected = a_selected / 0.8
        phi_Mn_selected = (0.9 * selected_As * fy * (d - a_selected/2)) / 1e6
    
    es_selected = ((d - c_selected) / c_selected) * 0.003
    check_capacity = phi_Mn_selected >= Mu
    
    if check_capacity:
        st.success(f"✓ Capacity\nφMn = {phi_Mn_selected:.2f}")
    else:
        st.error(f"✗ Capacity\nφMn = {phi_Mn_selected:.2f}")

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
        st.success("### ✅ CONFIG IS SAFE")
    else:
        st.error("### ❌ CONFIG FAILED")
    
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
