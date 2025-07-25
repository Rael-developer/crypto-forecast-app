from prophet import Prophet

def treinar_previsao(df, dias=30):
    model = Prophet(daily_seasonality=True)
    model.fit(df)
    future = model.make_future_dataframe(periods=dias)
    forecast = model.predict(future)
    return forecast
