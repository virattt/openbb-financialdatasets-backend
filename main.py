import json
from pathlib import Path
import os
import requests
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from functools import wraps
import asyncio
from fastapi.websockets import WebSocketState

# Initialize empty dictionary for widgets
WIDGETS = {}

# Store active WebSocket connections and their subscribed tickers
active_connections: dict[str, WebSocket] = {}
subscribed_tickers: dict[str, set[str]] = {}

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
    "type": "table",
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
    "type": "table",
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

@register_widget({
    "name": "Crypto Prices",
    "description": "Get historical price data for cryptocurrencies with customizable intervals and date ranges.",
    "category": "Crypto",
    "subcategory": "Prices",
    "type": "table",
    "widgetId": "crypto_prices",
    "endpoint": "crypto_prices",
    "gridData": {
        "w": 10,
        "h": 12
    },
    "data": {
        "table": {
            "showAll": True,
            "columnsDefs": [
                {"field": "time", "headerName": "Time", "width": 180, "cellDataType": "text"},
                {"field": "open", "headerName": "Open", "width": 120, "cellDataType": "number"},
                {"field": "high", "headerName": "High", "width": 120, "cellDataType": "number"},
                {"field": "low", "headerName": "Low", "width": 120, "cellDataType": "number"},
                {"field": "close", "headerName": "Close", "width": 120, "cellDataType": "number"},
                {"field": "volume", "headerName": "Volume", "width": 120, "cellDataType": "number"}
            ]
        }
    },
    "params": [
        {
            "type": "text",
            "paramName": "ticker",
            "label": "Symbol",
            "value": "BTC-USD",
            "description": "Crypto ticker (e.g., BTC-USD)"
        },
        {
            "type": "text",
            "value": "day",
            "paramName": "interval",
            "label": "Interval",
            "description": "Time interval for prices",
            "options": [
                {"value": "minute", "label": "Minute"},
                {"value": "day", "label": "Day"},
                {"value": "week", "label": "Week"},
                {"value": "month", "label": "Month"},
                {"value": "year", "label": "Year"}
            ]
        },
        {
            "type": "number",
            "paramName": "interval_multiplier",
            "label": "Interval Multiplier",
            "value": "1",
            "description": "Multiplier for the interval (e.g., 5 for every 5 minutes)"
        },
        {
            "type": "date",
            "paramName": "start_date",
            "label": "Start Date",
            "value": "2024-01-01",
            "description": "Start date for historical data"
        },
        {
            "type": "date",
            "paramName": "end_date",
            "label": "End Date",
            "value": "2024-03-20",
            "description": "End date for historical data"
        }
    ]
})
@app.get("/crypto_prices")
def get_crypto_prices(
    ticker: str,
    interval: str,
    interval_multiplier: int,
    start_date: str,
    end_date: str
):
    """Get historical crypto prices"""
    headers = {
        "X-API-KEY": FINANCIAL_DATASETS_API_KEY
    }
    
    url = (
        f'https://api.financialdatasets.ai/crypto/prices'
        f'?ticker={ticker}'
        f'&interval={interval}'
        f'&interval_multiplier={interval_multiplier}'
        f'&start_date={start_date}'
        f'&end_date={end_date}'
    )

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        prices = data.get('prices', [])
        
        # Format timestamps to be more readable
        for price in prices:
            if 'timestamp' in price:
                # Convert timestamp to ISO format date string
                timestamp = price['timestamp']
                if isinstance(timestamp, str):
                    # If it's already a string, try to parse and reformat
                    from datetime import datetime
                    try:
                        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        price['time'] = dt.strftime('%Y-%m-%d %H:%M:%S')
                        price.pop('timestamp', None)  # Remove the original timestamp field
                    except ValueError:
                        pass  # Keep original if parsing fails
        
        return prices

    print(f"Request error {response.status_code}: {response.text}")
    return JSONResponse(
        content={"error": response.text}, status_code=response.status_code
    )

