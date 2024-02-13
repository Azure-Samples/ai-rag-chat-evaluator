import logging
import os

import openai
from azure.core.credentials import AzureKeyCredential
from azure.identity import AzureDeveloperCliCredential
from azure.search.documents import SearchClient

logger = logging.getLogger("scripts")


def get_openai_config():
    if os.environ.get("OPENAI_HOST") == "azure":
        if os.environ.get("AZURE_OPENAI_KEY"):
            logger.info("Using Azure OpenAI Service with API Key from AZURE_OPENAI_KEY")
            api_key = os.environ["AZURE_OPENAI_KEY"]
        else:
            logger.info("Using Azure OpenAI Service with Azure Developer CLI Credential")
            azure_credential = AzureDeveloperCliCredential()
            api_key = azure_credential.get_token("https://cognitiveservices.azure.com/.default").token
        openai_config = {
            "api_type": "azure",
            "api_base": f"https://{os.environ['AZURE_OPENAI_SERVICE']}.openai.azure.com",
            "api_key": api_key,
            "api_version": "2023-07-01-preview",
            "deployment_id": os.environ["AZURE_OPENAI_EVAL_DEPLOYMENT"],
            "model": os.environ["OPENAI_GPT_MODEL"],
        }
    else:
        logger.info("Using OpenAI Service with API Key from OPENAICOM_KEY")
        openai_config = {
            "api_type": "openai",
            "api_key": os.environ["OPENAICOM_KEY"],
            "organization": os.environ["OPENAICOM_ORGANIZATION"],
            "model": os.environ["OPENAI_GPT_MODEL"],
        }
    return openai_config


def get_search_client():
    if api_key := os.environ.get("AZURE_SEARCH_KEY"):
        logger.info("Using Azure Search Service with API Key from AZURE_SEARCH_KEY")
        azure_credential = AzureKeyCredential(api_key)
    else:
        logger.info("Using Azure Search Service with Azure Developer CLI Credential")
        azure_credential = AzureDeveloperCliCredential()

    return SearchClient(
        endpoint=f"https://{os.environ['AZURE_SEARCH_SERVICE']}.search.windows.net",
        index_name=os.environ["AZURE_SEARCH_INDEX"],
        credential=azure_credential,
    )


def get_openai_client(oai_config: dict):
    if oai_config["api_type"] == "azure":
        return openai.AzureOpenAI(
            api_version=oai_config["api_version"],
            azure_endpoint=oai_config["api_base"],
            api_key=oai_config["api_key"] if os.environ.get("AZURE_OPENAI_KEY") else None,
            azure_ad_token=None if os.environ.get("AZURE_OPENAI_KEY") else oai_config["api_key"],
            azure_deployment=oai_config["deployment_id"],
        )
    else:
        return openai.OpenAI(
            api_key=oai_config["api_key"],
            organization=oai_config["organization"],
            model=oai_config["model"],
        )
