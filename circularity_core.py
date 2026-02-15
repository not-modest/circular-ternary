"""
Circular Economy Assessment Framework - Core Module
===================================================

This module contains all the core data structures, mathematical models,
and visualization classes for circular economy lifecycle assessment
using 3D ternary burden-space representation.

Author: [Your Name]
Version: 1.0
Date: February 2026
"""

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass, field
from copy import deepcopy
import warnings

# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class BurdenMetrics:
    """Container for the three burden dimensions."""
    cost: float  # $/kg of material processed
    environmental: float  # kg CO2-eq/kg material
    integrity_loss: float  # 0-1 scale, where 1 = complete degradation

    def __post_init__(self):
        """Validate that all burdens are non-negative."""
        if self.cost < 0 or self.environmental < 0 or self.integrity_loss < 0:
            raise ValueError("All burden values must be non-negative")
        if self.integrity_loss > 1:
            raise ValueError("Integrity loss must be between 0 and 1")

    def to_array(self) -> np.ndarray:
        """Convert to numpy array for calculations."""
        return np.array([self.cost, self.environmental, self.integrity_loss])


@dataclass
class LifecycleStage:
    """Represents a single stage in the material lifecycle."""
    name: str
    burdens: BurdenMetrics
    duration: float  # years
    mass_fraction: float = 1.0
    cycles: int = 1
    cost_increase_per_cycle: float = 0.0
    env_increase_per_cycle: float = 0.0
    integrity_increase_per_cycle: float = 0.0

    def __post_init__(self):
        """Validate stage parameters."""
        if self.duration < 0:
            raise ValueError("Duration must be non-negative")
        if not 0 < self.mass_fraction <= 1:
            raise ValueError("Mass fraction must be between 0 and 1")
        if self.cycles < 1:
            raise ValueError("Cycles must be at least 1")


@dataclass
class Benchmarks:
    """Maximum burden values used for normalization."""
    cost_max: float
    environmental_max: float
    integrity_loss_max: float = 1.0
    cost_unit: str = "$/kg"
    environmental_unit: str = "kg CO2-eq/kg"
    integrity_unit: str = "fraction"

    def __post_init__(self):
        """Validate benchmark values."""
        if self.cost_max <= 0 or self.environmental_max <= 0:
            raise ValueError("Benchmark maxima must be positive")
        if self.integrity_loss_max <= 0 or self.integrity_loss_max > 1:
            raise ValueError("Integrity loss max must be between 0 and 1")

    def normalize(self, burdens: BurdenMetrics) -> np.ndarray:
        """Normalize burden values against benchmarks."""
        return np.array([
            burdens.cost / self.cost_max,
            burdens.environmental / self.environmental_max,
            burdens.integrity_loss / self.integrity_loss_max
        ])


@dataclass
class Constraints:
    """Operational constraints that define feasibility boundaries."""
    cost_max: Optional[float] = None
    environmental_max: Optional[float] = None
    integrity_min: Optional[float] = None

    def check_feasibility(self, burdens: BurdenMetrics) -> Dict[str, bool]:
        """Check if a stage meets all constraints."""
        feasibility = {}

        if self.cost_max is not None:
            feasibility['cost'] = burdens.cost <= self.cost_max

        if self.environmental_max is not None:
            feasibility['environmental'] = burdens.environmental <= self.environmental_max

        if self.integrity_min is not None:
            feasibility['integrity'] = (1 - burdens.integrity_loss) >= self.integrity_min

        return feasibility

    def is_feasible(self, burdens: BurdenMetrics) -> bool:
        """Check if all constraints are met."""
        feasibility = self.check_feasibility(burdens)
        return all(feasibility.values()) if feasibility else True


# ============================================================================
# TERNARY GEOMETRY
# ============================================================================

