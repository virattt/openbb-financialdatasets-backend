import json
from pathlib import Path
import os
import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

app = FastAPI()

origins = [
    "https://pro.openbb.co",
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