@register_widget({
    "name": "Crypto Snapshot",
    "description": "Get real-time price snapshot for cryptocurrencies with live updates.",
    "category": "Crypto",
    "subcategory": "Prices",
    "type": "live_grid",
    "widgetId": "crypto_snapshot",
    "endpoint": "crypto_snapshot",
    "wsEndpoint": "crypto_ws",
    "gridData": {
        "w": 40,
        "h": 8
    },
    "data": {
        "wsRowIdColumn": "ticker",
        "table": {
            "showAll": True,
            "columnsDefs": [
                {"field": "ticker", "headerName": "Symbol", "width": 120, "cellDataType": "text"},
                {
                    "field": "price", 
                    "headerName": "Price", 
                    "width": 120, 
                    "cellDataType": "number",
                    "renderFn": "showCellChange",
                    "renderFnParams": {
                        "colorValueKey": "change_24h"
                    }
                },
                {"field": "volume_24h", "headerName": "24h Volume", "width": 150, "cellDataType": "number"},
                {
                    "field": "change_24h", 
                    "headerName": "24h Change", 
                    "width": 120, 
                    "cellDataType": "number",
                    "renderFn": "greenRed"
                },
                {"field": "timestamp", "headerName": "Last Updated", "width": 180, "cellDataType": "text"}
            ]
        }
    },
    "params": [
        {
            "type": "text",
            "paramName": "ticker",
            "label": "Symbol",
            "value": "BTC-USD",
            "description": "Select cryptocurrencies to track",
            "multiSelect": True,
            "options": [
                {"label": "Bitcoin (BTC-USD)", "value": "BTC-USD"}
            ]
        }
    ]
})
@app.get("/crypto_snapshot")
async def get_crypto_snapshot(ticker: str = Query(..., description="Comma-separated list of tickers")):
    """Initial data endpoint for crypto snapshot"""
    headers = {
        "X-API-KEY": FINANCIAL_DATASETS_API_KEY
    }
    
    # Handle multiple tickers - ensure proper splitting and cleaning
    tickers = [t.strip() for t in ticker.split(",") if t.strip()]
    if not tickers:
        return JSONResponse(
            content={"error": "No valid tickers provided"},
            status_code=400
        )
    
    results = []
    for t in tickers:
        url = (
            f'https://api.financialdatasets.ai/crypto/prices/snapshot'
            f'?ticker={t}'
        )
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            snapshot = data.get('snapshot', {})
            
            # Format timestamp
            if 'timestamp' in snapshot:
                timestamp = snapshot['timestamp']
                if isinstance(timestamp, str):
                    from datetime import datetime
                    try:
                        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        snapshot['timestamp'] = dt.strftime('%Y-%m-%d %H:%M:%S')
                    except ValueError:
                        pass
            
            results.append(snapshot)
        else:
            print(f"Error fetching data for {t}: {response.status_code} - {response.text}")
    
    return results

