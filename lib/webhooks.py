import sys
import os
sys.path.append(os.path.join(".."))
from discord import Webhook, RequestsWebhookAdapter
import pandas as pd


def parse_webhook(webhook: str):

    temp = [x for x in webhook.split("webhooks")[1].split("/") if x != ""]
    return Webhook.partial(int(temp[0]), temp[1], adapter=RequestsWebhookAdapter())


def get_webhook_by_type(project: str, webhook_type: str):

    df = pd.read_csv("../local/webhooks_config.csv", sep=";")
    df = df.loc[((df["project"] == project) & (df["webhook_type"] == webhook_type))]
    if not df.empty:
        return df["webhook"].iloc[0]
    else:
        return None


def create_project_webhooks_dict(project: str):

    project_webhooks = {}
    project_webhooks.update(
        {"LIST": parse_webhook(webhook=get_webhook_by_type(project=project, webhook_type="list"))})
    project_webhooks.update(
        {"EDIT": parse_webhook(webhook=get_webhook_by_type(project=project, webhook_type="list"))})
    project_webhooks.update(
        {"ACCEPT_OFFER": parse_webhook(webhook=get_webhook_by_type(project=project, webhook_type="sales"))})
    project_webhooks.update(
        {"SALE": parse_webhook(webhook=get_webhook_by_type(project=project, webhook_type="sales"))})
    project_webhooks.update(
        {"MAKE_OFFER": parse_webhook(webhook=get_webhook_by_type(project=project, webhook_type="offer"))})
    project_webhooks.update(
        {"REJECT_OFFER": parse_webhook(webhook=get_webhook_by_type(project=project, webhook_type="offer"))})
    project_webhooks.update(
        {"COLLECTION_OFFER": parse_webhook(webhook=get_webhook_by_type(project=project, webhook_type="offer"))})

    return project_webhooks


def create_hooks_master():
    master = {}
    df = pd.read_csv("../local/webhooks_config.csv", sep=";")
    for p in df["project"].unique():
        master.update({p: create_project_webhooks_dict(project=p)})

    return master