class TernaryGeometry:
    """Handles all mathematical operations for 3D ternary plot generation."""

    @staticmethod
    def normalize_ternary(a: float, b: float, c: float) -> Tuple[float, float, float]:
        """Normalize three values to sum to 1."""
        total = a + b + c
        if total == 0:
            return (1/3, 1/3, 1/3)
        return (a/total, b/total, c/total)

    @staticmethod
    def ternary_to_cartesian(a: float, b: float, c: float) -> Tuple[float, float]:
        """Convert normalized ternary coordinates to 2D Cartesian."""
        total = a + b + c
        a, b, c = a/total, b/total, c/total
        x = 0.5 * (2*b + c)
        y = (np.sqrt(3)/2) * c
        return (x, y)

    @staticmethod
    def create_scaled_triangle(
        normalized_burdens: np.ndarray,
        z_height: float,
        base_size: float = 1.0
    ) -> Dict[str, np.ndarray]:
        """Create an irregular triangle where each vertex scales independently."""
        vertices_base = np.array([
            [0.0, 0.0],
            [1.0, 0.0],
            [0.5, np.sqrt(3)/2],
            [0.0, 0.0]
        ])

        scale_factors = np.array([
            normalized_burdens[0],
            normalized_burdens[1],
            normalized_burdens[2],
            normalized_burdens[0]
        ])

        vertices_scaled = vertices_base * scale_factors[:, np.newaxis] * base_size

        x = vertices_scaled[:, 0]
        y = vertices_scaled[:, 1]
        z = np.full_like(x, z_height)

        return {'x': x, 'y': y, 'z': z}

    @staticmethod
    def calculate_trajectory_point(
        burdens: BurdenMetrics,
        benchmarks: Benchmarks,
        z_height: float
    ) -> Dict[str, float]:
        """Calculate the trajectory point within the ternary space."""
        normalized = benchmarks.normalize(burdens)

        a_rel, b_rel, c_rel = TernaryGeometry.normalize_ternary(
            burdens.cost,
            burdens.environmental,
            burdens.integrity_loss*10
        )

        cost_vertex_scaled = np.array([0.0, 0.0]) * normalized[0]
        env_vertex_scaled = np.array([1.0, 0.0]) * normalized[1]
        integrity_vertex_scaled = np.array([0.5, np.sqrt(3)/2]) * normalized[2]

        x = (a_rel * cost_vertex_scaled[0] + 
             b_rel * env_vertex_scaled[0] + 
             c_rel * integrity_vertex_scaled[0])

        y = (a_rel * cost_vertex_scaled[1] + 
             b_rel * env_vertex_scaled[1] + 
             c_rel * integrity_vertex_scaled[1])

        total_burden = burdens.cost + burdens.environmental + burdens.integrity_loss

        return {
            'x': x,
            'y': y,
            'z': z_height,
            'normalized_burdens': normalized,
            'total_burden': total_burden,
            'burden_magnitude': 1 / (total_burden + 0.001)
        }


# ============================================================================
# INTEGRITY MODEL
# ============================================================================

class IntegrityModel:
    """Comprehensive material integrity tracking."""

    @staticmethod
    def calculate_integrity(
        current_integrity_loss: float,
        base_degradation_rate: float,
        cycle_num: int,
        mass_fraction: float = 1.0
    ) -> dict:
        """Calculate comprehensive integrity metrics for a recycling cycle."""
        remaining_quality = max(0, 1.0 - current_integrity_loss)
        new_remaining_quality = remaining_quality * (1.0 - base_degradation_rate) * mass_fraction
        new_integrity_loss = min(1.0, max(0, 1.0 - new_remaining_quality))
        quality_score = new_remaining_quality * 100
        grade, grade_name, grade_color = IntegrityModel.get_material_grade(new_integrity_loss)
        is_recyclable = quality_score >= 10.0

        return {
            'integrity_loss': new_integrity_loss,
            'remaining_quality': new_remaining_quality,
            'quality_score': quality_score,
            'grade': grade,
            'grade_name': grade_name,
            'grade_color': grade_color,
            'is_recyclable': is_recyclable,
            'degradation_rate': base_degradation_rate,
            'cycles_processed': cycle_num + 1
        }

    @staticmethod
    def get_material_grade(integrity_loss: float) -> tuple:
        """Classify material into industry-standard grades."""
        if integrity_loss < 0.15:
            return 'A', 'Virgin-Equivalent', '#2ECC71'
        elif integrity_loss < 0.40:
            return 'B', 'Food-Safe', '#3498DB'
        elif integrity_loss < 0.70:
            return 'C', 'General Packaging', '#F39C12'
        elif integrity_loss < 0.90:
            return 'D', 'Fiber/Textile', '#E74C3C'
        else:
            return 'E', 'End-of-Life', '#95A5A6'