@app.websocket("/crypto_ws")
async def crypto_websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for live crypto updates"""
    await websocket.accept()
    connection_id = str(id(websocket))
    active_connections[connection_id] = websocket
    subscribed_tickers[connection_id] = set()
    
    try:
        await websocket_handler(websocket, connection_id)
    except WebSocketDisconnect:
        del active_connections[connection_id]
        del subscribed_tickers[connection_id]
    except Exception as e:
        await websocket.close(code=1011)
        raise HTTPException(status_code=500, detail=str(e))

async def websocket_handler(websocket: WebSocket, connection_id: str):
    """Handle WebSocket connections and data updates"""
    
    async def consumer_handler():
        try:
            async for data in websocket.iter_json():
                if tickers := data.get("params", {}).get("ticker"):
                    # Handle both string and array inputs
                    if isinstance(tickers, str):
                        tickers = [t.strip() for t in tickers.split(",") if t.strip()]
                    elif isinstance(tickers, list):
                        tickers = [t.strip() for t in tickers if t.strip()]
                    else:
                        continue
                    
                    if tickers:  # Only update if we have valid tickers
                        subscribed_tickers[connection_id] = set(tickers)
        except WebSocketDisconnect:
            return
        except Exception as e:
            print(f"Consumer error: {e}")
            return

    async def producer_handler():
        headers = {"X-API-KEY": FINANCIAL_DATASETS_API_KEY}
        
        while websocket.client_state != WebSocketState.DISCONNECTED:
            try:
                current_tickers = list(subscribed_tickers[connection_id])
                
                for ticker in current_tickers:
                    url = f'https://api.financialdatasets.ai/crypto/prices/snapshot?ticker={ticker}'
                    response = requests.get(url, headers=headers)
                    
                    if response.status_code == 200:
                        data = response.json()
                        snapshot = data.get('snapshot', {})
                        
                        # Format timestamp
                        if 'timestamp' in snapshot:
                            timestamp = snapshot['timestamp']
                            if isinstance(timestamp, str):
                                from datetime import datetime
                                try:
                                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                                    snapshot['timestamp'] = dt.strftime('%Y-%m-%d %H:%M:%S')
                                except ValueError:
                                    pass
                        
                        await websocket.send_json(snapshot)
                    
                    await asyncio.sleep(1)  # Wait 1 second between updates
                
                await asyncio.sleep(0.1)  # Small delay between ticker cycles
                
            except WebSocketDisconnect:
                return
            except Exception as e:
                print(f"Producer error: {e}")
                await asyncio.sleep(1)  # Wait before retrying
    
    consumer_task = asyncio.create_task(consumer_handler())
    producer_task = asyncio.create_task(producer_handler())
    
    done, pending = await asyncio.wait(
        [consumer_task, producer_task],
        return_when=asyncio.FIRST_COMPLETED
    )
    
    for task in pending:
        task.cancel()

# Add this function to fetch available tickers
async def get_available_tickers():
    """Fetch available tickers for earnings press releases"""
    headers = {
        "X-API-KEY": FINANCIAL_DATASETS_API_KEY
    }
    
    url = 'https://api.financialdatasets.ai/earnings/press-releases/tickers/'
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            tickers = data.get('tickers', [])
            # Sort tickers alphabetically
            tickers.sort()
            # Create options list with both label and value
            return [{"label": ticker, "value": ticker} for ticker in tickers]
    except Exception as e:
        print(f"Error fetching tickers: {e}")
    
    # Return a default list if fetch fails
    return [{"label": "AAPL", "value": "AAPL"}]

@register_widget({
    "name": "Earnings Press Releases",
    "description": "Get earnings-related press releases for companies, including URL, publish date, and full text.",
    "category": "Equity",
    "subcategory": "Earnings",
    "type": "markdown",
    "widgetId": "earnings_press_releases",
    "endpoint": "earnings_press_releases",
    "gridData": {
        "w": 40,
        "h": 8
    },
    "params": [
        {
            "type": "text",
            "paramName": "ticker",
            "label": "Symbol",
            "value": "AAPL",
            "description": "Company ticker to get earnings press releases for",
            "multiSelect": False,
            "options": []  # Will be populated dynamically
        }
    ]
})

# Add back the endpoint to get available tickers
@app.get("/earnings_press_releases/tickers")
async def get_tickers():
    """Get available tickers for earnings press releases"""
    return await get_available_tickers()

# Add back the startup event handler
@app.on_event("startup")
async def startup_event():
    """Initialize widget options on startup"""
    tickers = await get_available_tickers()
    # Update the widget configuration with available tickers
    for widget in WIDGETS.values():
        if widget.get("widgetId") == "earnings_press_releases":
            for param in widget.get("params", []):
                if param.get("paramName") == "ticker":
                    param["options"] = tickers

@app.get("/earnings_press_releases")
async def get_earnings_press_releases(ticker: str = Query(..., description="Company ticker")):
    """Get earnings press releases for a company"""
    headers = {
        "X-API-KEY": FINANCIAL_DATASETS_API_KEY
    }
    
    url = (
        f'https://api.financialdatasets.ai/earnings/press-releases'
        f'?ticker={ticker}'
    )

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        press_releases = data.get('press_releases', [])
        
        if not press_releases:
            return "# No Earnings Press Releases Found\n\nNo earnings press releases were found for this company."
        
        # Format the press releases into markdown
        markdown_content = f"# Earnings Press Releases for {ticker}\n\n"
        
        for release in press_releases:
            # Format date
            publish_date = release.get('publish_date', '')
            if publish_date:
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(publish_date.replace('Z', '+00:00'))
                    publish_date = dt.strftime('%B %d, %Y %H:%M:%S')
                except (ValueError, AttributeError):
                    pass
            
            # Get title and URL
            title = release.get('title', 'Untitled')
            url = release.get('url', '')
            
            # Format text with proper line breaks and paragraphs
            text = release.get('text', '')
            if text:
                # Replace multiple newlines with double newlines for markdown paragraphs
                text = text.replace('\n\n', '\n').replace('\n', '\n\n')
                # Truncate if too long
                if len(text) > 1000:
                    text = text[:997] + "..."
            
            # Build the markdown for this release
            markdown_content += f"## {title}\n\n"
            markdown_content += f"**Published:** {publish_date}\n\n"
            if url:
                markdown_content += f"[Read Full Release]({url})\n\n"
            markdown_content += f"{text}\n\n"
            markdown_content += "---\n\n"  # Add separator between releases
        
        return markdown_content

    print(f"Request error {response.status_code}: {response.text}")
    return f"# Error\n\nFailed to fetch earnings press releases: {response.text}"

@register_widget({
    "name": "Stock Prices Historical",
    "description": "Get historical price data for stocks with customizable intervals and date ranges.",
    "category": "Equity",
    "subcategory": "Prices",
    "type": "table",
    "widgetId": "stock_prices_historical",
    "endpoint": "stock_prices_historical",
    "gridData": {
        "w": 40,
        "h": 8
    },
    "data": {
        "table": {
            "showAll": True,
            "columnsDefs": [
                {"field": "time", "headerName": "Time", "width": 180, "cellDataType": "text", "pinned": "left"},
                {"field": "open", "headerName": "Open", "width": 120, "cellDataType": "number"},
                {"field": "high", "headerName": "High", "width": 120, "cellDataType": "number"},
                {"field": "low", "headerName": "Low", "width": 120, "cellDataType": "number"},
                {"field": "close", "headerName": "Close", "width": 120, "cellDataType": "number"},
                {"field": "volume", "headerName": "Volume", "width": 120, "cellDataType": "number"},
                {"field": "vwap", "headerName": "VWAP", "width": 120, "cellDataType": "number"},
                {"field": "transactions", "headerName": "Transactions", "width": 120, "cellDataType": "number"}
            ]
        }
    },
    "params": [
        {
            "type": "ticker",
            "paramName": "ticker",
            "label": "Symbol",
            "value": "AAPL",
            "description": "Stock ticker to get historical prices for"
        },
        {
            "type": "text",
            "value": "day",
            "paramName": "interval",
            "label": "Interval",
            "description": "Time interval for prices",
            "options": [
                {"value": "minute", "label": "Minute"},
                {"value": "day", "label": "Day"},
                {"value": "week", "label": "Week"},
                {"value": "month", "label": "Month"},
                {"value": "year", "label": "Year"}
            ]
        },
        {
            "type": "number",
            "paramName": "interval_multiplier",
            "label": "Interval Multiplier",
            "value": "1",
            "description": "Multiplier for the interval (e.g., 5 for every 5 minutes)"
        },
        {
            "type": "date",
            "paramName": "start_date",
            "label": "Start Date",
            "value": "2024-01-01",
            "description": "Start date for historical data"
        },
        {
            "type": "date",
            "paramName": "end_date",
            "label": "End Date",
            "value": "2024-03-20",
            "description": "End date for historical data"
        }
    ]
})
@app.get("/stock_prices_historical")
def get_stock_prices_historical(
    ticker: str,
    interval: str,
    interval_multiplier: int,
    start_date: str,
    end_date: str
):
    """Get historical stock prices"""
    headers = {
        "X-API-KEY": FINANCIAL_DATASETS_API_KEY
    }
    
    url = (
        f'https://api.financialdatasets.ai/prices'
        f'?ticker={ticker}'
        f'&interval={interval}'
        f'&interval_multiplier={interval_multiplier}'
        f'&start_date={start_date}'
        f'&end_date={end_date}'
    )

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        prices = data.get('prices', [])
        
        # Process and clean up the data
        for price in prices:
            # Format timestamp
            if 'timestamp' in price:
                timestamp = price['timestamp']
                if isinstance(timestamp, str):
                    from datetime import datetime
                    try:
                        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        price['time'] = dt.strftime('%Y-%m-%d %H:%M:%S')
                    except ValueError:
                        pass
            
            # Remove unwanted fields
            price.pop('timestamp', None)
            price.pop('time_milliseconds', None)
            price.pop('ticker', None)
        
        return prices

    print(f"Request error {response.status_code}: {response.text}")
    return JSONResponse(
        content={"error": response.text}, status_code=response.status_code
    )

@register_widget({
    "name": "Stock Prices Snapshot",
    "description": "Get real-time price snapshot for stocks with live updates.",
    "category": "Equity",
    "subcategory": "Prices",
    "type": "live_grid",
    "widgetId": "stock_snapshot",
    "endpoint": "stock_snapshot",
    "wsEndpoint": "stock_ws",
    "gridData": {
        "w": 40,
        "h": 8
    },
    "data": {
        "wsRowIdColumn": "ticker",
        "table": {
            "showAll": True,
            "columnsDefs": [
                {"field": "ticker", "headerName": "Symbol", "width": 120, "cellDataType": "text", "pinned": "left"},
                {
                    "field": "price", 
                    "headerName": "Price", 
                    "width": 120, 
                    "cellDataType": "number",
                    "renderFn": "showCellChange",
                    "renderFnParams": {
                        "colorValueKey": "change_percent"
                    }
                },
                {"field": "volume", "headerName": "Volume", "width": 150, "cellDataType": "number"},
                {
                    "field": "change_percent", 
                    "headerName": "Change %", 
                    "width": 120, 
                    "cellDataType": "number",
                    "renderFn": "greenRed"
                },
                {"field": "timestamp", "headerName": "Last Updated", "width": 180, "cellDataType": "text"}
            ]
        }
    },
    "params": [
        {
            "type": "text",
            "paramName": "ticker",
            "label": "Symbol",
            "value": "AAPL",
            "description": "Select stocks to track",
            "multiSelect": True,
            "options": [
                {"label": "Apple Inc. (AAPL)", "value": "AAPL"},
                {"label": "Microsoft Corp. (MSFT)", "value": "MSFT"},
                {"label": "Amazon.com Inc. (AMZN)", "value": "AMZN"},
                {"label": "Alphabet Inc. (GOOGL)", "value": "GOOGL"},
                {"label": "Meta Platforms Inc. (META)", "value": "META"}
            ]
        }
    ]
})
@app.get("/stock_snapshot")
async def get_stock_snapshot(ticker: str = Query(..., description="Comma-separated list of tickers")):
    """Initial data endpoint for stock snapshot"""
    headers = {
        "X-API-KEY": FINANCIAL_DATASETS_API_KEY
    }
    
    # Handle multiple tickers - ensure proper splitting and cleaning
    tickers = [t.strip() for t in ticker.split(",") if t.strip()]
    if not tickers:
        return JSONResponse(
            content={"error": "No valid tickers provided"},
            status_code=400
        )
    
    results = []
    for t in tickers:
        url = (
            f'https://api.financialdatasets.ai/prices/snapshot'
            f'?ticker={t}'
        )
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            snapshot = data.get('snapshot', {})
            
            # Format timestamp
            if 'timestamp' in snapshot:
                timestamp = snapshot['timestamp']
                if isinstance(timestamp, str):
                    from datetime import datetime
                    try:
                        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        snapshot['timestamp'] = dt.strftime('%Y-%m-%d %H:%M:%S')
                    except ValueError:
                        pass
            
            results.append(snapshot)
        else:
            print(f"Error fetching data for {t}: {response.status_code} - {response.text}")
    
    return results

@app.websocket("/stock_ws")
async def stock_websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for live stock updates"""
    await websocket.accept()
    connection_id = str(id(websocket))
    active_connections[connection_id] = websocket
    subscribed_tickers[connection_id] = set()
    
    print(f"New WebSocket connection established: {connection_id}")
    
    try:
        await websocket_handler(websocket, connection_id, "stock")
    except WebSocketDisconnect:
        print(f"WebSocket disconnected: {connection_id}")
        del active_connections[connection_id]
        del subscribed_tickers[connection_id]
    except Exception as e:
        print(f"WebSocket error: {e}")
        await websocket.close(code=1011)
        raise HTTPException(status_code=500, detail=str(e))

