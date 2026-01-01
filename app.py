import pandas as pd
import matplotlib as plt
import yfinance as yf
import altair as alt
import streamlit as st

st.title('米国株価可視化アプリ')

st.sidebar.write("""
# GAF株価
こちらは株価可視化ツールです。以下のオプションから表示日数を指定    
""")

st.sidebar.write("""
## 表示日数選択
""")

days = st.sidebar.slider('日数',1,50,20)

st.write(f"""
### 過去 **{days}日間**のGAFA株価
"""    
)

#キャッシュに関数をためることができる
@st.cache_data
def get_data(days,tickers):
    df = pd.DataFrame()
    for company in tickers.keys():
        tkr = yf.Ticker(tickers[company])
        hist = tkr.history(period = f'{days}d')
        hist.index = hist.index.strftime('%d %B %Y')
        #終値を習得
        hist = hist[['Close']]
        #列の名前をappleにする
        hist.columns = [company]
        #列と行を転置する
        hist = hist.T
        hist.index.name = 'Name'
        df = pd.concat([df,hist])
    return df

st.sidebar.write(
    """## 株価の範囲指定"""
)

ymin,ymax = st.sidebar.slider(
    '範囲を指定してください',
    0.0, 350.0,(0.0,3500.0)
)

tickers = {
    'apple' : 'AAPL',
    'facebook' : 'META', 
    'google' :'GOOGL',
    'microsoft' : 'MSFT',
    'netflix' : 'NFLX',
    'amazon' : 'AMZN'
}

df = get_data(days, tickers)

companies = st.multiselect(
    '会社名を選択してください。',
    list(df.index),
    ['google','amazon','facebook','apple','microsoft','netflix']
)

if not companies:
    st.error('少なくとも一社は選んでください。')
else:
    data = df.loc[companies]
    st.write("### 株価(USD)" ,data.sort_index())
    # 転置する
    data = data.T.reset_index()
    data = pd.melt(data, id_vars=['Date']).rename(
        columns={'value': 'Stock Prices(USD)'}
    )
    
    chart = (
    alt.Chart(data)
    #clipでグラフの外にはみ出しているものは削除する。
    .mark_line(opacity=0.8, clip=True)
    #scaleで200～300に指定できる。
    .encode(
        x="Date:T",
        y=alt.Y("Stock Prices(USD):Q", stack=None ,scale= alt.Scale(domain=[ymin,ymax])),
        color='Name:N'
    )
    )

    # コンテナの中にサイズをしてあげる
    st.altair_chart(chart, width='stretch')