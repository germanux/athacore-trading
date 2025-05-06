# tests/test_market_data.py

from core.data.market_data import get_price_data

def test_get_price_data():
    df = get_price_data('AAPL', period='5d')
    assert not df.empty
    assert 'Close' in df.columns
