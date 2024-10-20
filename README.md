# medicalRegRAG
The repository for the medical regulatory RAG application. To allows medical personell stay upto date with the regulatory practices set by medical institutions.

## Pre-requisites

1. [OpenAI API Key](https://platform.openai.com/api-keys)
2. Running [NEO4J Database instance](https://neo4j.com/product/auradb/?ref=docs-nav-get-started)

## Running the application

To run the application, you must install the libraries listed in `requirements.txt`.

```sh
pip install -r requirements.txt
```


Then run the `streamlit run` command to start the app on [http://localhost:8501](http://localhost:8501).

```sh
streamlit run bot.py ```
```

### For Mac
For first time set up, create the secrets.toml file and include the Open AI Key, Open AI Model and the Neo4j Database credentials

```sh

OPENAI_API_KEY = "YOUR-OPENAI-API-KEY"
OPENAI_MODEL = "gpt-3.5-turbo"

NEO4J_URI = "NEO4J-URI"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "NEO4J-PASSWORD"

AWS_ACCESS_KEY = "AWS-ACCESS-KEY"
AWS_SECRET_KEY = "AWS-SECRET-KEY"
AWS_REGION = "aws-region"
S3_BUCKET_NAME = "medical-name"
```