# ============================================================================
# PATHWAY RESULT
# ============================================================================

@dataclass
class PathwayResult:
    """Contains all calculated metrics and geometry for a complete pathway."""
    name: str
    stages: List[LifecycleStage]
    trajectory_coords: List[Dict]
    triangle_coords: List[Dict]
    cumulative_time: np.ndarray
    cumulative_cost: np.ndarray
    cumulative_environmental: np.ndarray
    cumulative_integrity_loss: np.ndarray
    total_duration: float
    total_cycles: int
    average_burden_rate: Dict[str, float]
    feasibility_flags: List[Dict]

    def get_summary_table(self) -> Dict[str, float]:
        """Generate summary statistics for comparison."""
        return {
            'Total Duration (years)': self.total_duration,
            'Total Cycles': self.total_cycles,
            'Total Cost ($/kg)': self.cumulative_cost[-1],
            'Total Environmental (kg CO2-eq/kg)': self.cumulative_environmental[-1],
            'Total Integrity Loss': self.cumulative_integrity_loss[-1],
            'Cost Rate ($/kg/yr)': self.average_burden_rate['cost'],
            'Environmental Rate (kg CO2-eq/kg/yr)': self.average_burden_rate['environmental'],
            'Integrity Loss Rate (/yr)': self.average_burden_rate['integrity']
        }


# ============================================================================
# CIRCULARITY ASSESSMENT ENGINE
# ============================================================================

