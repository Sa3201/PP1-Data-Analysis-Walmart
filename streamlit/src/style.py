from __future__ import annotations

import plotly.graph_objects as go


BLUE = "#0071CE"
LIGHT_BLUE = "#76B7F2"
NAVY = "#12344D"
YELLOW = "#FFC220"
TEAL = "#2A9D8F"
CORAL = "#E76F51"
GRAY = "#728197"

PALETTE = [BLUE, NAVY, YELLOW, TEAL, CORAL, LIGHT_BLUE, GRAY]


def polish(fig: go.Figure, *, height: int = 430, legend: bool = True) -> go.Figure:
    fig.update_layout(
        height=height,
        margin=dict(l=25, r=25, t=75, b=95 if legend else 40),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(family="Arial", color=NAVY),
        title=dict(
            font=dict(family="Arial", size=20, color=NAVY),
            x=0.01,
            xanchor="left",
            y=0.97,
            yanchor="top",
        ),
        colorway=PALETTE,
        hoverlabel=dict(bgcolor="white", font_size=13),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.20,
            xanchor="center",
            x=0.5,
            title_text="",
        ),
        showlegend=legend,
    )
    fig.update_xaxes(showgrid=False, linecolor="#DFE6ED")
    fig.update_yaxes(gridcolor="#EAF0F5", zeroline=False)
    return fig


def money(value: float) -> str:
    value = float(value or 0)
    if abs(value) >= 1_000_000_000:
        return f"${value / 1_000_000_000:,.2f}B"
    if abs(value) >= 1_000_000:
        return f"${value / 1_000_000:,.1f}M"
    if abs(value) >= 1_000:
        return f"${value / 1_000:,.1f}K"
    return f"${value:,.0f}"
