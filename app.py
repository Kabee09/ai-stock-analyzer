import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import anthropic
from datetime import datetime, timedelta

# Page config
st.set_page_config(page_title="AI Stock Analyzer", page_icon="📈", layout="wide")

st.title("📈 AI Stock Analyzer")
st.markdown("*Powered by Claude AI + Real Market Data*")

# Sidebar
st.sidebar.header("Settings")
ticker = st.sidebar.text_input("Stock Ticker", value="AAPL").upper()
period = st.sidebar.selectbox("Time Period", ["1mo", "3mo", "6mo", "1y", "2y"], index=2)
api_key = st.sidebar.text_input("Anthropic API Key", type="password")

if st.sidebar.button("Analyze Stock 🚀"):
    if not api_key:
        st.error("Please enter your Anthropic API key in the sidebar.")
    else:
        with st.spinner(f"Fetching data for {ticker}..."):
            # Fetch stock data
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period)
            info = stock.info

            if hist.empty:
                st.error(f"Could not find data for ticker: {ticker}")
            else:
                # Key metrics
                col1, col2, col3, col4 = st.columns(4)
                current_price = hist['Close'].iloc[-1]
                start_price = hist['Close'].iloc[0]
                price_change = ((current_price - start_price) / start_price) * 100
                high = hist['High'].max()
                low = hist['Low'].min()

                col1.metric("Current Price", f"${current_price:.2f}")
                col2.metric("Period Return", f"{price_change:.2f}%", f"{price_change:.2f}%")
                col3.metric("Period High", f"${high:.2f}")
                col4.metric("Period Low", f"${low:.2f}")

                # Price chart
                st.subheader(f"{ticker} Price Chart")
                fig = go.Figure()
                fig.add_trace(go.Candlestick(
                    x=hist.index,
                    open=hist['Open'],
                    high=hist['High'],
                    low=hist['Low'],
                    close=hist['Close'],
                    name=ticker
                ))
                fig.update_layout(
                    xaxis_rangeslider_visible=False,
                    template="plotly_dark",
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)

                # Volume chart
                st.subheader("Volume")
                fig2 = go.Figure()
                fig2.add_trace(go.Bar(x=hist.index, y=hist['Volume'], name="Volume", marker_color='#00b4d8'))
                fig2.update_layout(template="plotly_dark", height=200)
                st.plotly_chart(fig2, use_container_width=True)

                # AI Analysis
                st.subheader("🤖 AI Analysis")
                with st.spinner("Claude is analyzing the stock..."):
                    client = anthropic.Anthropic(api_key=api_key)

                    prompt = f"""
                    Analyze this stock data for {ticker}:
                    - Company: {info.get('longName', ticker)}
                    - Sector: {info.get('sector', 'N/A')}
                    - Current Price: ${current_price:.2f}
                    - Period Return: {price_change:.2f}%
                    - Period High: ${high:.2f}
                    - Period Low: ${low:.2f}
                    - Market Cap: {info.get('marketCap', 'N/A')}
                    - P/E Ratio: {info.get('trailingPE', 'N/A')}
                    - 52 Week High: {info.get('fiftyTwoWeekHigh', 'N/A')}
                    - 52 Week Low: {info.get('fiftyTwoWeekLow', 'N/A')}

                    Provide a concise analysis covering:
                    1. Price trend and momentum
                    2. Key observations from the data
                    3. Potential risks to consider
                    4. Overall sentiment (Bullish/Neutral/Bearish) and why

                    Keep it clear, professional, and under 300 words.
                    """

                    message = client.messages.create(
                        model="claude-sonnet-4-5",
                        max_tokens=1024,
                        messages=[{"role": "user", "content": prompt}]
                    )

                    analysis = message.content[0].text
                    st.markdown(analysis)

                    sentiment = "🟢 Bullish" if price_change > 5 else "🔴 Bearish" if price_change < -5 else "🟡 Neutral"
                    st.info(f"**Market Sentiment:** {sentiment}")