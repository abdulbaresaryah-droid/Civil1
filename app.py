import streamlit as st
import pandas as pd
import math

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="RC Section Design - ACI & ECP",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ═══════════════════════════════════════════════════════════════════════════════
# CUSTOM CSS STYLING
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
    <style>
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 1400px;
    }
    
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 0.5rem;
        margin-top: -1rem;
    }
    
    .section-header {
        font-size: 1.4rem;
        color: #2c3e50;
        margin-top: 1.5rem;
        margin-bottom: 0.8rem;
        border-bottom: 3px solid #1f77b4;
        padding-bottom: 0.4rem;
        font-weight: 600;
    }
    
    .subsection-header {
        font-size: 1.1rem;
        color: #34495e;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
        font-weight: 500;
    }
    
    div[data-testid="stMetricValue"] {
        font-size: 1.2rem;
        font-weight: 600;
    }
    
    .safe-card {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        border-radius: 10px;
        padding: 20px;
        color: white;
        text-align: center;
        font-size: 1.3rem;
        font-weight: bold;
    }
    
    .unsafe-card {
        background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
        border-radius: 10px;
        padding: 20px;
        color: white;
        text-align: center;
        font-size: 1.3rem;
        font-weight: bold;
    }
    
    .suggestion-card {
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        margin: 5px 0;
        border: 2px solid;
    }
    </style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# REBAR DATA TABLE (mm²)