async def websocket_handler(websocket: WebSocket, connection_id: str, data_type: str = "crypto"):
    """Handle WebSocket connections and data updates"""
    
    async def consumer_handler():
        try:
            async for data in websocket.iter_json():
                print(f"Received WebSocket message: {data}")
                if tickers := data.get("params", {}).get("ticker"):
                    # Handle both string and array inputs
                    if isinstance(tickers, str):
                        tickers = [t.strip() for t in tickers.split(",") if t.strip()]
                    elif isinstance(tickers, list):
                        tickers = [t.strip() for t in tickers if t.strip()]
                    else:
                        continue
                    
                    if tickers:  # Only update if we have valid tickers
                        print(f"Updating subscribed tickers for {connection_id}: {tickers}")
                        subscribed_tickers[connection_id] = set(tickers)
        except WebSocketDisconnect:
            print(f"Consumer WebSocket disconnected: {connection_id}")
            return
        except Exception as e:
            print(f"Consumer error: {e}")
            return

    async def producer_handler():
        headers = {"X-API-KEY": FINANCIAL_DATASETS_API_KEY}
        endpoint = "crypto/prices/snapshot" if data_type == "crypto" else "prices/snapshot"
        
        while websocket.client_state != WebSocketState.DISCONNECTED:
            try:
                current_tickers = list(subscribed_tickers[connection_id])
                if not current_tickers:
                    await asyncio.sleep(1)
                    continue
                
                print(f"Fetching updates for tickers: {current_tickers}")
                
                for ticker in current_tickers:
                    url = f'https://api.financialdatasets.ai/{endpoint}?ticker={ticker}'
                    response = requests.get(url, headers=headers)
                    
                    if response.status_code == 200:
                        data = response.json()
                        snapshot = data.get('snapshot', {})
                        
                        if not snapshot:
                            print(f"No snapshot data for {ticker}")
                            continue
                        
                        # Ensure we have the required fields
                        if 'price' not in snapshot:
                            print(f"Missing price in snapshot for {ticker}: {snapshot}")
                            continue
                        
                        # Format timestamp
                        if 'timestamp' in snapshot:
                            timestamp = snapshot['timestamp']
                            if isinstance(timestamp, str):
                                from datetime import datetime
                                try:
                                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                                    snapshot['timestamp'] = dt.strftime('%Y-%m-%d %H:%M:%S')
                                except ValueError:
                                    pass
                        
                        print(f"Sending update for {ticker}: {snapshot}")
                        await websocket.send_json(snapshot)
                    else:
                        print(f"Error fetching data for {ticker}: {response.status_code} - {response.text}")
                    
                    await asyncio.sleep(1)  # Wait 1 second between updates
                
                await asyncio.sleep(0.1)  # Small delay between ticker cycles
                
            except WebSocketDisconnect:
                print(f"Producer WebSocket disconnected: {connection_id}")
                return
            except Exception as e:
                print(f"Producer error: {e}")
                await asyncio.sleep(1)  # Wait before retrying
    
    consumer_task = asyncio.create_task(consumer_handler())
    producer_task = asyncio.create_task(producer_handler())
    
    done, pending = await asyncio.wait(
        [consumer_task, producer_task],
        return_when=asyncio.FIRST_COMPLETED
    )
    
    for task in pending:
        task.cancel()