class CircularityAssessment:
    """Main assessment engine for circular economy lifecycle analysis."""

    def __init__(
        self,
        benchmarks: Benchmarks,
        constraints: Optional[Constraints] = None,
        waste_management_burdens: Optional[BurdenMetrics] = None
    ):
        """Initialize the assessment framework."""
        self.benchmarks = benchmarks
        self.constraints = constraints or Constraints()
        self.waste_management = waste_management_burdens or BurdenMetrics(
            cost=0.05,
            environmental=0.5,
            integrity_loss=1.0
        )
        self.pathways: Dict[str, PathwayResult] = {}

    def add_pathway(
        self,
        name: str,
        stages: List[LifecycleStage]
    ) -> PathwayResult:
        """Add a pathway for analysis."""
        if not stages:
            raise ValueError("Pathway must have at least one stage")

        result = self._calculate_pathway_trajectory(name, stages)
        self.pathways[name] = result
        return result

    def _calculate_pathway_trajectory(
        self,
        name: str,
        stages: List[LifecycleStage]
    ) -> PathwayResult:
        """Calculate complete trajectory through burden-space for a pathway."""
        trajectory_coords = []
        triangle_coords = []
        time_points = []
        cost_cumulative = []
        env_cumulative = []
        integrity_cumulative = []
        feasibility_flags = []

        current_time = 0.0
        current_cost = 0.0
        current_env = 0.0
        current_integrity = 0.0
        total_cycles = 0

        for stage in stages:
            for cycle_num in range(stage.cycles):
                total_cycles += 1
                effective_mass = stage.mass_fraction
                stage_time = current_time + stage.duration

                cycle_cost = stage.burdens.cost + (cycle_num * stage.cost_increase_per_cycle)
                cycle_env = stage.burdens.environmental + (cycle_num * stage.env_increase_per_cycle)
                adjusted_degradation_rate = (
                    stage.burdens.integrity_loss + 
                    (cycle_num * stage.integrity_increase_per_cycle)
                )

                integrity_data = IntegrityModel.calculate_integrity(
                    current_integrity_loss=current_integrity,
                    base_degradation_rate=adjusted_degradation_rate,
                    cycle_num=cycle_num,
                    mass_fraction=effective_mass
                )
                cycle_integrity = integrity_data['integrity_loss']
                stage_integrity = cycle_integrity

                if not integrity_data['is_recyclable']:
                    print(f"⚠️ {stage.name} Cycle {cycle_num + 1}: Material quality too low!")
                    print(f"   Quality Score: {integrity_data['quality_score']:.1f}%")
                    print(f"   Grade: {integrity_data['grade']} ({integrity_data['grade_name']})")
                    print(f"   Pathway terminated.")
                    break

                stage_cost = current_cost + (cycle_cost * effective_mass)
                stage_env = current_env + (cycle_env * effective_mass)

                point_burdens = BurdenMetrics(
                    cost=cycle_cost,
                    environmental=cycle_env,
                    integrity_loss=cycle_integrity
                )

                point = TernaryGeometry.calculate_trajectory_point(
                    point_burdens,
                    self.benchmarks,
                    z_height=stage_time
                )

                point['stage_name'] = f"{stage.name} (Cycle {cycle_num + 1})" if stage.cycles > 1 else stage.name
                point['cycle_number'] = cycle_num + 1
                point['cumulative_cost'] = stage_cost
                point['cumulative_environmental'] = stage_env
                point['cumulative_integrity_loss'] = stage_integrity
                point['quality_score'] = integrity_data['quality_score']
                point['remaining_quality'] = integrity_data['remaining_quality']
                point['material_grade'] = integrity_data['grade']
                point['grade_name'] = integrity_data['grade_name']
                point['grade_color'] = integrity_data['grade_color']
                point['is_recyclable'] = integrity_data['is_recyclable']
                trajectory_coords.append(point)

                degraded_burdens_for_triangle = BurdenMetrics(
                    cost=cycle_cost,
                    environmental=cycle_env,
                    integrity_loss=cycle_integrity
                )
                
                normalized_degraded = self.benchmarks.normalize(degraded_burdens_for_triangle)
                
                triangle = TernaryGeometry.create_scaled_triangle(
                    normalized_degraded,
                    z_height=stage_time
                )
                triangle['stage_name'] = point['stage_name']
                triangle_coords.append(triangle)

                time_points.append(stage_time)
                cost_cumulative.append(stage_cost)
                env_cumulative.append(stage_env)
                integrity_cumulative.append(stage_integrity)

                feasibility = self.constraints.check_feasibility(point_burdens)
                feasibility_flags.append({
                    'stage': point['stage_name'],
                    'time': stage_time,
                    'feasibility': feasibility,
                    'is_feasible': all(feasibility.values()) if feasibility else True
                })

                current_time = stage_time
                current_cost = stage_cost
                current_env = stage_env
                current_integrity = stage_integrity

        if current_time > 0:
            cost_rate = current_cost / current_time
            env_rate = current_env / current_time
            integrity_rate = current_integrity / current_time
        else:
            cost_rate = env_rate = integrity_rate = 0.0

        result = PathwayResult(
            name=name,
            stages=stages,
            trajectory_coords=trajectory_coords,
            triangle_coords=triangle_coords,
            cumulative_time=np.array(time_points),
            cumulative_cost=np.array(cost_cumulative),
            cumulative_environmental=np.array(env_cumulative),
            cumulative_integrity_loss=np.array(integrity_cumulative),
            total_duration=current_time,
            total_cycles=total_cycles,
            average_burden_rate={
                'cost': cost_rate,
                'environmental': env_rate,
                'integrity': integrity_rate
            },
            feasibility_flags=feasibility_flags
        )

        return result


# ============================================================================
# VISUALIZATION ENGINE
# ============================================================================

