from pathlib import Path
import pandas as pd
from dash import Dash, html, dcc, Input, Output
import plotly.express as px

CUT_OFF = pd.Timestamp("2021-01-15")
CSV_PATH = Path("data/processed/pink_morsels_sales.csv")

# --- load & tidy ---
df = pd.read_csv(CSV_PATH)
df.columns = [c.strip().title() for c in df.columns]   # Sales/Date/Region
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df = df.dropna(subset=["Date", "Sales"]).sort_values("Date")

def daily_series(_df):
    return _df.groupby("Date", as_index=False)["Sales"].sum().sort_values("Date")

def make_fig(series):
    fig = px.line(series, x="Date", y="Sales")
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Sales (£)",
        margin=dict(l=40, r=20, t=10, b=40),
        plot_bgcolor="white",
        paper_bgcolor="white",
    )
    cutoff = CUT_OFF.to_pydatetime()
    fig.add_shape(type="line", x0=cutoff, x1=cutoff, xref="x",
                  y0=0, y1=1, yref="paper", line=dict(dash="dash"))
    fig.add_annotation(x=cutoff, xref="x", y=1, yref="paper",
                       text="Price increase (15 Jan 2021)",
                       showarrow=False, xanchor="left", yanchor="bottom")
    return fig

def verdict_text(series):
    before = series.loc[series["Date"] < CUT_OFF, "Sales"].sum()
    after  = series.loc[series["Date"] >= CUT_OFF, "Sales"].sum()
    if after > before:
        v = "higher after the price increase"
    elif after < before:
        v = "higher before the price increase"
    else:
        v = "equal before and after the price increase"
    return f"Total before: £{before:,.2f} · after: £{after:,.2f} — Sales were {v}."

app = Dash(__name__)
app.title = "Pink Morsel Sales"
server = app.server

regions = ["all", "north", "east", "south", "west"]

app.layout = html.Div(
    className="container",
    children=[
        html.H1("Pink Morsel Sales Over Time", className="title"),
        html.Div(
            className="controls",
            children=[
                html.Label("Region", className="label"),
                dcc.RadioItems(
                    id="region-radio",
                    options=[{"label": r.capitalize(), "value": r} for r in regions],
                    value="all",
                    inline=True,
                    className="radio-group",
                ),
            ],
        ),
        dcc.Graph(id="sales-chart", className="card"),
        html.P(id="summary", className="summary"),
    ],
)

@app.callback(
    Output("sales-chart", "figure"),
    Output("summary", "children"),
    Input("region-radio", "value"),
)
def update(region_value):
    if region_value == "all":
        dff = df
    else:
        dff = df[df["Region"].str.lower() == region_value]
    series = daily_series(dff)
    return make_fig(series), verdict_text(series)

if __name__ == "__main__":
    app.run(debug=True)
