import pandas as pd
import os
import sys
import discord
import requests
import shutil
sys.path.append(os.path.join(".."))
from local.config import VESEA_ADDRESS_URL, WOV_ADDRESS_URL, TOKEN_SCS, MODES, GATEWAYS, PJ_NAMES
from lib.sc_interaction import VeseaMarket, WovMarket


def get_rank(row: pd.core.series.Series):

    try:
        df = pd.read_csv("../data/rankings.csv", sep=";")
        df = df.drop_duplicates(subset=["project", "id"])
        df = df.loc[((df["project"] == row["project"]) & (df["id"] == row["nft_id"]))]
        rank = str(int(df["rank"].iloc[0]))
    except Exception as err:
        print(err)
        rank = "not available"

    return rank


def create_nft_embed(row: pd.core.series.Series):

    if row["market"] == "World of V":
        class_obj = WovMarket()
        user_url = WOV_ADDRESS_URL
        logo = "<:emojigold:995329451942490193>"
        page = "https://marketplace.worldofv.art/token/" + TOKEN_SCS[row["project"]] + "/" + str(row["nft_id"])

    else:
        class_obj = VeseaMarket()
        user_url = VESEA_ADDRESS_URL
        logo = "<:vesea:895873402303315988>"
        page = "https://www.vesea.io/assets?collection=" + row["project"] + "&id=" + str(row["nft_id"])

    try:
        image, traits = class_obj.get_nft_meta(token_sc_address=TOKEN_SCS[row["project"]],
                                               nft_id=abs(row["nft_id"]),
                                               gateway=GATEWAYS[row["project"]])

    except Exception as err:
        image, traits = "", [""]
        if row["project"] in ["vpunks"]:
            image = "https://www.larvalabs.com/cryptopunks/cryptopunk" + str(row["nft_id"]) + ".png?size=400"

    # Was too lazy to optimize this, but it works!
    if row["nft_id"] > 0:
        nft_id = row["project"].upper() + " #" + str(row["nft_id"])
    else:
        nft_id = row["project"].upper()

    if row["type"] in ["LIST", "EDIT"]:
        page = "[**" + nft_id + " [BUY NOW]**](" + page + ")"
    else:
        page = "[**" + nft_id + "**](" + page + ")"

    if row["type"] in ["SALE", "ACCEPT_OFFER"]:
        color = 0x0000ff
    else:
        color = 0x00ff00

    embed = discord.Embed(title=logo + " " + row["market"], description=page, color=color)
    embed.add_field(name='\u200b', value=MODES[row["type"]], inline=False)
    embed.add_field(name="Rank", value=get_rank(row=row), inline=True)
    embed.add_field(name="Price", value=f'{round(row["price"], 2):,}' + " VET", inline=True)
    embed.add_field(name="Block Number ",
                    value="[" + str(row["block"]) + "](https://explore.vechain.org/transactions/" + str(
                        row["txID"]) + ")",
                    inline=False)

    if int(row["seller"], 16) != 0:
        seller = "[" + class_obj.get_profile(user_address=row["seller"]) + "]" + "(" + user_url + row["seller"] + ")"
    else:
        seller = "n/a"

    if int(row["buyer"], 16) != 0:
        buyer = "[" + class_obj.get_profile(user_address=row["buyer"]) + "]" + "(" + user_url + row["buyer"] + ")"
    else:
        buyer = "n/a"

    embed.add_field(name="Seller", value=seller, inline=True)
    embed.add_field(name="Buyer", value=buyer, inline=True)

    if row["type"] not in ["COLLECTION_OFFER"]:
        result = []
        for a in traits:
            result.append(" - " + a)

        embed.add_field(name="Attributes", value="\n".join(result), inline=False)

    embed.add_field(name="The #VeFam List Bot",
                    value='\u200b',
                    inline=False)

    if row["market"] == "World of V":
        # World of V prefers image as image
        embed.set_image(url=image)
    else:
        # I decided to set image as thumbnail for VeSea
        embed.set_thumbnail(url=image)

    return image, embed


def discord_send(embed, hook):
    hook.send(embed=embed)


def get_media_id(url: str, twitter_api):
    filename = "temp.jpg"
    res = requests.get(url, stream=True)
    if res.status_code == 200:
        with open(filename, 'wb') as f:
            shutil.copyfileobj(res.raw, f)
        media = twitter_api.media_upload(filename=filename)
        os.remove(filename)
        return media
    else:
        return None


def twitter_send(row: pd.core.series.Series, image: str, twitter_api):

    icon = "🔔"

    if row["market"] in ["World of V"]:
        market_url = "https://worldofv.art/"
    else:
        market_url = "https://vesea.io"

    if "mad_vapes" in row["project"]:
        icon = "🦍"

    # Another piece of code than can be optimized, but I have little patience to do it :D
    numbers = {"0": "\u0030\u20E3",
               "1": "\u0031\u20E3",
               "2": "\u0032\u20E3",
               "3": "\u0033\u20E3",
               "4": "\u0034\u20E3",
               "5": "\u0035\u20E3",
               "6": "\u0036\u20E3",
               "7": "\u0037\u20E3",
               "8": "\u0038\u20E3",
               "9": "\u0039\u20E3"
               }

    temp = "{:,}".format(int(row["price"]))
    price = ""
    for x in temp:
        try:
            price = price + x.replace(x, numbers[x])
        except:
            price = price + x

    temp = "{:,}".format(int(row["price"] * 0.015))
    fee = ""
    for x in temp:
        try:
            fee = fee + x.replace(x, numbers[x])
        except:
            fee = fee + x

    tweet = icon + ' ' + PJ_NAMES[row["project"]] + ' Big Buy! ' + icon + '\n\n' + \
            '💰 ' + price + ' $VET 💰\n'

    try:
        eth_usd_price = float(requests.get(url="https://api.coinbase.com/v2/prices/ETH-USD/buy").json()["data"]["amount"])
        vet_usd_price = requests.get(url="https://api.vexchange.io/v1/tokens/0xD8CCDD85abDbF68DFEc95f06c973e87B1b5A9997").json()["usdPrice"]

        price_in_usd = round(row["price"] * vet_usd_price, 2)
        price_in_eth = round(price_in_usd / eth_usd_price, 3)

        tweet = tweet + '💰 ' + str(price_in_eth) + ' $ETH / ' + str(price_in_usd) + ' $USD 💰\n'

    except Exception as err:
        print(err)

    if row["market"] == "World of V" and "mad_vapes" in row["project"]:
        tweet = tweet + '💰 WoV ➡️ MVA DAO = ' + fee + ' $VET 💰\n'

    tweet = tweet + '\n💻Find ' + PJ_NAMES[row["project"]] + ' at ' + market_url + '\n\n' \
                    '#EthereumNFT #CardanoNFT #CronosNFT #NFTCommunity #NFT #tezosnft'

    media = get_media_id(url=image, twitter_api=twitter_api)

    if media != None:
        twitter_api.update_status(status=tweet, media_ids=[media.media_id_string])
