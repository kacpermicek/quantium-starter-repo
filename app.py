from pathlib import Path
import pandas as pd
from dash import Dash, html, dcc, Input, Output, callback
import plotly.express as px

CUT_OFF = pd.Timestamp("2021-01-15")
CSV_PATH = Path("data/processed/pink_morsels_sales.csv")

# --- load & tidy ---
df = pd.read_csv(CSV_PATH)
df.columns = [c.strip().title() for c in df.columns]   # handle Sales/Date/Region case
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df = df.dropna(subset=["Date", "Sales"])
df = df.sort_values("Date")

regions = ["All regions"] + sorted(r for r in df["Region"].dropna().unique())

def daily_series(_df):
    return _df.groupby("Date", as_index=False)["Sales"].sum().sort_values("Date")

def make_fig(series):
    import plotly.express as px
    fig = px.line(series, x="Date", y="Sales")
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Sales",
        margin=dict(l=40, r=20, t=20, b=40),
    )

    cutoff = CUT_OFF.to_pydatetime()  # plain datetime object

    # vertical cutoff line without timestamp arithmetic
    fig.add_shape(
        type="line",
        x0=cutoff, x1=cutoff, xref="x",
        y0=0, y1=1, yref="paper",
        line=dict(dash="dash")
    )
    fig.add_annotation(
        x=cutoff, xref="x",
        y=1, yref="paper",
        text="Price increase (15 Jan 2021)",
        showarrow=False, xanchor="left", yanchor="bottom"
    )
    return fig


def verdict_text(series):
    before = series.loc[series["Date"] < CUT_OFF, "Sales"].sum()
    after  = series.loc[series["Date"] >= CUT_OFF, "Sales"].sum()
    if before == 0 or after == 0:
        missing = "after" if after == 0 else "before"
        note = f" Note: no data {missing} the cutoff in this selection."
    else:
        note = ""
    if after > before:
        which = "higher after the price increase"
    elif after < before:
        which = "higher before the price increase"
    else:
        which = "equal before and after the price increase"
    return (f"Total sales before: £{before:,.2f} · after: £{after:,.2f}. "
            f"Sales were {which}.{note}")

# --- Dash app ---
app = Dash(__name__)
app.title = "Pink Morsel Sales"
server = app.server

app.layout = html.Div([
    html.H1("Pink Morsel Sales Over Time"),
    html.Div([
        html.Label("Filter by region:"),
        dcc.Dropdown(
            id="region-dd",
            options=[{"label": r.title(), "value": r} for r in regions],
            value="All regions",
            clearable=False,
            style={"maxWidth": 300}
        ),
    ], style={"marginBottom": "1rem"}),
    dcc.Graph(id="sales-chart"),
    html.P(id="summary", style={"fontWeight": "500"})
], style={"maxWidth": "900px", "margin": "0 auto", "padding": "1rem"})

@callback(
    Output("sales-chart", "figure"),
    Output("summary", "children"),
    Input("region-dd", "value")
)
def update(region_value):
    if region_value == "All regions":
        dff = df.copy()
    else:
        dff = df[df["Region"] == region_value]
    series = daily_series(dff)
    return make_fig(series), verdict_text(series)

if __name__ == "__main__":
    app.run(debug=True)

