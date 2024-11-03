# OpenBB with Financial Datasets backend

1. Install all the required libraries

```bash
poetry install
```

2. Use your API Key

Update your .env file with the API key obtained from your [Financial Datasets API Key dashboard](https://www.financialdatasets.ai/).

3. Run the custom backend

```bash
uvicorn main:app --reload
```
