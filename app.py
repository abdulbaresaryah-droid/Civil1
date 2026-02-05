import streamlit as st
import pandas as pd
import math
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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
    /* Main container */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 1400px;
    }
    
    /* Headers */
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 0.5rem;
        margin-top: -1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
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
    
    /* Input labels */
    .input-label {
        font-size: 0.9rem;
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 0.3rem;
    }
    
    /* Metrics */
    div[data-testid="stMetricValue"] {
        font-size: 1.2rem;
        font-weight: 600;
    }
    
    div[data-testid="stMetricLabel"] {
        font-size: 0.85rem;
    }
    
    /* Cards */
    .result-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        padding: 15px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    .safe-card {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        border-radius: 10px;
        padding: 20px;
        color: white;
        text-align: center;
        font-size: 1.3rem;
        font-weight: bold;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    .unsafe-card {
        background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
        border-radius: 10px;
        padding: 20px;
        color: white;
        text-align: center;
        font-size: 1.3rem;
        font-weight: bold;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    /* Info boxes */
    .info-box {
        background-color: #e8f4fd;
        border-left: 4px solid #1f77b4;
        padding: 10px 15px;
        border-radius: 0 8px 8px 0;
        margin: 10px 0;
    }
    
    .warning-box {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 10px 15px;
        border-radius: 0 8px 8px 0;
        margin: 10px 0;
    }
    
    .success-box {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        padding: 10px 15px;
        border-radius: 0 8px 8px 0;
        margin: 10px 0;
    }
    
    .error-box {
        background-color: #f8d7da;
        border-left: 4px solid #dc3545;
        padding: 10px 15px;
        border-radius: 0 8px 8px 0;
        margin: 10px 0;
    }
    
    /* Calculation steps */
    .calc-step {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 10px;
        margin: 5px 0;
        border: 1px solid #e9ecef;
    }
    
    /* Hide slider labels */
    .stSlider > label {
        display: none;
    }
    
    /* Divider */
    hr {
        margin-top: 1.5rem;
        margin-bottom: 1.5rem;
        border: none;
        border-top: 2px solid #e9ecef;
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
    """Initialize all session state variables with default values"""
    for key, value in DEFAULT_VALUES.items():
        if key not in st.session_state:
            st.session_state[key] = value

def reset_all_values():
    """Reset all values to defaults"""
    for key, value in DEFAULT_VALUES.items():
        st.session_state[key] = value

def clear_all_values():
    """Clear all values to zero"""
    for key in DEFAULT_VALUES.keys():
        if key in ['phi', 'jd', 'beta1', 'gamma_c', 'gamma_s']:
            continue
        st.session_state[key] = 0.0

initialize_session_state()

# ═══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def create_input_row(label, key, min_val, max_val, step, unit="", help_text=""):
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
            key=f"{key}_slider_widget",
            help=help_text
        )
    
    with col_input:
        input_val = st.number_input(
            label=f"{key}_input",
            min_value=float(min_val),
            max_value=float(max_val * 2),  # Allow manual input beyond slider max
            value=float(slider_val),
            step=float(step),
            label_visibility="collapsed",
            key=f"{key}_input_widget",
            format="%.2f"
        )
    
    # Update session state with the input value (takes precedence)
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


def draw_section(b, h, cover, num_bars, bar_diameter, As_provided, As_required):
    """Draw the cross-section using Plotly"""
    
    fig = go.Figure()
    
    # Concrete section (outer rectangle)
    fig.add_shape(
        type="rect",
        x0=0, y0=0, x1=b, y1=h,
        line=dict(color="gray", width=3),
        fillcolor="lightgray",
        opacity=0.5
    )
    
    # Cover zone (inner rectangle - effective area)
    fig.add_shape(
        type="rect",
        x0=cover, y0=cover, x1=b-cover, y1=h-cover,
        line=dict(color="blue", width=1, dash="dash"),
        fillcolor="rgba(0,0,255,0.05)"
    )
    
    # Calculate rebar positions
    d = h - cover
    effective_width = b - 2 * cover
    
    if num_bars > 0:
        if num_bars == 1:
            positions = [b / 2]
        else:
            spacing = effective_width / (num_bars - 1) if num_bars > 1 else 0
            positions = [cover + i * spacing for i in range(num_bars)]
        
        # Draw rebars
        for x_pos in positions:
            fig.add_shape(
                type="circle",
                x0=x_pos - bar_diameter/2,
                y0=cover - bar_diameter/2,
                x1=x_pos + bar_diameter/2,
                y1=cover + bar_diameter/2,
                line=dict(color="darkred", width=2),
                fillcolor="red"
            )
    
    # Dimension lines and annotations
    # Width dimension
    fig.add_annotation(
        x=b/2, y=-30,
        text=f"b = {b:.0f} mm",
        showarrow=False,
        font=dict(size=12, color="black")
    )
    
    # Height dimension
    fig.add_annotation(
        x=b+40, y=h/2,
        text=f"h = {h:.0f} mm",
        showarrow=False,
        font=dict(size=12, color="black"),
        textangle=-90
    )
    
    # Effective depth
    fig.add_annotation(
        x=b+80, y=d/2,
        text=f"d = {d:.0f} mm",
        showarrow=False,
        font=dict(size=11, color="blue"),
        textangle=-90
    )
    
    # Cover annotation
    fig.add_annotation(
        x=cover/2, y=cover/2,
        text=f"c={cover:.0f}",
        showarrow=False,
        font=dict(size=10, color="green")
    )
    
    # Reinforcement info
    fig.add_annotation(
        x=b/2, y=cover,
        text=f"{num_bars}Ø{bar_diameter}",
        showarrow=True,
        arrowhead=2,
        arrowsize=1,
        arrowwidth=1,
        arrowcolor="red",
        ax=0,
        ay=-50,
        font=dict(size=12, color="red", weight="bold")
    )
    
    # Steel area info box
    status_color = "green" if As_provided >= As_required else "red"
    fig.add_annotation(
        x=b/2, y=h+50,
        text=f"As,prov = {As_provided:.0f} mm² | As,req = {As_required:.0f} mm²",
        showarrow=False,
        font=dict(size=11, color=status_color),
        bgcolor="white",
        bordercolor=status_color,
        borderwidth=2,
        borderpad=5
    )
    
    fig.update_layout(
        title=dict(
            text="Cross-Section",
            x=0.5,
            font=dict(size=16)
        ),
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            range=[-50, b+120],
            scaleanchor="y",
            scaleratio=1
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            range=[-80, h+100]
        ),
        height=500,
        margin=dict(l=20, r=20, t=60, b=20),
        plot_bgcolor="white"
    )
    
    return fig


def create_moment_capacity_chart(Mu, phi_Mn, As_min, As_required, As_provided):
    """Create a visual comparison chart"""
    
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("Moment Capacity", "Steel Area"),
        specs=[[{"type": "bar"}, {"type": "bar"}]]
    )
    
    # Moment comparison
    fig.add_trace(
        go.Bar(
            x=["Applied Mu", "Capacity φMn"],
            y=[Mu, phi_Mn],
            marker_color=["#ff6b6b", "#51cf66"],
            text=[f"{Mu:.1f}", f"{phi_Mn:.1f}"],
            textposition="outside",
            name="Moment (kN.m)"
        ),
        row=1, col=1
    )
    
    # Steel area comparison
    fig.add_trace(
        go.Bar(
            x=["As,min", "As,req", "As,prov"],
            y=[As_min, As_required, As_provided],
            marker_color=["#ffd43b", "#ff6b6b", "#51cf66"],
            text=[f"{As_min:.0f}", f"{As_required:.0f}", f"{As_provided:.0f}"],
            textposition="outside",
            name="Steel Area (mm²)"
        ),
        row=1, col=2
    )
    
    fig.update_layout(
        height=350,
        showlegend=False,
        margin=dict(l=20, r=20, t=60, b=20)
    )
    
    return fig


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
        index=0,
        help="Choose the design code for calculations"
    )

