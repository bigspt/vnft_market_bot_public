import os
import sys
import time
sys.path.append(os.path.join(".."))
from lib.sc_interaction import VeseaMarket, WovMarket, blockchain
from local.twitter_secrets import my_twitter_api
from lib.information import discord_send, create_nft_embed, twitter_send
from lib.webhooks import create_hooks_master
from local.config import VESEA_MARKET_ADDRESS, VESEA_OFFERS_ADDRESS, WOV_MARKET_ADDRESS, WOV_OFFERS_ADDRESS

vesea = VeseaMarket()
world = WovMarket()


def myMain():

    hooks_master = create_hooks_master()

    processing_block = blockchain.connect.get_block("best")["number"]
    to_process = True
    repeater = 0

    while True:
        try:
            chain_block = blockchain.connect.get_block("best")["number"]

            if to_process:
                # Look for events in world of v and vesea (merging)
                txs = world.get_events(markets=[WOV_MARKET_ADDRESS, WOV_OFFERS_ADDRESS],
                                       init_block=processing_block,
                                       end_block=processing_block).append(
                      vesea.get_events(
                                        markets=[VESEA_MARKET_ADDRESS, VESEA_OFFERS_ADDRESS],
                                        init_block=processing_block,
                                        end_block=processing_block)
                )

                # Start Console Debug
                projs = ""
                if not txs.empty:
                    # Clear removal events because I don't want them listed.
                    txs = txs.loc[txs["type"] != "REMOVAL"]
                    txs = txs.reset_index(drop=True)

                    projs = ";".join(list(txs["project"]))
                    print(txs[txs.columns[:7]])

                print(int(time.time()), "Processing Block", processing_block, "(Chain", chain_block, ") -> ",
                      len(txs), "transactions (", projs, ")")
                # End Console Debug

                for _, r in txs.iterrows():

                    # Select appropriate discord server to send info to.
                    try:
                        HOOKS = hooks_master[r["project"]]
                    except:
                        HOOKS = hooks_master["dump_server"]

                    image, embed = create_nft_embed(row=r)

                    discord_send(embed=embed, hook=HOOKS[r["type"]])

                    if r["price"] >= 10000 and r["type"] in ["SALE", "ACCEPT_OFFER"] and "mad_vapes" in r["project"]:
                        try:
                            twitter_send(row=r, image=image, twitter_api=my_twitter_api)
                        except Exception as err:
                            print("Error: ", err)
                            pass

            # If processing block is the latest (current Vechain Block) we wait to avoid query API constantly.
            if processing_block >= chain_block - 1:
                to_process = False
                time.sleep(10)

            # Otherwise bot plays catch up processing everything as fast as possible to meet current Vechain Block
            else:
                to_process = True
                processing_block = processing_block + 1

        # In the event that some error occurs here (like Veblocks API timeout),
        # we wait 10 seconds and retry a maximum of 5 times before moving into next block
        except Exception as err:
            print("[ERROR] Main cycle:", err)
            repeater = repeater + 1
            if repeater > 5:
                processing_block = processing_block + 1
                to_process = True
                repeater = 0
            time.sleep(10)


if __name__ == "__main__":
    while True:
        print("RUNNING")
        try:
            myMain()
        except Exception as err:
            print("PANIC:", err)
            time.sleep(30)
