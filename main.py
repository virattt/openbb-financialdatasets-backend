import json
from pathlib import Path
import os
import pandas as pd
import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import plotly.graph_objects as go

app = FastAPI()

origins = [
    "https://pro.openbb.co",
    "http://localhost:1420"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

load_dotenv()
FINANCIAL_DATASETS_API_KEY = os.getenv("FINANCIAL_DATASETS_API_KEY")


@app.get("/")
def read_root():
    return {"Info": "Financial Datasets to integrate with OpenBB"}


@app.get("/widgets.json")
def get_widgets():
    """Widgets configuration file for OpenBB"""
    return JSONResponse(
        content=json.load((Path(__file__).parent.resolve() / "widgets.json").open())
    )


@app.get("/income")
def get_income(ticker: str, period: str, limit: int):
    """Get income statement"""
    # add your API key to the headers
    headers = {
        "X-API-KEY": FINANCIAL_DATASETS_API_KEY
    }
    # create the URL
    url = (
        f'https://api.financialdatasets.ai/financials/income-statements'
        f'?ticker={ticker}'
        f'&period={period}'
        f'&limit={limit}'
    )

    # make API request
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        # parse income_statements from the response
        income_statements = response.json().get('income_statements')

        return income_statements

    print(f"Request error {response.status_code}: {response.text}")
    return JSONResponse(
        content={"error": response.text}, status_code=response.status_code
    )

@app.get("/balance")
def get_balance(ticker: str, period: str, limit: int):
    """Get balance sheet"""
    # add your API key to the headers
    headers = {
        "X-API-KEY": FINANCIAL_DATASETS_API_KEY
    }
    # create the URL
    url = (
        f'https://api.financialdatasets.ai/financials/balance-sheets'
        f'?ticker={ticker}'
        f'&period={period}'
        f'&limit={limit}'
    )

    # make API request
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        # parse balance_sheets from the response
        balance_sheets = response.json().get('balance_sheets')

        return balance_sheets

    print(f"Request error {response.status_code}: {response.text}")
    return JSONResponse(
        content={"error": response.text}, status_code=response.status_code
    )


@app.get("/income-revenue")
def get_income_revenue_chart(ticker: str, period: str, limit: int):
    """Get income revenue chart"""
    # add your API key to the headers
    headers = {
        "X-API-KEY": FINANCIAL_DATASETS_API_KEY
    }
    # create the URL
    url = (
        f'https://api.financialdatasets.ai/financials/income-statements'
        f'?ticker={ticker}'
        f'&period={period}'
        f'&limit={limit}'
    )

    # make API request
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        # parse income_statements from the response
        income_statements = response.json().get('income_statements')

        # Create a DataFrame from the income statements
        df = pd.DataFrame(income_statements)

        # Convert report_period to datetime for proper sorting
        df['report_period'] = pd.to_datetime(df['report_period'])

        # Sort the DataFrame by report_period
        df = df.sort_values('report_period')

        # Create a bar chart using Plotly
        figure = go.Figure(
            layout=dict(
                yaxis=dict(
                    title="Revenue",
                    showgrid=True,
                    gridcolor='rgba(255,255,255,0.1)',
                    gridwidth=1
                ),
                xaxis=dict(
                    title="Time",
                    showgrid=True,
                    gridcolor='rgba(255,255,255,0.1)',
                    gridwidth=1
                ),
                margin=dict(b=50, l=10, r=40, t=0),
                plot_bgcolor='rgb(21,21,24)',
                paper_bgcolor='rgb(21,21,24)',
                font=dict(color='rgb(255,255,255)'),
                legend=dict(font=dict(color='rgb(255,255,255)'))
            )
        )
        figure.add_trace(go.Scatter(x=df["report_period"], y=df["revenue"], mode='lines'))

        # Return the plotly json
        return JSONResponse(content=json.loads(figure.to_json()))

    print(f"Request error {response.status_code}: {response.text}")
    return JSONResponse(
        content={"error": response.text}, status_code=response.status_code
    )
