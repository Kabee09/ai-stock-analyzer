import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import anthropic
from datetime import datetime, timedelta
import time
import pandas as pd
from prophet import Prophet

# Page config
st.set_page_config(page_title="AI Stock Analyzer", page_icon="📈", layout="wide")

st.title("📈 AI Stock Analyzer")
st.markdown("*Powered by Claude AI + Real Market Data + ML Predictions*")

# Sidebar
st.sidebar.header("Settings")
ticker = st.sidebar.text_input("Stock Ticker", value="AAPL").upper()
period = st.sidebar.selectbox("Time Period", ["1mo", "3mo", "6mo", "1y", "2y"], index=2)
forecast_days = st.sidebar.slider("Forecast Days", 7, 90, 30)
api_key = st.sidebar.text_input("Anthropic API Key", type="password")

if st.sidebar.button("Analyze Stock 🚀"):
    if not api_key:
        st.error("Please enter your Anthropic API key in the sidebar.")
    else:
        with st.spinner(f"Fetching data for {ticker}..."):
            time.sleep(2)
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period, auto_adjust=True, timeout=30)
            try:
                info = stock.info
            except:
                info = {}

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

                # ML Prediction
                st.subheader(f"🤖 ML Price Prediction — Next {forecast_days} Days")
                with st.spinner("Running Prophet forecasting model..."):
                    try:
                        # Prepare data for Prophet
                        df_prophet = hist[['Close']].reset_index()
                        df_prophet.columns = ['ds', 'y']
                        df_prophet['ds'] = pd.to_datetime(df_prophet['ds']).dt.tz_localize(None)

                        # Train Prophet model
                        model = Prophet(daily_seasonality=True, yearly_seasonality=True)
                        model.fit(df_prophet)

                        # Make future predictions
                        future = model.make_future_dataframe(periods=forecast_days)
                        forecast = model.predict(future)

                        # Plot prediction
                        fig3 = go.Figure()

                        # Historical prices
                        fig3.add_trace(go.Scatter(
                            x=df_prophet['ds'],
                            y=df_prophet['y'],
                            name='Historical Price',
                            line=dict(color='#00b4d8')
                        ))

                        # Predicted prices
                        future_forecast = forecast[forecast['ds'] > df_prophet['ds'].max()]
                        fig3.add_trace(go.Scatter(
                            x=future_forecast['ds'],
                            y=future_forecast['yhat'],
                            name='Predicted Price',
                            line=dict(color='#ff9f1c', dash='dash')
                        ))

                        # Confidence interval
                        fig3.add_trace(go.Scatter(
                            x=pd.concat([future_forecast['ds'], future_forecast['ds'][::-1]]),
                            y=pd.concat([future_forecast['yhat_upper'], future_forecast['yhat_lower'][::-1]]),
                            fill='toself',
                            fillcolor='rgba(255,159,28,0.1)',
                            line=dict(color='rgba(255,255,255,0)'),
                            name='Confidence Interval'
                        ))

                        fig3.update_layout(template="plotly_dark", height=400)
                        st.plotly_chart(fig3, use_container_width=True)

                        # Prediction summary
                        last_price = current_price
                        predicted_price = future_forecast['yhat'].iloc[-1]
                        predicted_change = ((predicted_price - last_price) / last_price) * 100

                        col1, col2, col3 = st.columns(3)
                        col1.metric("Current Price", f"${last_price:.2f}")
                        col2.metric(f"Predicted ({forecast_days}d)", f"${predicted_price:.2f}", f"{predicted_change:.2f}%")
                        col3.metric("Prediction", "📈 Upward" if predicted_change > 0 else "📉 Downward")

                        st.caption("⚠️ Predictions are for educational purposes only. Not financial advice.")

                    except Exception as e:
                        st.error(f"Prediction error: {e}")

                # AI Analysis
                st.subheader("🧠 Claude AI Analysis")
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