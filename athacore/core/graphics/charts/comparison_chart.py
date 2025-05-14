# Gráfica comparativa VC
import yfinance as yf
from flask import Flask, request, jsonify
import plotly.graph_objects as go

app = Flask(__name__)

def build_volume_comparison_chart_multiple(activos_dfs, period_start, period_end):
    fig = go.Figure()
    colores = ["blue", "red", "green", "orange", "purple", "cyan", "magenta", "lime", "brown", "pink"]

    for idx, (activo, df) in enumerate(activos_dfs):
        color = colores[idx % len(colores)]
        fig.add_trace(go.Scatter(
            x=df["Date"],
            y=df["Volume"],
            mode='lines+markers',
            name=f'{activo} ({period_start} a {period_end})',
            line=dict(color=color, width=2),
            marker=dict(size=4)
        ))

    fig.update_layout(
        title="Comparación de Volumen de Múltiples Activos",
        xaxis_title="Fecha",
        yaxis_title="Volumen",
        template='plotly_white',
        xaxis=dict(type="date", tickformat="%b %d\n%Y", showgrid=True),
        yaxis=dict(showgrid=True),
        hovermode="x unified",
        legend=dict(orientation="h", y=-0.2, x=0.5, xanchor="center")
    )
    return fig

@app.route('/get-comparison', methods=['POST'])
def get_comparison():
    data = request.json
    tickers = data.get('tickers')
    start_date = data.get('start_date')
    end_date = data.get('end_date')

    if not tickers or not start_date or not end_date:
        return jsonify({'error': 'Datos incompletos'}), 400

    activos_dfs = []
    for ticker in tickers:
        try:
            stock = yf.download(ticker, start=start_date, end=end_date)
            if stock.empty:
                continue
            df = stock.reset_index()
            activos_dfs.append((ticker, df))
        except Exception as e:
            return jsonify({'error': f'Error al obtener datos de {ticker}: {str(e)}'}), 500

    if not activos_dfs:
        return jsonify({'error': 'No se encontraron datos para los activos seleccionados.'}), 400

    try:
        fig = build_volume_comparison_chart_multiple(activos_dfs, start_date, end_date)
        return jsonify(fig.to_dict())
    except Exception as e:
        return jsonify({'error': f'Error al construir la gráfica: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)