# ═══════════════════════════════════════════════════════════════════════════════
REBAR_DATA = {
    6:  [28.3, 57, 85, 113, 142, 170, 198, 226, 255],
    8:  [50.3, 101, 151, 201, 252, 302, 352, 402, 453],
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

# ═══════════════════════════════════════════════════════════════════════════════
# SESSION STATE INITIALIZATION
# ═══════════════════════════════════════════════════════════════════════════════
DEFAULT_VALUES = {
    'fy': 420.0,
    'fcu': 30.0,
    'Mu': 150.0,
    'b': 300.0,
    'h': 600.0,
    'cover': 50.0,
    'phi': 0.9,
    'jd': 0.9,
    'beta1': 0.85,
    'gamma_c': 1.5,
    'gamma_s': 1.15,
    'selected_diameter': 16,
    'selected_num_bars': 4
}

def initialize_session_state():
    for key, value in DEFAULT_VALUES.items():
        if key not in st.session_state:
            st.session_state[key] = value

def reset_all_values():
    for key, value in DEFAULT_VALUES.items():
        st.session_state[key] = value

def clear_all_values():
    for key in DEFAULT_VALUES.keys():
        if key in ['phi', 'jd', 'beta1', 'gamma_c', 'gamma_s']:
            continue
        st.session_state[key] = 0.0

initialize_session_state()

# ═══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def create_input_row(label, key, min_val, max_val, step, unit=""):
    """Create a row with label, slider, and number input side by side"""
    st.markdown(f"**{label}** {'(' + unit + ')' if unit else ''}")
    
    col_slider, col_input = st.columns([3, 1])
    
    with col_slider:
        slider_val = st.slider(
            label=f"{key}_slider",
            min_value=float(min_val),
            max_value=float(max_val),
            value=float(st.session_state[key]),
            step=float(step),
            label_visibility="collapsed",
            key=f"{key}_slider_widget"
        )
    
    with col_input:
        input_val = st.number_input(
            label=f"{key}_input",
            min_value=float(min_val),
            max_value=float(max_val * 2),
            value=float(slider_val),
            step=float(step),
            label_visibility="collapsed",
            key=f"{key}_input_widget",
            format="%.2f"
        )
    
    st.session_state[key] = input_val
    return input_val


def calculate_beta1(fc_prime):
    """Calculate β₁ factor based on concrete strength (ACI 318)"""
    if fc_prime <= 28:
        return 0.85
    elif fc_prime >= 55:
        return 0.65
    else:
        return 0.85 - 0.05 * (fc_prime - 28) / 7


def get_strain_status(epsilon_s):
    """Determine section behavior based on steel strain"""
    if epsilon_s >= 0.005:
        return "Tension Controlled ✓", "success"
    elif epsilon_s >= 0.002:
        return "Transition Zone ⚠", "warning"
    else:
        return "Compression Controlled ✗", "error"


def draw_section_svg(b, h, cover, num_bars, bar_diameter, As_provided, As_required):
    """Draw the cross-section using SVG"""
    
    # Scale for display
    scale = 0.5
    svg_width = int(b * scale) +
    svg_height = int(h * scale) + 100
    
    # Offset for margins
    offset_x = 50
    offset_y = 30
    
    # Scaled dimensions
    b_s = b * scale
    h_s = h * scale
    cover_s = cover * scale
    bar_d_s = bar_diameter * scale * 1.5  # Slightly larger for visibility
    
    # Calculate bar positions
    d = h - cover
    effective_width = b - 2 * cover
    
    bars_svg = ""
    if num_bars > 0:
        if num_bars == 1:
            positions = [b / 2]
        else:
            spacing = effective_width / (num_bars - 1)
            positions = [cover + i * spacing for i in range(num_bars)]
        
        for x_pos in positions:
            cx = offset_x + x_pos * scale
            cy = offset_y + h_s - cover_s
            bars_svg += f'<circle cx="{cx}" cy="{cy}" r="{bar_d_s/2}" fill="#c0392b" stroke="#922b21" stroke-width="2"/>'
    
    # Status color
    status_color = "#27ae60" if As_provided >= As_required else "#e74c3c"
    status_text = "✓ OK" if As_provided >= As_required else "✗ INSUFFICIENT"
    
    svg = f'''
    <svg width="{svg_width}" height="{svg_height}" xmlns="http://www.w3.org/2000/svg">
        <!-- Background -->
        <rect x="0" y="0" width="{svg_width}" height="{svg_height}" fill="#f8f9fa"/>
        <!-- Concrete Section -->
        <rect x="{offset_x}" y="{offset_y}" width="{b_s}" height="{h_s}" 
              fill="#bdc3c7" stroke="#7f8c8d" stroke-width="3"/>
        <!-- Cover Zone (inner) -->
        <rect x="{offset_x + cover_s}" y="{offset_y + cover_s}" 
              width="{b_s - 2*cover_s}" height="{h_s - 2*cover_s}" 
              fill="none" stroke="#3498db" stroke-width="1" stroke-dasharray="5,5"/>
        <!-- Rebars -->
        {bars_svg}
        <!-- Dimension Lines -->
        <!-- Width -->
        <line x1="{offset_x}" y1="{offset_y + h_s + 20}" x2="{offset_x + b_s}" y2="{offset_y + h_s + 20}" 
              stroke="#2c3e50" stroke-width="2"/>
        <line x1="{offset_x}" y1="{offset_y + h_s + 15}" x2="{offset_x}" y2="{offset_y + h_s + 25}" 
              stroke="#2c3e50" stroke-width="2"/>
        <line x1="{offset_x + b_s}" y1="{offset_y + h_s + 15}" x2="{offset_x + b_s}" y2="{offset_y + h_s + 25}" 
              stroke="#2c3e50" stroke-width="2"/>
        <text x="{offset_x + b_s/2}" y="{offset_y + h_s + 40}" 
              text-anchor="middle" font-size="14" font-weight="bold" fill="#2c3e50">b = {b:.0f} mm</text>
        <!-- Height -->
        <line x1="{offset_x + b_s + 20}" y1="{offset_y}" x2="{offset_x + b_s + 20}" y2="{offset_y + h_s}" 
              stroke="#2c3e50" stroke-width="2"/>
        <line x1="{offset_x + b_s + 15}" y1="{offset_y}" x2="{offset_x + b_s + 25}" y2="{offset_y}" 
              stroke="#2c3e50" stroke-width="2"/>
        <line x1="{offset_x + b_s + 15}" y1="{offset_y + h_s}" x2="{offset_x + b_s + 25}" y2="{offset_y + h_s}" 
              stroke="#2c3e50" stroke-width="2"/>
        <text x="{offset_x + b_s + 40}" y="{offset_y + h_s/2}" 
              text-anchor="middle" font-size="14" font-weight="bold" fill="#2c3e50" 
              transform="rotate(90 {offset_x + b_s + 40} {offset_y + h_s/2})">h = {h:.0f} mm</text>
        <!-- Effective Depth -->
        <line x1="{offset_x + b_s + 60}" y1="{offset_y}" x2="{offset_x + b_s + 60}" y2="{offset_y + h_s - cover_s}" 
              stroke="#3498db" stroke-width="2"/>
        <text x="{offset_x + b_s + 80}" y="{offset_y + (h_s - cover_s)/2}" 
              text-anchor="middle" font-size="12" fill="#3498db" 
              transform="rotate(90 {offset_x + b_s + 80} {offset_y + (h_s - cover_s)/2})">d = {d:.0f} mm</text>
        <!-- Reinforcement Label -->
        <text x="{offset_x + b_s/2}" y="{offset_y + h_s - cover_s - 20}" 
              text-anchor="middle" font-size="14" font-weight="bold" fill="#c0392b">{num_bars}Ø{bar_diameter}</text>
        <!-- Status Box -->
        <rect x="{offset_x}" y="{offset_y - 25}" width="{b_s}" height="20" 
              fill="{status_color}" rx="5"/>
        <text x="{offset_x + b_s/2}" y="{offset_y - 11}" 
              text-anchor="middle" font-size="12" font-weight="bold" fill="white">
              As = {As_provided:.0f} mm² {status_text}
        </text>
    </svg>
    '''
    
    return svg


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN APPLICATION
# ═══════════════════════════════════════════════════════════════════════════════

# Title
st.markdown('<h1 class="main-header">🏗️ RC Section Design Calculator</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #666; margin-top: -10px;">ACI 318 & Egyptian Code (ECP 203)</p>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# CONTROL BUTTONS & CODE SELECTION
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("---")

col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

with col1:
    design_code = st.selectbox(
        "🔧 Select Design Code",
        ["ACI 318-19", "Egyptian Code (ECP 203)"],
        index=0
    )

with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 Reset", type="secondary", use_container_width=True):
        reset_all_values()
        st.rerun()

with col3:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🗑️ Clear", type="secondary", use_container_width=True):
        clear_all_values()
        st.rerun()

with col4:
    st.markdown("<br>", unsafe_allow_html=True)
    show_details = st.checkbox("📋 Details", value=True)

# Code info
if design_code == "ACI 318-19":
    st.info("📘 **ACI 318-19**: American Concrete Institute Building Code")
else:
    st.info("📗 **ECP 203**: Egyptian Code for Concrete Structures")

# ═══════════════════════════════════════════════════════════════════════════════
# INPUT SECTION
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown('<h2 class="section-header">📋 Input Parameters</h2>', unsafe_allow_html=True)

# Material Properties
st.markdown('<h3 class="subsection-header">🔩 Material Properties</h3>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    fy = create_input_row("Steel Yield Strength, fy", "fy", 0.0, 600.0, 10.0, "MPa")

with col2:
    fcu_label = "Concrete Strength, f'c" if design_code == "ACI 318-19" else "Concrete Cube Strength, fcu"
    fcu = create_input_row(fcu_label, "fcu", 0.0, 60.0, 2.5, "MPa")

# Loading
st.markdown('<h3 class="subsection-header">⚡ Loading</h3>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    Mu = create_input_row("Ultimate Moment, Mu", "Mu", 0.0, 1000.0, 5.0, "kN.m")

# Section Dimensions
st.markdown('<h3 class="subsection-header">📐 Section Dimensions</h3>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    b = create_input_row("Width, b", "b", 0.0, 1500.0, 25.0, "mm")

with col2:
    h = create_input_row("Total Height, h", "h", 0.0, 1500.0, 25.0, "mm")

with col3:
    cover = create_input_row("Concrete Cover", "cover", 0.0, 100.0, 5.0, "mm")

# Design Parameters
st.markdown('<h3 class="subsection-header">⚙️ Design Parameters</h3>', unsafe_allow_html=True)

if design_code == "ACI 318-19":
    col1, col2, col3 = st.columns(3)
    
    with col1:
        phi = create_input_row("Reduction Factor, φ", "phi", 0.65, 0.90, 0.05, "")
    
    with col2:
        jd = create_input_row("Moment Arm Factor, j", "jd", 0.80, 0.95, 0.01, "")
    
    with col3:
        beta1_auto = calculate_beta1(fcu)
        st.markdown(f"**β₁ Factor** (auto)")
        st.info(f"β₁ = {beta1_auto:.3f}")
        beta1 = beta1_auto
        st.session_state.beta1 = beta1

else:
    col1, col2 = st.columns(2)
    
    with col1:
        gamma_c = create_input_row("Concrete Safety Factor, γc", "gamma_c", 1.3, 1.8, 0.05, "")
    
    with col2:
        gamma_s = create_input_row("Steel Safety Factor, γs", "gamma_s", 1.0, 1.3, 0.05, "")

# ═══════════════════════════════════════════════════════════════════════════════
# INPUT VALIDATION
# ═══════════════════════════════════════════════════════════════════════════════

errors = []

if fy <= 0:
    errors.append("Steel yield strength (fy) must be > 0")
if fcu <= 0:
    errors.append("Concrete strength (fcu) must be > 0")
if Mu <= 0:
    errors.append("Ultimate moment (Mu) must be > 0")
if b <= 0:
    errors.append("Section width (b) must be > 0")
if h <= 0:
    errors.append("Section height (h) must be > 0")
if h <= cover:
    errors.append("Section height must be > cover")

d = h - cover

if d <= 0:
    errors.append("Effective depth (d = h - cover) must be > 0")

if errors:
    for error in errors:
        st.error(f"❌ {error}")
    st.stop()

# ═══════════════════════════════════════════════════════════════════════════════
# CALCULATIONS
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown("---")
st.markdown('<h2 class="section-header">🔢 Design Calculations</h2>', unsafe_allow_html=True)

calc_steps = []

try:
    Mu_Nmm = Mu * 1e6
    
    # ═══════════════════════════════════════════════════════════════════════════
    # ACI 318-19 CALCULATIONS
    # ═══════════════════════════════════════════════════════════════════════════
    if design_code == "ACI 318-19":
        
        # Step 1: Effective Depth
        calc_steps.append({
            'step': 1, 'description': 'Effective Depth',
            'formula': r'd = h - \text{cover}',
            'substitution': f'{h:.0f} - {cover:.0f}',
            'result': f'{d:.1f} mm'
        })
        
        # Step 2: Initial Steel Area
        As_initial = Mu_Nmm / (phi * fy * jd * d)
        calc_steps.append({
            'step': 2, 'description': 'Initial Steel Area Estimate',
            'formula': r'A_{s,init} = \frac{M_u}{\phi \cdot f_y \cdot j \cdot d}',
            'substitution': f'\\frac{{{Mu*1e6:.2e}}}{{{phi:.2f} \\times {fy:.0f} \\times {jd:.2f} \\times {d:.1f}}}',
            'result': f'{As_initial:.1f} mm²'
        })
        
        # Step 3: Compression Block Depth
        a_initial = (As_initial * fy) / (0.85 * fcu * b)
        calc_steps.append({
            'step': 3, 'description': 'Compression Block Depth',
            'formula': r"a = \frac{A_s \cdot f_y}{0.85 \cdot f'_c \cdot b}",
            'substitution': f'\\frac{{{As_initial:.1f} \\times {fy:.0f}}}{{0.85 \\times {fcu:.1f} \\times {b:.0f}}}',
            'result': f'{a_initial:.2f} mm'
        })
        
        # Step 4: Refined Steel Area
        As_calculated = Mu_Nmm / (phi * fy * (d - a_initial/2))
        calc_steps.append({
            'step': 4, 'description': 'Refined Steel Area',
            'formula': r'A_s = \frac{M_u}{\phi \cdot f_y \cdot (d - a/2)}',
            'substitution': f'\\frac{{{Mu*1e6:.2e}}}{{{phi:.2f} \\times {fy:.0f} \\times ({d:.1f} - {a_initial/2:.2f})}}',
            'result': f'{As_calculated:.1f} mm²'
        })
        
        # Step 5: Minimum Steel
        As_min_1 = (0.25 * math.sqrt(fcu) / fy) * b * d
        As_min_2 = (1.4 / fy) * b * d
        As_min = max(As_min_1, As_min_2)
        calc_steps.append({
            'step': 5, 'description': 'Minimum Steel Area',
            'formula': r"A_{s,min} = \max\left(\frac{0.25\sqrt{f'_c}}{f_y} bd, \frac{1.4}{f_y} bd\right)",
            'substitution': f'\\max({As_min_1:.1f}, {As_min_2:.1f})',
            'result': f'{As_min:.1f} mm²'
        })
        
        # Step 6: Required Steel
        As_required = max(As_calculated, As_min)
        governing = "As,min" if As_required == As_min else "As,calc"
        calc_steps.append({
            'step': 6, 'description': 'Required Steel Area',
            'formula': r'A_{s,req} = \max(A_{s,calc}, A_{s,min})',
            'substitution': f'\\max({As_calculated:.1f}, {As_min:.1f})',
            'result': f'{As_required:.1f} mm² ({governing} governs)'
        })
        
        # Step 7: Final a
        a_final = (As_required * fy) / (0.85 * fcu * b)
        calc_steps.append({
            'step': 7, 'description': 'Final Compression Block',
            'formula': r"a = \frac{A_{s,req} \cdot f_y}{0.85 \cdot f'_c \cdot b}",
            'substitution': f'\\frac{{{As_required:.1f} \\times {fy:.0f}}}{{0.85 \\times {fcu:.1f} \\times {b:.0f}}}',
            'result': f'{a_final:.2f} mm'
        })
        
        # Step 8: Neutral Axis
        c = a_final / beta1
        calc_steps.append({
            'step': 8, 'description': 'Neutral Axis Depth',
            'formula': r'c = \frac{a}{\beta_1}',
            'substitution': f'\\frac{{{a_final:.2f}}}{{{beta1:.3f}}}',
            'result': f'{c:.2f} mm'
        })
        
        # Step 9: Steel Strain
        epsilon_cu = 0.003
        epsilon_s = ((d - c) / c) * epsilon_cu
        calc_steps.append({
            'step': 9, 'description': 'Steel Strain',
            'formula': r'\varepsilon_s = \frac{d - c}{c} \times 0.003',
            'substitution': f'\\frac{{{d:.1f} - {c:.2f}}}{{{c:.2f}}} \\times 0.003',
            'result': f'{epsilon_s:.5f}'
        })
        
        # Step 10: Capacity
        phi_Mn_Nmm = phi * As_required * fy * (d - a_final/2)
        phi_Mn = phi_Mn_Nmm / 1e6
        calc_steps.append({
            'step': 10, 'description': 'Design Moment Capacity',
            'formula': r'\phi M_n = \phi \cdot A_s \cdot f_y \cdot (d - a/2)',
            'substitution': f'{phi:.2f} \\times {As_required:.1f} \\times {fy:.0f} \\times ({d:.1f} - {a_final/2:.2f})',
            'result': f'{phi_Mn:.2f} kN.m'
        })
        
        rho = As_required / (b * d)
        
    # ═══════════════════════════════════════════════════════════════════════════
    # EGYPTIAN CODE (ECP 203) CALCULATIONS
    # ═══════════════════════════════════════════════════════════════════════════
    else:
        # Convert to ECP units
        d_cm = d / 10
        b_cm = b / 10
        Mu_kgcm = Mu * 1e5
        fcu_kgcm2 = fcu * 10.197
        fy_kgcm2 = fy * 10.197
        
        # Step 1: Effective Depth
        calc_steps.append({
            'step': 1, 'description': 'Effective Depth',
            'formula': r'd = h - \text{cover}',
            'substitution': f'{h:.0f} - {cover:.0f}',
            'result': f'{d:.1f} mm = {d_cm:.2f} cm'
        })
        
        # Step 2: C₁ Factor
        C1 = d_cm * math.sqrt(fcu_kgcm2 * b_cm / Mu_kgcm)
        C1_min = 2.76
        calc_steps.append({
            'step': 2, 'description': 'C₁ Factor',
            'formula': r'C_1 = d \times \sqrt{\frac{f_{cu} \times b}{M_u}}',
            'substitution': f'{d_cm:.2f} \\times \\sqrt{{\\frac{{{fcu_kgcm2:.1f} \\times {b_cm:.1f}}}{{{Mu_kgcm:.0f}}}}}',
            'result': f'{C1:.3f}'
        })
        
        # Step 3: Check C₁
        c1_pass = C1 >= C1_min
        calc_steps.append({
            'step': 3, 'description': 'C₁ Check',
            'formula': r'C_1 \geq C_{1,min} = 2.76',
            'substitution': f'{C1:.3f} \\geq 2.76',
            'result': f'{"✓ PASS" if c1_pass else "✗ FAIL"}'
        })
        
        if not c1_pass:
            st.error("❌ Section needs compression steel (C₁ < 2.76)")
            st.stop()
        
        # Step 4: J Factor
        term = 0.25 - (Mu_kgcm / (0.9 * fcu_kgcm2 * b_cm * d_cm * d_cm))
        
        if term < 0:
            st.error("❌ Section too small!")
            st.stop()
        
        J_calc = (1/1.15) * (0.5 + math.sqrt(term))
        J = min(J_calc, 0.826)
        calc_steps.append({
            'step': 4, 'description': 'J Factor',
            'formula': r'J = \frac{1}{1.15} \times \left(0.5 + \sqrt{0.25 - \frac{M_u}{0.9 f_{cu} b d^2}}\right)',
            'substitution': f'J_{{calc}} = {J_calc:.4f}',
            'result': f'{J:.4f}'
        })
        
        # Step 5: Steel Area
        As_calc_cm2 = Mu_kgcm / (fy_kgcm2 * J * d_cm)
        As_calculated = As_calc_cm2 * 100
        calc_steps.append({
            'step': 5, 'description': 'Calculated Steel Area',
            'formula': r'A_s = \frac{M_u}{f_y \times J \times d}',
            'substitution': f'\\frac{{{Mu_kgcm:.0f}}}{{{fy_kgcm2:.1f} \\times {J:.4f} \\times {d_cm:.2f}}}',
            'result': f'{As_calculated:.1f} mm²'
        })
        
        # Step 6: Minimum Steel
        As_min = max(0.6/fy * b * d, 0.0015 * b * d)
        calc_steps.append({
            'step': 6, 'description': 'Minimum Steel Area',
            'formula': r'A_{s,min} = \max\left(\frac{0.6}{f_y} bd, 0.0015 bd\right)',
            'substitution': f'{0.6/fy * b * d:.1f}, {0.0015 * b * d:.1f}',
            'result': f'{As_min:.1f} mm²'
        })
        
        # Step 7: Required Steel
        As_required = max(As_calculated, As_min)
        governing = "As,min" if As_required == As_min else "As,calc"
        calc_steps.append({
            'step': 7, 'description': 'Required Steel Area',
            'formula': r'A_{s,req} = \max(A_{s,calc}, A_{s,min})',
            'substitution': f'\\max({As_calculated:.1f}, {As_min:.1f})',
            'result': f'{As_required:.1f} mm² ({governing} governs)'
        })
        
        # Step 8: Compression block
        a_final = (As_required * fy) / (0.67 * fcu * b / gamma_c)
        c = a_final / 0.8
        calc_steps.append({
            'step': 8, 'description': 'Compression Block',
            'formula': r'a = \frac{A_s f_y}{0.67 f_{cu} b / \gamma_c}',
            'substitution': f'\\frac{{{As_required:.1f} \\times {fy:.0f}}}{{0.67 \\times {fcu:.1f} \\times {b:.0f} / {gamma_c:.2f}}}',
            'result': f'{a_final:.2f} mm'
        })
        
        # Step 9: Strain
        epsilon_cu = 0.003
        epsilon_s = ((d - c) / c) * epsilon_cu if c > 0 else 0.01
        calc_steps.append({
            'step': 9, 'description': 'Steel Strain',
            'formula': r'\varepsilon_s = \frac{d - c}{c} \times 0.003',
            'substitution': f'\\frac{{{d:.1f} - {c:.2f}}}{{{c:.2f}}} \\times 0.003',
            'result': f'{epsilon_s:.5f}'
        })
        
        # Step 10: Capacity
        phi_Mn_Nmm = (1/gamma_s) * As_required * fy * (d - a_final/2)
        phi_Mn = phi_Mn_Nmm / 1e6
        phi = 1/gamma_s
        calc_steps.append({
            'step': 10, 'description': 'Design Capacity',
            'formula': r'M_d = \frac{A_s f_y}{\gamma_s} (d - a/2)',
            'substitution': f'\\frac{{{As_required:.1f} \\times {fy:.0f}}}{{{gamma_s:.2f}}} \\times ({d:.1f} - {a_final/2:.2f})',
            'result': f'{phi_Mn:.2f} kN.m'
        })
        
        beta1 = 0.8
        rho = As_required / (b * d)
    
    # Safety checks
    strain_status, strain_type = get_strain_status(epsilon_s)
    strain_safe = epsilon_s >= 0.002
    capacity_safe = phi_Mn >= Mu
    overall_safe = strain_safe and capacity_safe and (As_required >= As_min)
    utilization = (Mu / phi_Mn) * 100 if phi_Mn > 0 else 0

except Exception as e:
    st.error(f"❌ Error: {str(e)}")
    st.stop()

# ═══════════════════════════════════════════════════════════════════════════════
# DISPLAY CALCULATION STEPS
# ═══════════════════════════════════════════════════════════════════════════════

if show_details:
    st.markdown(f"**📘 Design Code: {design_code}**")
    
    for calc in calc_steps:
        col1, col2, col3, col4 = st.columns([0.5, 2.5, 2.5, 1.5])
        
        with col1:
            st.markdown(f"**{calc['step']}**")
        
        with col2:
            st.markdown(f"**{calc['description']}**")
            st.latex(calc['formula'])
        
        with col3:
            st.latex(calc['substitution'])
        
        with col4:
            result = calc['result']
            if '✓' in result or 'PASS' in result:
                st.success(f"**{result}**")
            elif '✗' in result or 'FAIL' in result:
                st.error(f"**{result}**")
            else:
                st.info(f"**{result}**")
    
    st.markdown("---")

# ═══════════════════════════════════════════════════════════════════════════════
# DESIGN SUMMARY
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown('<h2 class="section-header">✅ Design Summary</h2>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 📏 Steel Requirements")
    st.metric("As Required", f"{As_required:.1f} mm²")
    st.metric("As Minimum", f"{As_min:.1f} mm²")
    st.metric("Effective Depth (d)", f"{d:.1f} mm")
    st.metric("Steel Ratio (ρ)", f"{rho*100:.3f} %")

with col2:
    st.markdown("### 🔍 Section Analysis")
    st.metric("Compression Block (a)", f"{a_final:.2f} mm")
    st.metric("Neutral Axis (c)", f"{c:.2f} mm")
    st.metric("c/d Ratio", f"{(c/d):.4f}")
    st.metric("Steel Strain (εs)", f"{epsilon_s:.5f}")
    
    if strain_type == "success":
        st.success(f"🟢 {strain_status}")
    elif strain_type == "warning":
        st.warning(f"🟡 {strain_status}")
    else:
        st.error(f"🔴 {strain_status}")

with col3:
    st.markdown("### ✅ Safety Status")
    
    if overall_safe:
        st.markdown('<div class="safe-card">✅ DESIGN IS SAFE</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="unsafe-card">❌ NEEDS REVISION</div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"{'✅' if epsilon_s >= 0.002 else '❌'} Strain: εs = {epsilon_s:.5f}")
    st.markdown(f"{'✅' if capacity_safe else '❌'} Capacity: φMn = {phi_Mn:.2f} ≥ Mu = {Mu:.2f}")
    st.markdown(f"{'✅' if As_required >= As_min else '❌'} Minimum Steel")
    
    st.metric("Utilization", f"{utilization:.1f} %")
    st.metric("Capacity (φMn)", f"{phi_Mn:.2f} kN.m")

# ═══════════════════════════════════════════════════════════════════════════════
# REINFORCEMENT SELECTION
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown("---")
st.markdown('<h2 class="section-header">🔧 Reinforcement Selection</h2>', unsafe_allow_html=True)

# Suggestions
st.markdown("### 💡 Recommended Configurations")

suggestions = []
for diameter in [10, 12, 14, 16, 18, 20, 22, 25, 28, 32]:
    area_per_bar = REBAR_DATA[diameter][0]
    num_bars = math.ceil(As_required / area_per_bar)
    
    if 2 <= num_bars <= 8:
        total_area = REBAR_DATA[diameter][num_bars - 1]
        excess = ((total_area - As_required) / As_required) * 100
        
        clear_width = b - 2 * cover
        min_spacing = max(25, diameter)
        max_bars = int((clear_width + min_spacing) / (diameter + min_spacing))
        
        if num_bars <= max_bars:
            suggestions.append({
                'config': f"{num_bars}Ø{diameter}",
                'num': num_bars,
                'diameter': diameter,
                'area': total_area,
                'excess': excess
            })

if suggestions:
    suggestions = sorted(suggestions, key=lambda x: x['excess'])[:6]
    
    cols = st.columns(3)
    for i, sugg in enumerate(suggestions):
        with cols[i % 3]:
            color = "#27ae60" if sugg['excess'] < 20 else "#f39c12" if sugg['excess'] < 40 else "#e74c3c"
            st.markdown(f"""
                <div style="background: {color}22; border: 2px solid {color}; border-radius: 10px; 
                            padding: 15px; text-align: center; margin: 5px 0;">
                    <h3 style="margin: 0; color: {color};">{sugg['config']}</h3>
                    <p style="margin: 5px 0;">As = {sugg['area']:.0f} mm²</p>
                    <p style="margin: 0; font-size: 0.9em; color: #666;">+{sugg['excess']:.1f}% excess</p>
                </div>
            """, unsafe_allow_html=True)

# Manual Selection
st.markdown("---")
st.markdown("### 🎯 Manual Selection")

col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

with col1:
    selected_diameter = st.selectbox(
        "Bar Diameter (mm)",
        options=list(REBAR_DATA.keys()),
        index=list(REBAR_DATA.keys()).index(st.session_state.selected_diameter)
    )
    st.session_state.selected_diameter = selected_diameter

with col2:
    selected_num_bars = st.selectbox(
        "Number of Bars",
        options=list(range(1, 10)),
        index=st.session_state.selected_num_bars - 1
    )
    st.session_state.selected_num_bars = selected_num_bars

As_provided = REBAR_DATA[selected_diameter][selected_num_bars - 1]
excess_pct = ((As_provided - As_required) / As_required) * 100

with col3:
    st.metric("Provided Area", f"{As_provided:.0f} mm²")

with col4:
    if As_provided >= As_required:
        st.success(f"✓ +{excess_pct:.1f}% excess")
    else:
        st.error(f"✗ {excess_pct:.1f}% deficit")

# Verification
st.markdown("---")
st.markdown("### ✅ Verification")

if design_code == "ACI 318-19":
    a_sel = (As_provided * fy) / (0.85 * fcu * b)
    c_sel = a_sel / beta1
    phi_Mn_sel = (phi * As_provided * fy * (d - a_sel/2)) / 1e6
else:
    a_sel = (As_provided * fy) / (0.67 * fcu * b / gamma_c)
    c_sel = a_sel / 0.8
    phi_Mn_sel = ((1/gamma_s) * As_provided * fy * (d - a_sel/2)) / 1e6

eps_sel = ((d - c_sel) / c_sel) * 0.003 if c_sel > 0 else 0.01
util_sel = (Mu / phi_Mn_sel) * 100 if phi_Mn_sel > 0 else 0

# Spacing check
clear_width = b - 2 * cover
total_bar_width = selected_num_bars * selected_diameter
spacing = (clear_width - total_bar_width) / (selected_num_bars - 1) if selected_num_bars > 1 else clear_width
min_spacing = max(25, selected_diameter)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**📊 Recalculated**")
    st.metric("a", f"{a_sel:.2f} mm")
    st.metric("c", f"{c_sel:.2f} mm")
    st.metric("φMn", f"{phi_Mn_sel:.2f} kN.m")

with col2:
    st.markdown("**⚡ Checks**")
    st.metric("εs", f"{eps_sel:.5f}")
    st.metric("Spacing", f"{spacing:.1f} mm")
    
    strain_st, strain_tp = get_strain_status(eps_sel)
    if strain_tp == "success":
        st.success(f"🟢 {strain_st}")
    elif strain_tp == "warning":
        st.warning(f"🟡 {strain_st}")
    else:
        st.error(f"🔴 {strain_st}")

with col3:
    st.markdown("**🎯 Final Status**")
    
    checks = [
        As_provided >= As_required,
        phi_Mn_sel >= Mu,
        eps_sel >= 0.002,
        spacing >= min_spacing
    ]
    
    if all(checks):
        st.markdown('<div class="safe-card">✅ APPROVED</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="unsafe-card">❌ REJECTED</div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"{'✅' if checks[0] else '❌'} Steel Area")
    st.markdown(f"{'✅' if checks[1] else '❌'} Capacity")
    st.markdown(f"{'✅' if checks[2] else '❌'} Ductility")
    st.markdown(f"{'✅' if checks[3] else '❌'} Spacing ({min_spacing:.0f}mm min)")
    
    st.metric("Utilization", f"{util_sel:.1f}%")

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION DRAWING
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown("---")
st.markdown('<h2 class="section-header">📐 Section Drawing</h2>', unsafe_allow_html=True)

svg_drawing = draw_section_svg(b, h, cover, selected_num_bars, selected_diameter, As_provided, As_required)
st.markdown(svg_drawing, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# REBAR TABLE
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown("---")
st.markdown('<h2 class="section-header">📋 Rebar Reference Table</h2>', unsafe_allow_html=True)

df_data = []
for diameter, areas in REBAR_DATA.items():
    row = {'Ø (mm)': diameter}
    for i, area in enumerate(areas, 1):
        row[f'{i}'] = int(area)
    df_data.append(row)

df = pd.DataFrame(df_data)
df = df.set_index('Ø (mm)')

st.dataframe(df, use_container_width=True)
st.caption("📝 All areas in mm²")

# ═══════════════════════════════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: #666; padding: 20px;">
        <p>🏗️ <strong>RC Section Design Calculator</strong> | ACI 318-19 & ECP 203</p>
        <p style="font-size: 0.8em;">⚠️ For educational purposes only. Verify with professional judgment.</p>
    </div>
""", unsafe_allow_html=True)