class CircularityVisualizer:
    """Professional-grade visualization engine for circular economy assessment."""

    PATHWAY_COLORS = [
        '#EF553B', '#00CC96', '#AB63FA',
        '#FFA15A', '#19D3F3', '#FF6692'
    ]

    def __init__(self, assessment: CircularityAssessment):
        """Initialize visualizer with assessment data."""
        self.assessment = assessment
        self.fig_3d = None
        self.fig_2d = None

    def create_3d_ternary_plot(
        self,
        show_triangles: bool = True,
        show_constraints: bool = True,
        show_labels: bool = True,
        camera_eye: Optional[Dict] = None
    ) -> go.Figure:
        """Generate the main 3D ternary burden-space visualization."""
        fig = go.Figure()

        if camera_eye is None:
            camera_eye = {'x': 1.6, 'y': 1.6, 'z': 0.6}

        z_min, z_max = 0, 0

        for pathway_idx, (pathway_name, pathway_result) in enumerate(self.assessment.pathways.items()):
            color = self.PATHWAY_COLORS[pathway_idx % len(self.PATHWAY_COLORS)]
            z_max = max(z_max, pathway_result.total_duration)

            if show_triangles:
                self._add_triangle_frames(fig, pathway_result, pathway_idx)

            self._add_trajectory_line(fig, pathway_result, color)

        if show_triangles:
            fig.add_trace(go.Scatter3d(
                x=[None], y=[None], z=[None],
                mode='lines',
                line=dict(color='rgba(52, 152, 219, 1)', width=3),
                name='─ Cost Edge',
                showlegend=True
            ))
            fig.add_trace(go.Scatter3d(
                x=[None], y=[None], z=[None],
                mode='lines',
                line=dict(color='rgba(46, 204, 113, 1)', width=3),
                name='─ Environmental Edge',
                showlegend=True
            ))
            fig.add_trace(go.Scatter3d(
                x=[None], y=[None], z=[None],
                mode='lines',
                line=dict(color='rgba(230, 126, 34, 1)', width=3),
                name='─ Integrity Edge',
                showlegend=True
            ))

        if show_labels:
            self._add_axis_labels(fig, z_max)

        fig.update_layout(
            title={
                'text': "Circular Economy Lifecycle Assessment: 3D Ternary Burden-Space",
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 16, 'family': 'Arial, sans-serif','color': '#2C3E50'}
            },
            scene=dict(
                xaxis=dict(visible=False, showgrid=False, range=[-0.1, 1.1]),
                yaxis=dict(visible=False, showgrid=False, range=[-0.1, 1.0]),
                zaxis=dict(
                    title=dict(text='Cumulative Time (years)', font=dict(size=14, color='#2C3E50')),
                    gridcolor='rgba(200, 200, 200, 0.3)',
                    showbackground=True,
                    backgroundcolor='rgba(240, 240, 240, 0.5)',
                    range=[z_min - 0.5, z_max + 0.5]
                ),
                aspectratio=dict(x=1, y=1, z=1.5),
                camera=dict(eye=camera_eye),
                bgcolor='rgba(245, 245, 245, 0.9)'
            ),
            margin=dict(l=0, r=0, b=0, t=60),
            showlegend=True,
            legend=dict(
                x=1.02, y=0.98,
                xanchor='left', yanchor='top',
                bgcolor='rgba(255, 255, 255, 0.9)',
                bordercolor='rgba(0, 0, 0, 0.3)',
                borderwidth=1,
                font=dict(color='#2C3E50')
            ),
            paper_bgcolor='white',
            font=dict(family='Arial, sans-serif', size=11, color='#2C3E50')
        )

        self.fig_3d = fig
        return fig

    def _add_triangle_frames(
        self,
        fig: go.Figure,
        pathway: PathwayResult,
        pathway_idx: int
    ):
        """Add triangle frames to show burden-space at each stage."""
        for tri_idx, triangle in enumerate(pathway.triangle_coords):
            base_opacity = 0.3 + 0.5 * (tri_idx / max(1, len(pathway.triangle_coords) - 1))

            x_coords = triangle['x']
            y_coords = triangle['y']
            z_coords = triangle['z']

            fig.add_trace(go.Scatter3d(
                x=[x_coords[0], x_coords[1]],
                y=[y_coords[0], y_coords[1]],
                z=[z_coords[0], z_coords[1]],
                mode='lines',
                line=dict(color='rgba(52, 152, 219, 1)', width=3),
                opacity=base_opacity,
                name=f"{pathway.name} - Cost edge",
                showlegend=False,
                hoverinfo='text',
                hovertext=f"Cost Burden Edge<br>Stage: {triangle['stage_name']}<br>Time: {z_coords[0]:.2f} yrs"
            ))

            fig.add_trace(go.Scatter3d(
                x=[x_coords[1], x_coords[2]],
                y=[y_coords[1], y_coords[2]],
                z=[z_coords[1], z_coords[2]],
                mode='lines',
                line=dict(color='rgba(46, 204, 113, 1)', width=3),
                opacity=base_opacity,
                name=f"{pathway.name} - Env edge",
                showlegend=False,
                hoverinfo='text',
                hovertext=f"Environmental Burden Edge<br>Stage: {triangle['stage_name']}<br>Time: {z_coords[0]:.2f} yrs"
            ))

            fig.add_trace(go.Scatter3d(
                x=[x_coords[2], x_coords[3]],
                y=[y_coords[2], y_coords[3]],
                z=[z_coords[2], z_coords[3]],
                mode='lines',
                line=dict(color='rgba(230, 126, 34, 1)', width=3),
                opacity=base_opacity,
                name=f"{pathway.name} - Integrity edge",
                showlegend=False,
                hoverinfo='text',
                hovertext=f"Integrity Loss Edge<br>Stage: {triangle['stage_name']}<br>Time: {z_coords[0]:.2f} yrs"
            ))

    def _add_trajectory_line(
        self,
        fig: go.Figure,
        pathway: PathwayResult,
        color: str
    ):
        """Add the main trajectory line connecting all stages."""
        x_coords = [p['x'] for p in pathway.trajectory_coords]
        y_coords = [p['y'] for p in pathway.trajectory_coords]
        z_coords = [p['z'] for p in pathway.trajectory_coords]

        marker_sizes = [5] * len(pathway.trajectory_coords)
        total_burdens = [p['total_burden'] for p in pathway.trajectory_coords]

        hover_texts = []
        for point in pathway.trajectory_coords:
            text = (
                f"{point['stage_name']}<br>"
                f"Time: {point['z']:.2f} years<br>"
                f"Cycle: {point['cycle_number']}<br>"
                f"<b>Cumulative:</b><br>"
                f"Total Cost: ${point['cumulative_cost']:.2f}/kg<br>"
                f"Total Environmental: {point['cumulative_environmental']:.2f} kg CO2-eq/kg<br>"
                f"Total Integrity Loss: {point['cumulative_integrity_loss']:.3f}"
            )
            hover_texts.append(text)

        fig.add_trace(go.Scatter3d(
            x=x_coords,
            y=y_coords,
            z=z_coords,
            mode='lines+markers',
            name=pathway.name,
            line=dict(color=color, width=2),
            marker=dict(
                size=marker_sizes,
                color=total_burdens,
                colorscale='RdYlGn_r',
                line=dict(color='white', width=1.5),
                opacity=0.95,
                showscale=True,
                colorbar=dict(
                    title="Total Burden",
                    titleside='top',
                    x=0.5,              # Center horizontally
                    y=-0.15,            # Position below plot
                    xanchor='center',   # Center anchor
                    yanchor='top',      # Top anchor
                    orientation='h',    # Horizontal orientation
                    thickness=15,
                    len=0.5,            # Length (50% of plot width)
                    titlefont=dict(color='#2C3E50'),
                    tickfont=dict(color='#2C3E50')
                )
            ),
            hoverinfo='text',
            hovertext=hover_texts
        ))

    def _add_axis_labels(self, fig: go.Figure, z_max: float):
        """Add labels for the three ternary axes."""
        label_offset = -0.08

        labels = [
            {'text': 'Cost Burden<br>($/kg)', 'x': 0, 'y': label_offset, 'z': 0},
            {'text': 'Environmental Burden<br>(kg CO₂-eq/kg)', 'x': 1, 'y': label_offset, 'z': 0},
            {'text': 'Integrity Loss<br>(Material Quality)', 'x': 0.5, 'y': np.sqrt(3)/2 + 0.15, 'z': 0}
        ]

        for label in labels:
            fig.add_trace(go.Scatter3d(
                x=[label['x']],
                y=[label['y']],
                z=[label['z']],
                mode='text',
                text=[label['text']],
                textfont=dict(size=12, color='black', family='Arial Black'),
                showlegend=False,
                hoverinfo='none'
            ))
