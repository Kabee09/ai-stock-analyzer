# 📈 AI Stock Analyzer

An AI-powered stock analysis and ML prediction tool built with Python, Streamlit, and Claude AI.
Fetches real-time market data, generates intelligent investment insights, and predicts future prices.

## 🚀 Features
- Real-time stock data via Yahoo Finance
- Interactive candlestick charts with Plotly
- ML price prediction using Facebook Prophet
- Confidence interval forecasting (7-90 days)
- AI-powered analysis powered by Claude (Anthropic)
- Price trends, key observations, risk assessment
- Market sentiment indicator (Bullish/Neutral/Bearish)

## 🛠️ Tech Stack
- **Python** — Core language
- **Streamlit** — Web dashboard
- **yfinance** — Real market data
- **Prophet** — ML forecasting model
- **Plotly** — Interactive charts
- **Anthropic Claude API** — AI analysis
- **Docker** — Containerization
- **GitHub Actions** — CI/CD pipeline

## 🌐 Live Demo
https://ai-stock-analyzer-axswdekqow2jappaddbcmyf.streamlit.app/

## ⚙️ Setup & Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 🐳 Run with Docker
```bash
docker build -t ai-stock-analyzer .
docker run -p 8501:8501 ai-stock-analyzer
```

## 👤 Author
Kabilan Rajendran — [LinkedIn](https://linkedin.com/in/kabilan-rajendran) | [GitHub](https://github.com/Kabee09)
