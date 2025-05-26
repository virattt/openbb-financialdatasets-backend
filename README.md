# OpenBB with Financial Datasets backend

1. Install all the required libraries

```bash
poetry install
```

2. Use your API Key

Update your .env file with the API key obtained from your [Financial Datasets API Key dashboard](https://www.financialdatasets.ai/).

3. Run the custom backend

```bash
poetry run uvicorn src.main:app --reload
```

4. Go into [OpenBB](httpc://pro.openbb.co), into the Data Connectors tab to  be more specific.

5. Add a new custom backend, with https://pro.openbb.co/app/data-connectors?modal=data-connectors&dcTab=backend as follows.

<img width="854" alt="Screenshot 2024-11-03 at 1 24 47 AM" src="https://github.com/user-attachments/assets/82ff3f7a-aaae-4449-a81e-546b576f67bd">

That's it, now you can access data from that widget.
