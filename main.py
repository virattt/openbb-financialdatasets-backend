import json
from pathlib import Path
import os
import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from functools import wraps
import asyncio

# Initialize empty dictionary for widgets
WIDGETS = {}


def register_widget(widget_config):
    """
    Decorator that registers a widget configuration in the WIDGETS dictionary.
    
    Args:
        widget_config (dict): The widget configuration to add to the WIDGETS 
            dictionary. This should follow the same structure as other entries 
            in WIDGETS.
    
    Returns:
        function: The decorated function.
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Call the original function
            return await func(*args, **kwargs)
            
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Call the original function
            return func(*args, **kwargs)
        
        # Extract the endpoint from the widget_config
        endpoint = widget_config.get("endpoint")
        if endpoint:
            # Add an id field to the widget_config if not already present
            if "id" not in widget_config:
                widget_config["id"] = endpoint
            
            WIDGETS[endpoint] = widget_config
        
        # Return the appropriate wrapper based on whether the function is async
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    return decorator

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


# Endpoint that returns the registered widgets configuration
# The WIDGETS dictionary is maintained by the registry.py helper
# which automatically registers widgets when using the @register_widget decorator
@app.get("/widgets.json")
def get_widgets():
    """Returns the configuration of all registered widgets
    
    The widgets are automatically registered through the @register_widget decorator
    and stored in the WIDGETS dictionary from registry.py
    
    Returns:
        dict: The configuration of all registered widgets
    """
    return WIDGETS


@register_widget({
    "name": "Income Statement",
    "description": "Financial statements that provide information about a company's revenues, expenses, and profits over a specific period.",
    "category": "Equity",
    "subcategory": "Financials",
    "widgetType": "individual",
    "widgetId": "income",
    "endpoint": "income",
    "gridData": {
    "w": 80,
    "h": 12
    },
    "data": {
    "table": {
        "showAll": True
    }
    },
    "params": [
        {
            "type": "ticker",
            "paramName": "ticker",
            "label": "Symbol",
            "value": "AAPL",
            "description": "Ticker to get income statement for"
        },
        {
            "type": "text",
            "value": "annual",
            "paramName": "period",
            "label": "Period",
            "description": "Period to get statements from",
            "options": [
                {
                    "value": "annual",
                    "label": "Annual"
                },
                {
                    "value": "quarterly",
                    "label": "Quarterly"
                },
                {
                    "value": "ttm",
                    "label": "TTM"
                }
            ]
        },
        {
            "type": "number",
            "paramName": "limit",
            "label": "Number of Statements",
            "value": "10",
            "description": "Number of statements to display"
        }
    ]
})
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
        data = response.json()
        statements = data.get('income_statements', [])
        for stmt in statements:
            stmt.pop('ticker', None)
        return statements

    print(f"Request error {response.status_code}: {response.text}")
    return JSONResponse(
        content={"error": response.text}, status_code=response.status_code
    )

@register_widget({
    "name": "Balance Sheet",
    "description": "A financial statement that summarizes a company's assets, liabilities and shareholders' equity at a specific point in time.",
    "category": "Equity",
    "subcategory": "Financials",
    "widgetType": "individual",
    "widgetId": "balance",
    "endpoint": "balance",
    "gridData": {
    "w": 80,
    "h": 12
    },
    "data": {
    "table": {
        "showAll": True
    }
    },
    "params": [
        {
            "type": "ticker",
            "paramName": "ticker",
            "label": "Symbol",
            "value": "AAPL",
            "description": "Ticker to get balance sheet for"
        },
        {
            "type": "text",
            "value": "annual",
            "paramName": "period",
            "label": "Period",
            "description": "Period to get statements from",
            "options": [
                {
                    "value": "annual",
                    "label": "Annual"
                },
                {
                    "value": "quarterly",
                    "label": "Quarterly"
                },
                {
                    "value": "ttm",
                    "label": "TTM"
                }
            ]
        },
        {
            "type": "number",
            "paramName": "limit",
            "label": "Number of Statements",
            "value": "10",
            "description": "Number of statements to display"
        }
    ]
})
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
        balance_sheets = response.json().get('balance_sheets', [])
        for sheet in balance_sheets:
            sheet.pop('ticker', None)

        return balance_sheets

    print(f"Request error {response.status_code}: {response.text}")
    return JSONResponse(
        content={"error": response.text}, status_code=response.status_code
    )

@register_widget({
    "name": "Company Facts",
    "description": "Get key company information including name, CIK, market cap, total employees, website URL, and more.",
    "category": "Equity",
    "subcategory": "Company Info",
    "widgetType": "individual",
    "widgetId": "company_facts",
    "endpoint": "company_facts",
    "gridData": {
        "w": 10,
        "h": 12
    },
    "data": {
        "table": {
            "showAll": True,
            "columns": [
                {"field": "fact", "headerName": "Fact", "width": 200},
                {"field": "value", "headerName": "Value", "width": 200}
            ]
        }
    },
    "params": [
        {
            "type": "ticker",
            "paramName": "ticker",
            "label": "Symbol",
            "value": "AAPL",
            "description": "Ticker to get company facts for"
        }
    ]
})
@app.get("/company_facts")
def get_company_facts(ticker: str):
    """Get company facts for a ticker"""
    headers = {
        "X-API-KEY": FINANCIAL_DATASETS_API_KEY
    }
    
    url = (
        f'https://api.financialdatasets.ai/company/facts'
        f'?ticker={ticker}'
    )

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        company_facts = data.get('company_facts', {})
        
        # Transform the data into a list of fact-value pairs
        transformed_data = []
        for key, value in company_facts.items():
            # Convert key to title case and replace underscores with spaces
            fact = key.replace('_', ' ').title()
            transformed_data.append({
                "fact": fact,
                "value": value
            })
        
        # Sort by fact name for consistent display
        transformed_data.sort(key=lambda x: x["fact"])
        return transformed_data

    print(f"Request error {response.status_code}: {response.text}")
    return JSONResponse(
        content={"error": response.text}, status_code=response.status_code
    )
