"""
Circular Economy Assessment - Interactive Streamlit GUI
========================================================

Interactive dashboard for exploring circular economy pathways through
parameter tuning and real-time 3D visualization.

Usage: streamlit run app.py

Author: [Your Name]
Version: 1.0
Date: February 2026
"""

import streamlit as st
import pandas as pd
import numpy as np
from circularity_core import (
    BurdenMetrics,
    LifecycleStage,
    Benchmarks,
    Constraints,
    CircularityAssessment,
    CircularityVisualizer
)

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Circular Economy Assessment",
    page_icon="🔄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better spacing
st.markdown("""
<style>
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# TITLE
# ============================================================================

st.title("🔄 Circular Economy Lifecycle Assessment")
st.markdown("### Interactive 3D Ternary Burden-Space Exploration")
st.markdown("---")

# ============================================================================
# SIDEBAR: GLOBAL SETTINGS
# ============================================================================

with st.sidebar:
    st.header("🌍 Global Settings")

    st.subheader("Benchmarks (Per-Cycle Basis)")
    cost_benchmark_per_cycle = st.number_input(
        "Cost Benchmark ($/kg per cycle)", 
        min_value=0.1, max_value=30.0, value=0.5, step=0.1,
        help="Benchmark cost per recycling cycle (for normalization)"
        key="cost_benchmark_input"
    )
    env_benchmark_per_cycle = st.number_input(
        "Environmental Benchmark (kg CO₂-eq/kg per cycle)", 
        min_value=0.1, max_value=10.0, value=1.0, step=0.1,
        help="Benchmark environmental impact per recycling cycle"
    )
    integrity_benchmark_per_cycle = st.number_input(
        "Integrity Benchmark (loss per cycle)", 
        min_value=0.01, max_value=0.8, value=0.1, step=0.01,
        help="Benchmark integrity loss per recycling cycle"
    )

    st.markdown("---")

    st.subheader("Constraints (Optional)")
    enable_constraints = st.checkbox("Enable Constraints", value=False)

    if enable_constraints:
        constraint_cost = st.number_input(
            "Max Acceptable Cost ($/kg)",
            min_value=0.0,
            max_value=10.0,
            value=5.0,
            step=0.5
        )

        constraint_env = st.number_input(
            "Max Acceptable Environmental (kg CO₂)",
            min_value=0.0,
            max_value=20.0,
            value=8.0,
            step=1.0
        )

        constraint_integrity = st.slider(
            "Min Integrity Remaining (%)",
            min_value=0,
            max_value=100,
            value=15,
            step=5
        ) / 100.0
    else:
        constraint_cost = None
        constraint_env = None
        constraint_integrity = None

    st.markdown("---")

    st.subheader("Pathway Selection")
    enable_mechanical = st.checkbox("Mechanical Recycling", value=True)
    enable_chemical = st.checkbox("Chemical Recycling", value=True)
    enable_downcycle = st.checkbox("Downcycling", value=True)

# ============================================================================
# CREATE TABS FOR PATHWAY CONFIGURATION
# ============================================================================

tab1, tab2, tab3, tab4 = st.tabs([
    "⚙️ Mechanical Recycling", 
    "🧪 Chemical Recycling", 
    "📦 Downcycling",
    "📊 Visualization Settings"
])

# ============================================================================
# TAB 1: MECHANICAL RECYCLING PATHWAY
# ============================================================================

with tab1:
    st.header("Mechanical Closed-Loop Recycling")
    st.markdown("*Conventional mechanical recycling with repeated bottle-to-bottle cycles*")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Virgin Production Stage")
        mech_virgin_cost = st.number_input("Virgin Cost ($/kg)", 0.0, 5.0, 1.20, 0.05, key="mech_v_cost")
        mech_virgin_env = st.number_input("Virgin Environmental", 0.0, 10.0, 3.5, 0.1, key="mech_v_env")
        mech_virgin_integrity = st.number_input("Virgin Integrity Loss", 0.0, 0.1, 0.0, 0.01, key="mech_v_int")
        mech_virgin_duration = st.number_input("Virgin Duration (years)", 0.0, 1.0, 0.0, 0.1, key="mech_v_dur")
        mech_virgin_mass = st.slider("Virgin Mass Fraction", 0.5, 1.0, 1.0, 0.01, key="mech_v_mass")

        st.subheader("Use Stage (Bottle)")
        mech_use_cost = st.number_input("Use Cost ($/kg)", 0.0, 1.0, 0.05, 0.01, key="mech_u_cost")
        mech_use_env = st.number_input("Use Environmental", 0.0, 1.0, 0.1, 0.01, key="mech_u_env")
        mech_use_integrity = st.slider("Use Integrity Loss", 0.0, 0.2, 0.03, 0.01, key="mech_u_int")
        mech_use_duration = st.number_input("Use Duration (years)", 0.0, 2.0, 0.3, 0.1, key="mech_u_dur")
        mech_use_mass = st.slider("Use Mass Fraction", 0.5, 1.0, 1.0, 0.01, key="mech_u_mass")

    with col2:
        st.subheader("Recycling Loop")
        mech_base_cost = st.number_input("Base Cost ($/kg)", 0.0, 5.0, 0.85, 0.05, key="mech_r_cost")
        mech_base_env = st.number_input("Base Environmental", 0.0, 5.0, 1.0, 0.1, key="mech_r_env")
        mech_base_integrity = st.slider("Base Integrity Loss", 0.0, 0.3, 0.06, 0.01, key="mech_r_int")
        mech_duration = st.number_input("Duration per Cycle (years)", 0.0, 2.0, 0.3, 0.1, key="mech_r_dur")
        mech_mass = st.slider("Mass Fraction per Cycle", 0.5, 1.0, 0.95, 0.01, key="mech_r_mass")

        st.markdown("**Per-Cycle Increases**")
        mech_cycles = st.number_input("Number of Cycles", 1, 50, 20, 1, key="mech_cycles")
        mech_cost_inc = st.number_input("Cost Increase per Cycle", 0.0, 0.5, 0.12, 0.01, key="mech_cost_inc")
        mech_env_inc = st.number_input("Env Increase per Cycle", 0.0, 0.5, 0.08, 0.01, key="mech_env_inc")
        mech_int_inc = st.number_input("Integrity Increase per Cycle", 0.0, 0.01, 0.0005, 0.0001, key="mech_int_inc", format="%.4f")

# ============================================================================
# TAB 2: CHEMICAL RECYCLING PATHWAY
# ============================================================================

with tab2:
    st.header("Chemical Closed-Loop Recycling")
    st.markdown("*Advanced chemical recycling (solvolysis/depolymerization)*")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Virgin Production Stage")
        chem_virgin_cost = st.number_input("Virgin Cost ($/kg)", 0.0, 5.0, 1.20, 0.05, key="chem_v_cost")
        chem_virgin_env = st.number_input("Virgin Environmental", 0.0, 10.0, 3.5, 0.1, key="chem_v_env")
        chem_virgin_integrity = st.number_input("Virgin Integrity Loss", 0.0, 0.1, 0.0, 0.01, key="chem_v_int")
        chem_virgin_duration = st.number_input("Virgin Duration (years)", 0.0, 1.0, 0.0, 0.1, key="chem_v_dur")
        chem_virgin_mass = st.slider("Virgin Mass Fraction", 0.5, 1.0, 1.0, 0.01, key="chem_v_mass")

        st.subheader("Use Stage (Bottle)")
        chem_use_cost = st.number_input("Use Cost ($/kg)", 0.0, 1.0, 0.05, 0.01, key="chem_u_cost")
        chem_use_env = st.number_input("Use Environmental", 0.0, 1.0, 0.1, 0.01, key="chem_u_env")
        chem_use_integrity = st.slider("Use Integrity Loss", 0.0, 0.2, 0.015, 0.005, key="chem_u_int")
        chem_use_duration = st.number_input("Use Duration (years)", 0.0, 2.0, 0.3, 0.1, key="chem_u_dur")
        chem_use_mass = st.slider("Use Mass Fraction", 0.5, 1.0, 1.0, 0.01, key="chem_u_mass")

    with col2:
        st.subheader("Chemical Recycling Loop")
        chem_base_cost = st.number_input("Base Cost ($/kg)", 0.0, 10.0, 2.50, 0.1, key="chem_r_cost")
        chem_base_env = st.number_input("Base Environmental", 0.0, 10.0, 3.8, 0.1, key="chem_r_env")
        chem_base_integrity = st.slider("Base Integrity Loss", 0.0, 0.1, 0.012, 0.001, key="chem_r_int")
        chem_duration = st.number_input("Duration per Cycle (years)", 0.0, 2.0, 0.5, 0.1, key="chem_r_dur")
        chem_mass = st.slider("Mass Fraction per Cycle", 0.5, 1.0, 0.94, 0.01, key="chem_r_mass")

        st.markdown("**Per-Cycle Increases**")
        chem_cycles = st.number_input("Number of Cycles", 1, 50, 30, 1, key="chem_cycles")
        chem_cost_inc = st.number_input("Cost Increase per Cycle", 0.0, 0.5, 0.0, 0.01, key="chem_cost_inc")
        chem_env_inc = st.number_input("Env Increase per Cycle", 0.0, 0.5, 0.0, 0.01, key="chem_env_inc")
        chem_int_inc = st.number_input("Integrity Increase per Cycle", 0.0, 0.01, 0.0001, 0.0001, key="chem_int_inc", format="%.4f")

# ============================================================================
# TAB 3: DOWNCYCLING PATHWAY
# ============================================================================

with tab3:
    st.header("Downcycling to Carpet Fiber")
    st.markdown("*Single cascade recycling to low-grade fiber applications*")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Virgin Production Stage")
        down_virgin_cost = st.number_input("Virgin Cost ($/kg)", 0.0, 5.0, 1.20, 0.05, key="down_v_cost")
        down_virgin_env = st.number_input("Virgin Environmental", 0.0, 10.0, 3.5, 0.1, key="down_v_env")
        down_virgin_integrity = st.number_input("Virgin Integrity Loss", 0.0, 0.1, 0.0, 0.01, key="down_v_int")
        down_virgin_duration = st.number_input("Virgin Duration (years)", 0.0, 1.0, 0.0, 0.1, key="down_v_dur")
        down_virgin_mass = st.slider("Virgin Mass Fraction", 0.5, 1.0, 1.0, 0.01, key="down_v_mass")

        st.subheader("Use Stage (Bottle)")
        down_use_cost = st.number_input("Use Cost ($/kg)", 0.0, 1.0, 0.05, 0.01, key="down_u_cost")
        down_use_env = st.number_input("Use Environmental", 0.0, 1.0, 0.1, 0.01, key="down_u_env")
        down_use_integrity = st.slider("Use Integrity Loss", 0.0, 0.2, 0.03, 0.01, key="down_u_int")
        down_use_duration = st.number_input("Use Duration (years)", 0.0, 2.0, 0.3, 0.1, key="down_u_dur")
        down_use_mass = st.slider("Use Mass Fraction", 0.5, 1.0, 1.0, 0.01, key="down_u_mass")

    with col2:
        st.subheader("Downcycle to Fiber")
        down_base_cost = st.number_input("Downcycle Cost ($/kg)", 0.0, 5.0, 0.60, 0.05, key="down_r_cost")
        down_base_env = st.number_input("Downcycle Environmental", 0.0, 5.0, 2.0, 0.1, key="down_r_env")
        down_base_integrity = st.slider("Downcycle Integrity Loss", 0.0, 1.0, 0.60, 0.05, key="down_r_int")
        down_duration = st.number_input("Carpet Lifespan (years)", 1.0, 30.0, 15.0, 1.0, key="down_r_dur")
        down_mass = st.slider("Conversion Mass Fraction", 0.5, 1.0, 0.85, 0.01, key="down_r_mass")

        st.markdown("**Single Cycle (Terminal Application)**")
        st.info("Downcycling is a terminal application - material exits the closed-loop system.")

# ============================================================================
# TAB 4: VISUALIZATION SETTINGS
# ============================================================================

with tab4:
    st.header("3D Visualization Controls")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Display Options")
        show_triangles = st.checkbox("Show Triangle Frames", value=True)
        show_constraints = st.checkbox("Show Constraint Boundaries", value=False)
        show_labels = st.checkbox("Show Axis Labels", value=True)

    with col2:
        st.subheader("Camera Position")
        camera_x = st.slider("Camera X", 0.0, 3.0, 1.6, 0.1)
        camera_y = st.slider("Camera Y", 0.0, 3.0, 1.6, 0.1)
        camera_z = st.slider("Camera Z", 0.0, 2.0, 0.6, 0.1)

st.markdown("---")

# ============================================================================
# COMPUTATION SECTION
# ============================================================================

st.header("🔬 Pathway Analysis")

# Create assessment object

benchmarks = Benchmarks(
    cost_max=cost_benchmark_per_cycle, 
    environmental_max=env_benchmark_per_cycle,
    integrity_loss_max=integrity_benchmark_per_cycle
)

if enable_constraints:
    constraints = Constraints(
        cost_max=constraint_cost,
        environmental_max=constraint_env,
        integrity_min=constraint_integrity
    )
else:
    constraints = Constraints()

assessment = CircularityAssessment(benchmarks, constraints)

# Build pathways based on enabled checkboxes
pathways_built = []

try:
    if enable_mechanical:
        mech_stages = [
            LifecycleStage(
                name="Virgin PET Production",
                burdens=BurdenMetrics(mech_virgin_cost, mech_virgin_env, mech_virgin_integrity),
                duration=mech_virgin_duration,
                mass_fraction=mech_virgin_mass
            ),
            LifecycleStage(
                name="Bottle Use",
                burdens=BurdenMetrics(mech_use_cost, mech_use_env, mech_use_integrity),
                duration=mech_use_duration,
                mass_fraction=mech_use_mass
            ),
            LifecycleStage(
                name="Mechanical Recycling (Bottle-to-Bottle)",
                burdens=BurdenMetrics(mech_base_cost, mech_base_env, mech_base_integrity),
                duration=mech_duration,
                mass_fraction=mech_mass,
                cycles=mech_cycles,
                cost_increase_per_cycle=mech_cost_inc,
                env_increase_per_cycle=mech_env_inc,
                integrity_increase_per_cycle=mech_int_inc
            )
        ]
        assessment.add_pathway("Mechanical Closed-Loop", mech_stages)
        pathways_built.append("Mechanical Closed-Loop")

    if enable_chemical:
        chem_stages = [
            LifecycleStage(
                name="Virgin PET Production",
                burdens=BurdenMetrics(chem_virgin_cost, chem_virgin_env, chem_virgin_integrity),
                duration=chem_virgin_duration,
                mass_fraction=chem_virgin_mass
            ),
            LifecycleStage(
                name="Bottle Use",
                burdens=BurdenMetrics(chem_use_cost, chem_use_env, chem_use_integrity),
                duration=chem_use_duration,
                mass_fraction=chem_use_mass
            ),
            LifecycleStage(
                name="Chemical Recycling (Solvolysis)",
                burdens=BurdenMetrics(chem_base_cost, chem_base_env, chem_base_integrity),
                duration=chem_duration,
                mass_fraction=chem_mass,
                cycles=chem_cycles,
                cost_increase_per_cycle=chem_cost_inc,
                env_increase_per_cycle=chem_env_inc,
                integrity_increase_per_cycle=chem_int_inc
            )
        ]
        assessment.add_pathway("Chemical Closed-Loop", chem_stages)
        pathways_built.append("Chemical Closed-Loop")

    if enable_downcycle:
        down_stages = [
            LifecycleStage(
                name="Virgin PET Production",
                burdens=BurdenMetrics(down_virgin_cost, down_virgin_env, down_virgin_integrity),
                duration=down_virgin_duration,
                mass_fraction=down_virgin_mass
            ),
            LifecycleStage(
                name="Bottle Use",
                burdens=BurdenMetrics(down_use_cost, down_use_env, down_use_integrity),
                duration=down_use_duration,
                mass_fraction=down_use_mass
            ),
            LifecycleStage(
                name="Downcycle to Carpet Fiber",
                burdens=BurdenMetrics(down_base_cost, down_base_env, down_base_integrity),
                duration=down_duration,
                mass_fraction=down_mass,
                cycles=1
            )
        ]
        assessment.add_pathway("Downcycle to Carpet", down_stages)
        pathways_built.append("Downcycle to Carpet")

    if not pathways_built:
        st.warning("⚠️ No pathways enabled! Please select at least one pathway in the sidebar.")
    else:
        st.success(f"✅ {len(pathways_built)} pathway(s) computed successfully!")

        # Generate visualization
        visualizer = CircularityVisualizer(assessment)
        fig = visualizer.create_3d_ternary_plot(
            show_triangles=show_triangles,
            show_constraints=show_constraints,
            show_labels=show_labels,
            camera_eye={'x': camera_x, 'y': camera_y, 'z': camera_z}
        )

        # Display plot
        st.plotly_chart(fig, use_container_width=True)

        # Summary comparison table
        st.subheader("📊 Pathway Comparison Summary")

        comparison_data = []
        for pathway_name, pathway_result in assessment.pathways.items():
            summary = pathway_result.get_summary_table()
            comparison_data.append({
                'Pathway': pathway_name,
                'Duration (years)': f"{summary['Total Duration (years)']:.2f}",
                'Total Cycles': int(summary['Total Cycles']),
                'Total Cost ($/kg)': f"${summary['Total Cost ($/kg)']:.2f}",
                'Total Env (kg CO₂-eq/kg)': f"{summary['Total Environmental (kg CO2-eq/kg)']:.2f}",
                'Total Integrity Loss': f"{summary['Total Integrity Loss']:.3f}",
                'Cost Rate ($/kg/yr)': f"${summary['Cost Rate ($/kg/yr)']:.2f}",
                'Env Rate (kg CO₂-eq/kg/yr)': f"{summary['Environmental Rate (kg CO2-eq/kg/yr)']:.2f}"
            })

        comparison_df = pd.DataFrame(comparison_data)
        st.dataframe(comparison_df, use_container_width=True)

        # Export functionality
        st.subheader("📥 Export Results")
        csv = comparison_df.to_csv(index=False)
        st.download_button(
            label="Download Summary as CSV",
            data=csv,
            file_name="circular_economy_results.csv",
            mime="text/csv"
        )

except Exception as e:
    st.error(f"❌ Error during computation: {str(e)}")
    st.exception(e)

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; font-size: 12px;'>
    <p>Circular Economy Assessment Framework v1.0 | February 2026</p>
    <p>Built with Streamlit + Plotly</p>
</div>
""", unsafe_allow_html=True)
