import os

from azure.core.credentials import AzureKeyCredential
from azure.identity import AzureDeveloperCliCredential
from azure.search.documents import SearchClient


def get_openai_config():
    if os.environ.get("OPENAI_HOST") == "azure":
        if os.environ.get("AZURE_OPENAI_KEY"):
            api_type = "azure"
            api_key = os.environ["AZURE_OPENAI_KEY"]
        else:
            api_type = "azure_ad"
            azure_credential = AzureDeveloperCliCredential()
            api_key = azure_credential.get_token("https://cognitiveservices.azure.com/.default").token
        openai_config = {
            "api_type": api_type,
            "api_base": f"https://{os.environ['AZURE_OPENAI_SERVICE']}.openai.azure.com",
            "api_key": api_key,
            "api_version": "2023-07-01-preview",
            "deployment_id": os.environ["AZURE_OPENAI_EVAL_DEPLOYMENT"],
            "model": os.environ["OPENAI_GPT_MODEL"],
        }
    else:
        openai_config = {
            "api_type": "openai",
            "api_key": os.environ["OPENAI_KEY"],
            "organization": os.environ["OPENAI_ORGANIZATION"],
            "model": os.environ["OPENAI_GPT_MODEL"],
        }
    return openai_config


def get_search_client():
    if api_key := os.environ.get("AZURE_SEARCH_KEY"):
        azure_credential = AzureKeyCredential(api_key)
    else:
        azure_credential = AzureDeveloperCliCredential()

    return SearchClient(
        endpoint=f"https://{os.environ['AZURE_SEARCH_SERVICE']}.search.windows.net",
        index_name=os.environ["AZURE_SEARCH_INDEX"],
        credential=azure_credential,
    )
