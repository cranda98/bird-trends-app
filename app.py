import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import numpy as np

# Load data
trends = pd.read_csv("data/species_trend_predictions.csv")
df = pd.read_csv("data/ebd_MI_threecounties.csv")

# Preprocess
df["OBSERVATION DATE"] = pd.to_datetime(df["OBSERVATION DATE"], errors="coerce")
df["OBSERVATION COUNT"] = pd.to_numeric(df["OBSERVATION COUNT"], errors="coerce")
df["DURATION MINUTES"] = pd.to_numeric(df["DURATION MINUTES"], errors="coerce")
df["NUMBER OBSERVERS"] = pd.to_numeric(df["NUMBER OBSERVERS"], errors="coerce")

df = df[(df["ALL SPECIES REPORTED"] == 1)]
df = df[(df["DURATION MINUTES"] >= 5) & (df["DURATION MINUTES"] <= 180)]
df = df[df["NUMBER OBSERVERS"] <= 5]
df = df[df["OBSERVATION COUNT"] > 0]

df["year"] = df["OBSERVATION DATE"].dt.year

species_options = sorted(df['COMMON NAME'].dropna().unique())
county_options = sorted(df['COUNTY'].dropna().unique())

# Dash app
app = dash.Dash(__name__)
app.title = "MI Bird Trends"

app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap" rel="stylesheet">
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

app.layout = html.Div([
    html.H1("🪶 Michigan Bird Species Trends by County", style={"marginBottom": "20px"}),

    html.Div([
        html.Div([
            html.Label("Select County:", style={"fontWeight": "bold"}),
            dcc.Dropdown(id='county', options=[{'label': c, 'value': c} for c in county_options], value='Ingham')
        ], style={"padding": "15px", "backgroundColor": "#f9f9f9", "borderRadius": "8px", "boxShadow": "0 1px 3px rgba(0,0,0,0.1)", "marginBottom": "10px", "width": "45%", "display": "inline-block", "marginRight": "5%"}),

        html.Div([
            html.Label("Select Species:", style={"fontWeight": "bold"}),
            dcc.Dropdown(id='species', options=[{'label': s, 'value': s} for s in species_options], value='Red-winged Blackbird')
        ], style={"padding": "15px", "backgroundColor": "#f9f9f9", "borderRadius": "8px", "boxShadow": "0 1px 3px rgba(0,0,0,0.1)", "width": "45%", "display": "inline-block"}),
    ], style={"marginBottom": "20px"}),

    dcc.Loading(dcc.Graph(id='trend-plot'), type="circle"),
    dcc.Loading(html.Div(id='trend-summary', style={"marginTop": "20px"}), type="default")
], style={"fontFamily": "'Inter', 'Segoe UI', 'Roboto', sans-serif", "margin": "30px"})

@app.callback(
    [Output('trend-plot', 'figure'),
     Output('trend-summary', 'children')],
    [Input('county', 'value'),
     Input('species', 'value')]
)
def update_plot(county, species):
    sub_obs = df[(df['COUNTY'] == county) & (df['COMMON NAME'] == species)]
    sub_pred = trends[(trends['COUNTY'] == county) & (trends['COMMON NAME'] == species)]

    if sub_obs.empty:
        return go.Figure(), f"No data for {species} in {county}."

    obs_by_year = sub_obs.groupby("year")["OBSERVATION COUNT"].sum().reset_index()
    obs_by_year = obs_by_year[obs_by_year["OBSERVATION COUNT"] >= 5]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=obs_by_year["year"],
        y=obs_by_year["OBSERVATION COUNT"],
        mode='lines+markers',
        name="Observed Count",
        line=dict(color='blue'),
        hovertemplate='Year: %{x}<br>Count: %{y}<extra></extra>'
    ))

    # Summary stats
    avg = int(obs_by_year["OBSERVATION COUNT"].mean())
    peak_year = int(obs_by_year.loc[obs_by_year["OBSERVATION COUNT"].idxmax(), "year"])
    slope = np.polyfit(obs_by_year["year"], obs_by_year["OBSERVATION COUNT"], 1)[0]
    trend_icon = "📈" if slope > 0.05 else ("📉" if slope < -0.05 else "➡️")
    trend_label = "Increasing" if slope > 0.05 else ("Decreasing" if slope < -0.05 else "Stable")

    # Start with summary
    summary = [
        html.H4("Trend Summary"),
        html.P(f"Avg sightings/year: {avg}"),
        html.P(f"Peak year: {peak_year}"),
        html.P(f"Trend: {trend_icon} {trend_label}")
    ]

    # If model prediction is valid, add to plot and summary
    pred_only = sub_pred[sub_pred['model_r2'].notnull()]
    if not pred_only.empty:
        r2 = pred_only['model_r2'].values[0]
        pval = pred_only['model_p_value'].values[0]
        n_years = pred_only['n_years_fit'].values[0]
        if n_years >= 4 and r2 >= 0.2:
            fig.add_trace(go.Scatter(
                x=pred_only["year"], y=pred_only["predicted_count"],
                mode='lines', name="Predicted Count", line=dict(color='red'),
                hovertemplate='Year: %{x}<br>Predicted: %{y:.0f}<extra></extra>'
            ))
            fig.add_trace(go.Scatter(
                x=pred_only["year"], y=pred_only["predicted_ci_upper"],
                mode='lines', line=dict(width=0), showlegend=False
            ))
            fig.add_trace(go.Scatter(
                x=pred_only["year"], y=pred_only["predicted_ci_lower"],
                mode='lines', fill='tonexty', fillcolor='rgba(200,100,100,0.2)',
                line=dict(width=0), showlegend=False
            ))
            summary.append(html.P(f"Model R²: {r2:.2f}, p-value: {pval:.3f}, Years Fit: {n_years}"))
        else:
            summary.append(html.P("⚠️ Prediction model too weak to display."))

    fig.update_layout(
        title=dict(text=f"{species} in {county} — Observed vs Predicted", x=0.5),
        xaxis=dict(title="Year", dtick=1),
        yaxis=dict(title="Count", rangemode="tozero"),
        plot_bgcolor="white",
        font=dict(family="Inter", size=14)
    )

    return fig, html.Div(summary)

if __name__ == '__main__':
    app.run(debug=True)
