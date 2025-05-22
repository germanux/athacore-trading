# tests/test_market_data.py

from athacore.core.data.market_data_alpha_vantage import get_price_data

def test_get_price_data():
    df = get_price_data('AAPL', period='5d')
    assert not df.empty
    assert 'Close' in df.columns