with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 Reset Defaults", type="secondary", use_container_width=True):
        reset_all_values()
        st.rerun()

with col3:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🗑️ Clear All", type="secondary", use_container_width=True):
        clear_all_values()
        st.rerun()

with col4:
    st.markdown("<br>", unsafe_allow_html=True)
    show_details = st.checkbox("📋 Show Details", value=True)

# Display selected code info
if design_code == "ACI 318-19":
    st.info("📘 **ACI 318-19**: American Concrete Institute Building Code Requirements")
else:
    st.info("📗 **ECP 203**: Egyptian Code for Design and Construction of Concrete Structures")

# ═══════════════════════════════════════════════════════════════════════════════
# INPUT SECTION
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown('<h2 class="section-header">📋 Input Parameters</h2>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# Material Properties
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<h3 class="subsection-header">🔩 Material Properties</h3>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    fy = create_input_row(
        label="Steel Yield Strength, fy",
        key="fy",
        min_val=0.0,
        max_val=600.0,
        step=10.0,
        unit="MPa",
        help_text="Typical values: 400-500 MPa"
    )

with col2:
    if design_code == "ACI 318-19":
        fcu_label = "Concrete Strength, f'c"
    else:
        fcu_label = "Concrete Cube Strength, fcu"
    
    fcu = create_input_row(
        label=fcu_label,
        key="fcu",
        min_val=0.0,
        max_val=60.0,
        step=2.5,
        unit="MPa",
        help_text="Typical values: 25-40 MPa"
    )

# ─────────────────────────────────────────────────────────────────────────────
# Loading
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<h3 class="subsection-header">⚡ Loading</h3>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    Mu = create_input_row(
        label="Ultimate Moment, Mu",
        key="Mu",
        min_val=0.0,
        max_val=1000.0,
        step=5.0,
        unit="kN.m",
        help_text="Factored design moment"
    )

# ─────────────────────────────────────────────────────────────────────────────
# Section Dimensions
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<h3 class="subsection-header">📐 Section Dimensions</h3>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    b = create_input_row(
        label="Width, b",
        key="b",
        min_val=0.0,
        max_val=1500.0,
        step=25.0,
        unit="mm",
        help_text="Section width"
    )

with col2:
    h = create_input_row(
        label="Total Height, h",
        key="h",
        min_val=0.0,
        max_val=1500.0,
        step=25.0,
        unit="mm",
        help_text="Total section depth"
    )

with col3:
    cover = create_input_row(
        label="Concrete Cover",
        key="cover",
        min_val=0.0,
        max_val=100.0,
        step=5.0,
        unit="mm",
        help_text="Clear cover to reinforcement centroid"
    )

# ─────────────────────────────────────────────────────────────────────────────
# Design Parameters (Code Specific)
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<h3 class="subsection-header">⚙️ Design Parameters</h3>', unsafe_allow_html=True)

if design_code == "ACI 318-19":
    col1, col2, col3 = st.columns(3)
    
    with col1:
        phi = create_input_row(
            label="Strength Reduction Factor, φ",
            key="phi",
            min_val=0.65,
            max_val=0.90,
            step=0.05,
            unit="",
            help_text="φ = 0.9 for tension-controlled sections"
        )
    
    with col2:
        jd = create_input_row(
            label="Moment Arm Factor, j",
            key="jd",
            min_val=0.80,
            max_val=0.95,
            step=0.01,
            unit="",
            help_text="Initial assumption for lever arm"
        )
    
    with col3:
        # Auto-calculate β₁ based on f'c
        beta1_auto = calculate_beta1(fcu)
        st.markdown(f"**β₁ Factor** (auto-calculated)")
        st.info(f"β₁ = {beta1_auto:.3f}")
        beta1 = beta1_auto
        st.session_state.beta1 = beta1

else:  # Egyptian Code
    col1, col2 = st.columns(2)
    
    with col1:
        gamma_c = create_input_row(
            label="Concrete Safety Factor, γc",
            key="gamma_c",
            min_val=1.3,
            max_val=1.8,
            step=0.05,
            unit="",
            help_text="γc = 1.5 for normal conditions"
        )
    
    with col2:
        gamma_s = create_input_row(
            label="Steel Safety Factor, γs",
            key="gamma_s",
            min_val=1.0,
            max_val=1.3,
            step=0.05,
            unit="",
            help_text="γs = 1.15 for normal conditions"
        )

# ═══════════════════════════════════════════════════════════════════════════════
# INPUT VALIDATION
# ═══════════════════════════════════════════════════════════════════════════════

# Check for valid inputs
errors = []
warnings = []

if fy <= 0:
    errors.append("Steel yield strength (fy) must be greater than 0")
if fcu <= 0:
    errors.append("Concrete strength (fcu) must be greater than 0")
if Mu <= 0:
    errors.append("Ultimate moment (Mu) must be greater than 0")
if b <= 0:
    errors.append("Section width (b) must be greater than 0")
if h <= 0:
    errors.append("Section height (h) must be greater than 0")
if cover < 0:
    errors.append("Cover cannot be negative")
if h <= cover:
    errors.append("Section height must be greater than cover")

# Calculate effective depth
d = h - cover

if d <= 0:
    errors.append("Effective depth (d = h - cover) must be greater than 0")

# Warnings
if cover < 25:
    warnings.append("Cover is less than 25mm - check code minimum requirements")
if d < 100:
    warnings.append("Effective depth is very small - consider increasing section height")
if fcu > 50:
    warnings.append("High strength concrete - verify β₁ factor")

# Display errors and warnings
if errors:
    for error in errors:
        st.error(f"❌ {error}")
    st.stop()

if warnings:
    for warning in warnings:
        st.warning(f"⚠️ {warning}")

# ═══════════════════════════════════════════════════════════════════════════════
# CALCULATIONS
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown("---")
st.markdown('<h2 class="section-header">🔢 Design Calculations</h2>', unsafe_allow_html=True)

# Store all calculation steps
calc_steps = []

try:
    # Convert moment to N.mm
    Mu_Nmm = Mu * 1e6
    
    # ═══════════════════════════════════════════════════════════════════════════
    # ACI 318-19 CALCULATIONS
    # ═══════════════════════════════════════════════════════════════════════════
    if design_code == "ACI 318-19":
        
        # Step 1: Effective Depth
        calc_steps.append({
            'step': 1,
            'description': 'Calculate Effective Depth',
            'formula': r'd = h - \text{cover}',
            'substitution': f'{h:.0f} - {cover:.0f}',
            'result': f'{d:.1f} mm',
            'variable': 'd'
        })
        
        # Step 2: Initial Steel Area Estimate
        As_initial = Mu_Nmm / (phi * fy * jd * d)
        calc_steps.append({
            'step': 2,
            'description': 'Initial Steel Area Estimate',
            'formula': r'A_{s,init} = \frac{M_u}{\phi \cdot f_y \cdot j \cdot d}',
            'substitution': f'\\frac{{{Mu*1e6:.2e}}}{{{phi:.2f} \\times {fy:.0f} \\times {jd:.2f} \\times {d:.1f}}}',
            'result': f'{As_initial:.1f} mm²',
            'variable': 'As,init'
        })
        
        # Step 3: Depth of Compression Block
        a_initial = (As_initial * fy) / (0.85 * fcu * b)
        calc_steps.append({
            'step': 3,
            'description': 'Depth of Compression Block',
            'formula': r"a = \frac{A_s \cdot f_y}{0.85 \cdot f'_c \cdot b}",
            'substitution': f'\\frac{{{As_initial:.1f} \\times {fy:.0f}}}{{0.85 \\times {fcu:.1f} \\times {b:.0f}}}',
            'result': f'{a_initial:.2f} mm',
            'variable': 'a'
        })
        
        # Step 4: Refined Steel Area
        As_calculated = Mu_Nmm / (phi * fy * (d - a_initial/2))
        calc_steps.append({
            'step': 4,
            'description': 'Refined Steel Area',
            'formula': r'A_s = \frac{M_u}{\phi \cdot f_y \cdot (d - a/2)}',
            'substitution': f'\\frac{{{Mu*1e6:.2e}}}{{{phi:.2f} \\times {fy:.0f} \\times ({d:.1f} - {a_initial/2:.2f})}}',
            'result': f'{As_calculated:.1f} mm²',
            'variable': 'As,calc'
        })
        
        # Step 5: Minimum Steel Area (ACI 318-19 Section 9.6.1.2)
        As_min_1 = (0.25 * math.sqrt(fcu) / fy) * b * d
        As_min_2 = (1.4 / fy) * b * d
        As_min = max(As_min_1, As_min_2)
        
        calc_steps.append({
            'step': 5,
            'description': 'Minimum Steel Area',
            'formula': r"A_{s,min} = \max\left(\frac{0.25\sqrt{f'_c}}{f_y} b_w d, \frac{1.4}{f_y} b_w d\right)",
            'substitution': f'\\max({As_min_1:.1f}, {As_min_2:.1f})',
            'result': f'{As_min:.1f} mm²',
            'variable': 'As,min'
        })
        
        # Step 6: Required Steel Area
        As_required = max(As_calculated, As_min)
        governing = "As,min governs" if As_required == As_min else "As,calc governs"
        
        calc_steps.append({
            'step': 6,
            'description': 'Required Steel Area',
            'formula': r'A_{s,req} = \max(A_{s,calc}, A_{s,min})',
            'substitution': f'\\max({As_calculated:.1f}, {As_min:.1f})',
            'result': f'{As_required:.1f} mm² ({governing})',
            'variable': 'As,req'
        })
        
        # Step 7: Final Compression Block Depth
        a_final = (As_required * fy) / (0.85 * fcu * b)
        calc_steps.append({
            'step': 7,
            'description': 'Final Compression Block Depth',
            'formula': r"a = \frac{A_{s,req} \cdot f_y}{0.85 \cdot f'_c \cdot b}",
            'substitution': f'\\frac{{{As_required:.1f} \\times {fy:.0f}}}{{0.85 \\times {fcu:.1f} \\times {b:.0f}}}',
            'result': f'{a_final:.2f} mm',
            'variable': 'a,final'
        })
        
        # Step 8: Neutral Axis Depth
        c = a_final / beta1
        calc_steps.append({
            'step': 8,
            'description': 'Neutral Axis Depth',
            'formula': r'c = \frac{a}{\beta_1}',
            'substitution': f'\\frac{{{a_final:.2f}}}{{{beta1:.3f}}}',
            'result': f'{c:.2f} mm',
            'variable': 'c'
        })
        
        # Step 9: Steel Strain
        epsilon_cu = 0.003  # Ultimate concrete strain
        epsilon_s = ((d - c) / c) * epsilon_cu
        calc_steps.append({
            'step': 9,
            'description': 'Steel Strain at Ultimate',
            'formula': r'\varepsilon_s = \frac{d - c}{c} \times \varepsilon_{cu}',
            'substitution': f'\\frac{{{d:.1f} - {c:.2f}}}{{{c:.2f}}} \\times 0.003',
            'result': f'{epsilon_s:.5f}',
            'variable': 'εs'
        })
        
        # Step 10: Design Moment Capacity
        phi_Mn_Nmm = phi * As_required * fy * (d - a_final/2)
        phi_Mn = phi_Mn_Nmm / 1e6
        calc_steps.append({
            'step': 10,
            'description': 'Design Moment Capacity',
            'formula': r'\phi M_n = \phi \cdot A_s \cdot f_y \cdot (d - a/2)',
            'substitution': f'{phi:.2f} \\times {As_required:.1f} \\times {fy:.0f} \\times ({d:.1f} - {a_final/2:.2f})',
            'result': f'{phi_Mn:.2f} kN.m',
            'variable': 'φMn'
        })
        
        # Maximum steel ratio check
        rho = As_required / (b * d)
        rho_max = 0.85 * beta1 * (fcu / fy) * (epsilon_cu / (epsilon_cu + 0.004))
        
    # ═══════════════════════════════════════════════════════════════════════════
    # EGYPTIAN CODE (ECP 203) CALCULATIONS
    # ═══════════════════════════════════════════════════════════════════════════
    else:
        
        # Convert to ECP units (cm and kg/cm²)
        d_cm = d / 10           # mm to cm
        b_cm = b / 10           # mm to cm
        h_cm = h / 10           # mm to cm
        Mu_tcm = Mu / 10        # kN.m to t.cm (1 kN.m = 0.1 t.m = 10 t.cm)
        Mu_kgcm = Mu * 1e5      # kN.m to kg.cm
        fcu_kgcm2 = fcu * 10.197  # MPa to kg/cm² (1 MPa ≈ 10.197 kg/cm²)
        fy_kgcm2 = fy * 10.197    # MPa to kg/cm²
        
        # Step 1: Effective Depth
        calc_steps.append({
            'step': 1,
            'description': 'Effective Depth',
            'formula': r'd = h - \text{cover}',
            'substitution': f'{h:.0f} - {cover:.0f}',
            'result': f'{d:.1f} mm = {d_cm:.2f} cm',
            'variable': 'd'
        })
        
        # Step 2: C₁ Factor (ECP characteristic factor)
        # C₁ = d / √(Mu / (fcu × b))
        # Using simplified formula: C₁ = d / √(fcu × b) for checking
        C1_check = d_cm / math.sqrt(Mu_kgcm / (fcu_kgcm2 * b_cm))
        
        # More accurate C1 calculation
        C1 = d_cm * math.sqrt(fcu_kgcm2 * b_cm / Mu_kgcm)
        C1_min = 2.76  # For singly reinforced sections
        
        calc_steps.append({
            'step': 2,
            'description': 'C₁ Factor (Section Check)',
            'formula': r'C_1 = d \times \sqrt{\frac{f_{cu} \times b}{M_u}}',
            'substitution': f'{d_cm:.2f} \\times \\sqrt{{\\frac{{{fcu_kgcm2:.1f} \\times {b_cm:.1f}}}{{{Mu_kgcm:.0f}}}}}',
            'result': f'{C1:.3f}',
            'variable': 'C₁'
        })
        
        # Step 3: Check C₁ ≥ C₁,min
        c1_check_pass = C1 >= C1_min
        calc_steps.append({
            'step': 3,
            'description': 'C₁ Check (Singly Reinforced)',
            'formula': r'C_1 \geq C_{1,min} = 2.76',
            'substitution': f'{C1:.3f} \\geq 2.76',
            'result': f'{"✓ PASS - Singly Reinforced OK" if c1_check_pass else "✗ FAIL - Need Compression Steel"}',
            'variable': 'Check'
        })
        
        if not c1_check_pass:
            st.error("❌ Section requires compression reinforcement (doubly reinforced). C₁ < 2.76")
            st.warning("Consider increasing section dimensions or use doubly reinforced design.")
            st.stop()
        
        # Step 4: Calculate J Factor
        term_inside_sqrt = 0.25 - (Mu_kgcm / (0.9 * fcu_kgcm2 * b_cm * d_cm * d_cm))
        
        if term_inside_sqrt < 0:
            st.error("❌ Section is too small for the applied moment!")
            st.stop()
        
        J_calculated = (1/1.15) * (0.5 + math.sqrt(term_inside_sqrt))
        J_max = 0.826  # Maximum J for singly reinforced
        J = min(J_calculated, J_max)
        
        calc_steps.append({
            'step': 4,
            'description': 'J Factor Calculation',
            'formula': r'J = \frac{1}{1.15} \times \left(0.5 + \sqrt{0.25 - \frac{M_u}{0.9 \times f_{cu} \times b \times d^2}}\right)',
            'substitution': f'\\frac{{1}}{{1.15}} \\times (0.5 + \\sqrt{{0.25 - \\frac{{{Mu_kgcm:.0f}}}{{0.9 \\times {fcu_kgcm2:.1f} \\times {b_cm:.1f} \\times {d_cm:.2f}^2}}}})',
            'result': f'{J_calculated:.4f}',
            'variable': 'J,calc'
        })
        
        calc_steps.append({
            'step': 5,
            'description': 'J Factor (Limited)',
            'formula': r'J = \min(J_{calc}, J_{max} = 0.826)',
            'substitution': f'\\min({J_calculated:.4f}, 0.826)',
            'result': f'{J:.4f}',
            'variable': 'J'
        })
        
        # Step 6: Required Steel Area
        As_calculated_cm2 = Mu_kgcm / (fy_kgcm2 * J * d_cm)
        As_calculated = As_calculated_cm2 * 100  # cm² to mm²
        
        calc_steps.append({
            'step': 6,
            'description': 'Calculated Steel Area',
            'formula': r'A_s = \frac{M_u}{f_y \times J \times d}',
            'substitution': f'\\frac{{{Mu_kgcm:.0f}}}{{{fy_kgcm2:.1f} \\times {J:.4f} \\times {d_cm:.2f}}}',
            'result': f'{As_calculated:.1f} mm² ({As_calculated_cm2:.2f} cm²)',
            'variable': 'As,calc'
        })
        
        # Step 7: Minimum Steel Area (ECP 203)
        As_min = max(0.6/fy * b * d, 0.0015 * b * d)  # ECP minimum
        
        calc_steps.append({
            'step': 7,
            'description': 'Minimum Steel Area (ECP)',
            'formula': r'A_{s,min} = \max\left(\frac{0.6}{f_y} \times b \times d, 0.0015 \times b \times d\right)',
            'substitution': f'\\max(\\frac{{0.6}}{{{fy:.0f}}} \\times {b:.0f} \\times {d:.1f}, 0.0015 \\times {b:.0f} \\times {d:.1f})',
            'result': f'{As_min:.1f} mm²',
            'variable': 'As,min'
        })
        
        # Step 8: Required Steel Area
        As_required = max(As_calculated, As_min)
        governing = "As,min governs" if As_required == As_min else "As,calc governs"
        
        calc_steps.append({
            'step': 8,
            'description': 'Required Steel Area',
            'formula': r'A_{s,req} = \max(A_{s,calc}, A_{s,min})',
            'substitution': f'\\max({As_calculated:.1f}, {As_min:.1f})',
            'result': f'{As_required:.1f} mm² ({governing})',
            'variable': 'As,req'
        })
        
        # Step 9: Compression block depth (for verification)
        a_final = (As_required * fy) / (0.67 * fcu * b / gamma_c)
        c = a_final / 0.8
        
        calc_steps.append({
            'step': 9,
            'description': 'Compression Block Depth',
            'formula': r'a = \frac{A_s \times f_y}{0.67 \times f_{cu} \times b / \gamma_c}',
            'substitution': f'\\frac{{{As_required:.1f} \\times {fy:.0f}}}{{0.67 \\times {fcu:.1f} \\times {b:.0f} / {gamma_c:.2f}}}',
            'result': f'{a_final:.2f} mm',
            'variable': 'a'
        })
        
        # Step 10: Steel Strain
        epsilon_cu = 0.003
        epsilon_s = ((d - c) / c) * epsilon_cu if c > 0 else 0.01
        
        calc_steps.append({
            'step': 10,
            'description': 'Steel Strain Check',
            'formula': r'\varepsilon_s = \frac{d - c}{c} \times \varepsilon_{cu}',
            'substitution': f'\\frac{{{d:.1f} - {c:.2f}}}{{{c:.2f}}} \\times 0.003',
            'result': f'{epsilon_s:.5f}',
            'variable': 'εs'
        })
        
        # Step 11: Design Moment Capacity
        phi_Mn_Nmm = (1/gamma_s) * As_required * fy * (d - a_final/2)
        phi_Mn = phi_Mn_Nmm / 1e6
        phi = 1/gamma_s  # For display purposes
        
        calc_steps.append({
            'step': 11,
            'description': 'Design Moment Capacity',
            'formula': r'M_d = \frac{A_s \times f_y}{\gamma_s} \times (d - a/2)',
            'substitution': f'\\frac{{{As_required:.1f} \\times {fy:.0f}}}{{{gamma_s:.2f}}} \\times ({d:.1f} - {a_final/2:.2f})',
            'result': f'{phi_Mn:.2f} kN.m',
            'variable': 'Md'
        })
        
        # Placeholder for consistency
        beta1 = 0.8
        rho = As_required / (b * d)
        rho_max = 0.67 * 0.8 * (fcu / fy) * (0.003 / (0.003 + 0.002)) / gamma_c
    
    # ═══════════════════════════════════════════════════════════════════════════
    # SAFETY CHECKS (Common to both codes)
    # ═══════════════════════════════════════════════════════════════════════════
    
    # Strain check
    strain_status, strain_type = get_strain_status(epsilon_s)
    strain_safe = epsilon_s >= 0.002
    
    # Capacity check
    capacity_safe = phi_Mn >= Mu
    
    # Overall status
    overall_safe = strain_safe and capacity_safe and (As_required >= As_min)
    
    # Utilization ratio
    utilization = (Mu / phi_Mn) * 100 if phi_Mn > 0 else 0

except ZeroDivisionError:
    st.error("❌ Calculation Error: Division by zero. Please check your inputs.")
    st.stop()
except ValueError as ve:
    st.error(f"❌ Calculation Error: {str(ve)}")
    st.stop()
except Exception as e:
    st.error(f"❌ Unexpected Error: {str(e)}")
    st.stop()

# ═══════════════════════════════════════════════════════════════════════════════
# DISPLAY CALCULATION STEPS
# ═══════════════════════════════════════════════════════════════════════════════

if show_details:
    st.markdown(f"**📘 Design Code: {design_code}**")
    
    for calc in calc_steps:
        with st.container():
            col1, col2, col3, col4 = st.columns([0.5, 2.5, 2.5, 1.5])
            
            with col1:
                st.markdown(f"**{calc['step']}**")
            
            with col2:
                st.markdown(f"**{calc['description']}**")
                st.latex(calc['formula'])
            
            with col3:
                st.markdown("**Substitution:**")
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
    
    # Strain status with color
    if strain_type == "success":
        st.success(f"🟢 {strain_status}")
    elif strain_type == "warning":
        st.warning(f"🟡 {strain_status}")
    else:
        st.error(f"🔴 {strain_status}")

with col3:
    st.markdown("### ✅ Safety Status")
    
    if overall_safe:
        st.markdown("""
            <div class="safe-card">
                ✅ DESIGN IS SAFE
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div class="unsafe-card">
                ❌ DESIGN NEEDS REVISION
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Individual checks
    st.markdown("**Safety Checks:**")
    st.markdown(f"{'✅' if epsilon_s >= 0.002 else '❌'} Strain: εs = {epsilon_s:.5f} {'≥' if epsilon_s >= 0.002 else '<'} 0.002")
    st.markdown(f"{'✅' if capacity_safe else '❌'} Capacity: φMn = {phi_Mn:.2f} {'≥' if capacity_safe else '<'} Mu = {Mu:.2f}")
    st.markdown(f"{'✅' if As_required >= As_min else '❌'} Minimum Steel: As,req ≥ As,min")
    
    st.metric("Utilization", f"{utilization:.1f} %")
    st.metric("Capacity (φMn)", f"{phi_Mn:.2f} kN.m")

# ═══════════════════════════════════════════════════════════════════════════════
# REINFORCEMENT SELECTION
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown("---")
st.markdown('<h2 class="section-header">🔧 Reinforcement Selection</h2>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# Automatic Suggestions
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("### 💡 Recommended Configurations")

suggestions = []
for diameter in [10, 12, 14, 16, 18, 20, 22, 25, 28, 32]:
    area_per_bar = REBAR_DATA[diameter][0]
    num_bars = math.ceil(As_required / area_per_bar)
    
    if 2 <= num_bars <= 8:  # Practical range
        total_area = REBAR_DATA[diameter][num_bars - 1]
        excess = ((total_area - As_required) / As_required) * 100
        
        # Check spacing (minimum 25mm or bar diameter)
        clear_width = b - 2 * cover
        min_spacing = max(25, diameter)
        max_bars = int((clear_width + min_spacing) / (diameter + min_spacing))
        
        if num_bars <= max_bars:
            suggestions.append({
                'config': f"{num_bars}Ø{diameter}",
                'num': num_bars,
                'diameter': diameter,
                'area': total_area,
                'excess': excess,
                'practical': True
            })

# Display top 6 suggestions
if suggestions:
    suggestions = sorted(suggestions, key=lambda x: x['excess'])[:6]
    
    cols = st.columns(3)
    for i, sugg in enumerate(suggestions):
        with cols[i % 3]:
            color = "#28a745" if sugg['excess'] < 20 else "#ffc107" if sugg['excess'] < 40 else "#dc3545"
            st.markdown(f"""
                <div style="background: linear-gradient(135deg, {color}22, {color}11); 
                            border: 2px solid {color}; border-radius: 10px; 
                            padding: 15px; text-align: center; margin: 5px 0;">
                    <h3 style="margin: 0; color: {color};">{sugg['config']}</h3>
                    <p style="margin: 5px 0;">As = {sugg['area']:.0f} mm²</p>
                    <p style="margin: 0; font-size: 0.9em; color: #666;">+{sugg['excess']:.1f}% excess</p>
                </div>
            """, unsafe_allow_html=True)
else:
    st.warning("No suitable single-layer configuration found. Consider using multiple layers.")

# ─────────────────────────────────────────────────────────────────────────────
# Manual Selection
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 🎯 Manual Selection & Verification")

col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

with col1:
    selected_diameter = st.selectbox(
        "Bar Diameter (mm)",
        options=list(REBAR_DATA.keys()),
        index=list(REBAR_DATA.keys()).index(st.session_state.selected_diameter),
        key='diameter_select'
    )
    st.session_state.selected_diameter = selected_diameter

with col2:
    selected_num_bars = st.selectbox(
        "Number of Bars",
        options=list(range(1, 10)),
        index=st.session_state.selected_num_bars - 1,
        key='num_bars_select'
    )
    st.session_state.selected_num_bars = selected_num_bars

# Calculate selected configuration
As_provided = REBAR_DATA[selected_diameter][selected_num_bars - 1]
excess_pct = ((As_provided - As_required) / As_required) * 100

with col3:
    st.metric("Provided Area", f"{As_provided:.0f} mm²")

with col4:
    if As_provided >= As_required:
        st.success(f"✓ +{excess_pct:.1f}% excess")
    else:
        st.error(f"✗ {excess_pct:.1f}% deficit")

# ─────────────────────────────────────────────────────────────────────────────
# Detailed Verification
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### ✅ Selected Configuration Verification")

# Recalculate with selected steel
if design_code == "ACI 318-19":
    a_selected = (As_provided * fy) / (0.85 * fcu * b)
    c_selected = a_selected / beta1
    phi_Mn_selected = (phi * As_provided * fy * (d - a_selected/2)) / 1e6
else:
    a_selected = (As_provided * fy) / (0.67 * fcu * b / gamma_c)
    c_selected = a_selected / 0.8
    phi_Mn_selected = ((1/gamma_s) * As_provided * fy * (d - a_selected/2)) / 1e6

epsilon_s_selected = ((d - c_selected) / c_selected) * 0.003 if c_selected > 0 else 0.01
utilization_selected = (Mu / phi_Mn_selected) * 100 if phi_Mn_selected > 0 else 0

# Spacing check
clear_width = b - 2 * cover
total_bar_width = selected_num_bars * selected_diameter
spacing = (clear_width - total_bar_width) / (selected_num_bars - 1) if selected_num_bars > 1 else clear_width
min_spacing = max(25, selected_diameter, 1.5 * 20)  # Assuming 20mm max aggregate

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**📊 Recalculated Values**")
    st.metric("a (selected)", f"{a_selected:.2f} mm")
    st.metric("c (selected)", f"{c_selected:.2f} mm")
    st.metric("c/d ratio", f"{(c_selected/d):.4f}")
    st.metric("φMn (selected)", f"{phi_Mn_selected:.2f} kN.m")

with col2:
    st.markdown("**⚡ Strain & Spacing**")
    st.metric("εs (selected)", f"{epsilon_s_selected:.5f}")
    
    strain_status_sel, strain_type_sel = get_strain_status(epsilon_s_selected)
    if strain_type_sel == "success":
        st.success(f"🟢 {strain_status_sel}")
    elif strain_type_sel == "warning":
        st.warning(f"🟡 {strain_status_sel}")
    else:
        st.error(f"🔴 {strain_status_sel}")
    
    st.metric("Bar Spacing", f"{spacing:.1f} mm")
    if spacing >= min_spacing:
        st.success(f"✓ Spacing OK (≥ {min_spacing:.0f} mm)")
    else:
        st.error(f"✗ Spacing too small (< {min_spacing:.0f} mm)")

with col3:
    st.markdown("**🎯 Final Verification**")
    
    checks = [
        As_provided >= As_required,
        phi_Mn_selected >= Mu,
        epsilon_s_selected >= 0.002,
        spacing >= min_spacing
    ]
    
    all_pass = all(checks)
    
    if all_pass:
        st.markdown("""
            <div class="safe-card">
                ✅ CONFIGURATION APPROVED
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div class="unsafe-card">
                ❌ CONFIGURATION REJECTED
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"{'✅' if checks[0] else '❌'} Steel Area Check")
    st.markdown(f"{'✅' if checks[1] else '❌'} Moment Capacity Check")
    st.markdown(f"{'✅' if checks[2] else '❌'} Ductility Check (εs ≥ 0.002)")
    st.markdown(f"{'✅' if checks[3] else '❌'} Spacing Check")
    
    st.metric("Final Utilization", f"{utilization_selected:.1f} %")

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION DRAWING
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown("---")
st.markdown('<h2 class="section-header">📐 Section Visualization</h2>', unsafe_allow_html=True)

col1, col2 = st.columns([1, 1])

with col1:
    fig_section = draw_section(b, h, cover, selected_num_bars, selected_diameter, As_provided, As_required)
    st.plotly_chart(fig_section, use_container_width=True)

with col2:
    fig_comparison = create_moment_capacity_chart(Mu, phi_Mn_selected, As_min, As_required, As_provided)
    st.plotly_chart(fig_comparison, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# REBAR REFERENCE TABLE
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown("---")
st.markdown('<h2 class="section-header">📋 Rebar Area Reference Table</h2>', unsafe_allow_html=True)

# Create DataFrame
df_data = []
for diameter, areas in REBAR_DATA.items():
    row = {'Ø (mm)': diameter}
    for i, area in enumerate(areas, 1):
        row[f'{i} bar'] = area
    df_data.append(row)

df = pd.DataFrame(df_data)
df = df.set_index('Ø (mm)')

# Highlight the selected configuration
def highlight_selection(val):
    return ''

# Style the dataframe
styled_df = df.style.format("{:.0f}").background_gradient(cmap='Blues', axis=None)

st.dataframe(styled_df, use_container_width=True, height=400)

st.caption("📝 All areas in mm². Click on a cell to select that configuration.")

# ═══════════════════════════════════════════════════════════════════════════════
# EXPORT SECTION
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown("---")
st.markdown('<h2 class="section-header">📤 Export Results</h2>', unsafe_allow_html=True)

# Create summary data for export
summary_data = {
    'Parameter': [
        'Design Code',
        'Ultimate Moment (Mu)',
        'Section Width (b)',
        'Section Height (h)',
        'Effective Depth (d)',
        'Concrete Cover',
        'Steel Strength (fy)',
        'Concrete Strength (fcu)',
        'Required Steel Area (As,req)',
        'Minimum Steel Area (As,min)',
        'Selected Reinforcement',
        'Provided Steel Area (As,prov)',
        'Design Capacity (φMn)',
        'Utilization Ratio',
        'Steel Strain (εs)',
        'Section Status'
    ],
    'Value': [
        design_code,
        f'{Mu:.2f} kN.m',
        f'{b:.0f} mm',
        f'{h:.0f} mm',
        f'{d:.1f} mm',
        f'{cover:.0f} mm',
        f'{fy:.0f} MPa',
        f'{fcu:.1f} MPa',
        f'{As_required:.1f} mm²',
        f'{As_min:.1f} mm²',
        f'{selected_num_bars}Ø{selected_diameter}',
        f'{As_provided:.0f} mm²',
        f'{phi_Mn_selected:.2f} kN.m',
        f'{utilization_selected:.1f}%',
        f'{epsilon_s_selected:.5f}',
        'SAFE ✓' if all_pass else 'NEEDS REVISION ✗'
    ]
}

summary_df = pd.DataFrame(summary_data)

col1, col2, col3 = st.columns(3)

with col1:
    csv = summary_df.to_csv(index=False)
    st.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name=f"RC_Design_{design_code.replace(' ', '_')}.csv",
        mime="text/csv",
        use_container_width=True
    )

with col2:
    # Create detailed text report
    report = f"""
╔══════════════════════════════════════════════════════════════════╗
║              RC SECTION DESIGN CALCULATION REPORT                 ║
╠══════════════════════════════════════════════════════════════════╣
║  Design Code: {design_code:<50} ║
╠══════════════════════════════════════════════════════════════════╣
║  INPUT DATA                                                       ║
╠──────────────────────────────────────────────────────────────────╣
║  Ultimate Moment (Mu)     : {Mu:>10.2f} kN.m                      ║
║  Section Width (b)        : {b:>10.0f} mm                         ║
║  Section Height (h)       : {h:>10.0f} mm                         ║
║  Concrete Cover           : {cover:>10.0f} mm                     ║
║  Steel Strength (fy)      : {fy:>10.0f} MPa                       ║
║  Concrete Strength (fcu)  : {fcu:>10.1f} MPa                      ║
╠══════════════════════════════════════════════════════════════════╣
║  CALCULATION RESULTS                                              ║
╠──────────────────────────────────────────────────────────────────╣
║  Effective Depth (d)      : {d:>10.1f} mm                         ║
║  Required Steel (As,req)  : {As_required:>10.1f} mm²              ║
║  Minimum Steel (As,min)   : {As_min:>10.1f} mm²                   ║
║  Compression Block (a)    : {a_final:>10.2f} mm                   ║
║  Neutral Axis (c)         : {c:>10.2f} mm                         ║
║  Steel Strain (εs)        : {epsilon_s:>10.5f}                    ║
╠══════════════════════════════════════════════════════════════════╣
║  SELECTED REINFORCEMENT                                           ║
╠──────────────────────────────────────────────────────────────────╣
║  Configuration            : {selected_num_bars}Ø{selected_diameter:<30} ║
║  Provided Area (As,prov)  : {As_provided:>10.0f} mm²              ║
║  Design Capacity (φMn)    : {phi_Mn_selected:>10.2f} kN.m         ║
║  Utilization              : {utilization_selected:>10.1f} %       ║
╠══════════════════════════════════════════════════════════════════╣
║  STATUS: {'✅ DESIGN IS SAFE' if all_pass else '❌ NEEDS REVISION':<52} ║
╚══════════════════════════════════════════════════════════════════╝
"""
    
    st.download_button(
        label="📄 Download Report",
        data=report,
        file_name=f"RC_Design_Report_{design_code.replace(' ', '_')}.txt",
        mime="text/plain",
        use_container_width=True
    )

with col3:
    st.info("💡 Tip: Copy this summary for your records")

# ═══════════════════════════════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: #666; padding: 20px;">
        <p>🏗️ <strong>RC Section Design Calculator</strong></p>
        <p style="font-size: 0.9em;">
            Supports ACI 318-19 & Egyptian Code (ECP 203) | 
            Rectangular Beam Sections | 
            Flexural Design
        </p>
        <p style="font-size: 0.8em; color: #999;">
            ⚠️ This tool is for educational purposes. Always verify results with professional engineering judgment.
        </p>
    </div>
""", unsafe_allow_html=True)
