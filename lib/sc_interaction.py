import pandas as pd
import sys
import os
import requests
sys.path.append(os.path.join(".."))
from lib.blockchain import Blockchain
from local.config import PROJECTS, VESEA_PROFILE_ADDRESS, WOV_PROFILE_ADDRESS, VESEA_GATEWAY, WOV_GATEWAY


blockchain = Blockchain()


class VeseaMarket:

    def __init__(self):
        self.profile_contract_address = VESEA_PROFILE_ADDRESS
        self.profile_method_hash = "0x0f53a470"
        self.null_address = "0x0000000000000000000000000000000000000000000000000000000000000000"
        self.actions = {"0xb3899b51b340638a15e910a0fe4e2ff5a5061ebd6aa2424078cabb0876118bd9": "LIST",
                        "0xc448b641f9d136b2082a1543ddddd8b6f8b86576bc444a187505ea3934bac2f8": "REMOVAL",
                        "0x829123eda815ee393110704f1363c6a888f17756625234059c6bf27ea25d8ad0": "ACCEPT_OFFER",
                        "0xbcf10c39f62b09d50efa1e275c1297b15ef10efd0e4e9b54883d782eef4ef564": "SALE",
                        "0x068dedde85b59648270684d4c7303620187a93832a4b7bee4408261ee2c5f680": "EDIT",
                        "0xd46a008cac1cb5ec453d4928e646f936b6d11b8ec6b488f00a55bd90eda74a73": "MAKE_OFFER",
                        "0x43ed654b5afe744e9dff01129791fe9dae038198180b53ccfe83a78ed49fb278": "COLLECTION_OFFER",
                        "0xba709ccf1e80b1ce1a0ed3bd35bc3b7577e98902a05e0ec2b4aa478e7a9596a2": "REJECT_OFFER"
                        }

    # Specific encoding for VESEA events.
    def get_events(self, markets: list, init_block: int, end_block: int):

        event_list = blockchain.get_market_event_log_data(markets=markets,
                                                          init_block=init_block,
                                                          end_block=end_block)
        parsed_event_list = [x for x in event_list if x["topics"][0] in list(self.actions.keys())]

        final = []
        zero_address = "0x0000000000000000000000000000000000000000"
        for x in parsed_event_list:
            type_list = self.actions[x["topics"][0]]
            nft_id = int(x["topics"][2], 16)
            buyer = zero_address
            seller = zero_address

            if self.actions[x["topics"][0]] in ["SALE", "LIST", "ACCEPT_OFFER"]:
                seller = "0x" + x["topics"][3][-40:]
                buyer = "0x" + blockchain.parse_tx(x["data"])[1][0][-40:]
                price = int(blockchain.parse_tx(x["data"])[1][1], 16) / pow(10, 18)

            elif self.actions[x["topics"][0]] in ["MAKE_OFFER"]:
                buyer = "0x" + x["topics"][3][-40:]
                price = int(blockchain.parse_tx(x["data"])[1][0], 16) / pow(10, 18)

            elif self.actions[x["topics"][0]] in ["COLLECTION_OFFER"]:
                buyer = "0x" + x["topics"][2][-40:]
                price = int(blockchain.parse_tx(x["data"])[1][0], 16) / pow(10, 18)
                nft_id = -1

            else:
                seller = "0x" + x["topics"][3][-40:]
                try:
                    price = int(blockchain.parse_tx(x["data"])[1][0], 16) / pow(10, 18)
                except Exception as err:
                    price = 0

            try:
                final.append({"market": "VeSea",
                              "project": PROJECTS["0x" + x["topics"][1][-40:]],
                              "nft_id": nft_id,
                              "seller": seller, "buyer": buyer,
                              "price": price, "type": type_list,
                              "timestamp": x["meta"]["blockTimestamp"], "block": x["meta"]["blockNumber"],
                              "txID": x["meta"]["txID"]})
            except Exception as err:
                print("Error: ", err)

        df = pd.DataFrame.from_dict(final)

        return df

    def get_profile(self, user_address: str):
        return blockchain.get_profile(profile_contract_address=self.profile_contract_address,
                                      method_hash=self.profile_method_hash,
                                      user_address=user_address)

    @staticmethod
    def get_nft_meta(token_sc_address: str, nft_id: int, gateway: str):
        return blockchain.get_nft_meta(token_sc_address=token_sc_address,
                                       nft_id=nft_id,
                                       gateway=gateway)


class WovMarket:

    def __init__(self):
        self.profile_contract_address = WOV_PROFILE_ADDRESS
        self.profile_method_hash = "0x000d93da"
        self.null_address = "0x0000000000000000000000000000000000000000000000000000000000000000"
        self.actions = {"0x4d0b0c9dba6cc79527b52313869b6e43dcd323e7c1291fae24187c72dff27db0": "LIST",
                        "0x315a69fa5403a5ca6f7e2dbb0d79c209cb8ec13ecc8459fd26e8a2f4224636a0": "REMOVAL",
                        "0x7df4fb99994dbf47a019499d198c1ba69e18420edf1d0bc9a31cba5ffa531ef0": "ACCEPT_OFFER",
                        "0x2f68ebad7f3a3ea711d9b120acf07d745158b6253d70ce38d9f35724f4b75cc6": "SALE",
                        "0x5c5106a18b73e6d3098473272e251fd15266062bbba9e9683cf980a307dd4c45": "MAKE_OFFER",
                        # SAME AS MAKE_OFFER "0x5c5106a18b73e6d3098473272e251fd15266062bbba9e9683cf980a307dd4c45": "COLLECTION_OFFER",
                        # NOT CONSIDERED "0xba709ccf1e80b1ce1a0ed3bd35bc3b7577e98902a05e0ec2b4aa478e7a9596a2": "REJECT_OFFER"
                        }

    # Specific encoding for WOV events.
    def get_events(self, markets: list, init_block: int, end_block: int):

        event_list = blockchain.get_market_event_log_data(markets=markets,
                                                          init_block=init_block,
                                                          end_block=end_block)

        parsed_event_list = [x for x in event_list if x["topics"][0] in list(self.actions.keys())]

        final = []
        zero_address = "0x0000000000000000000000000000000000000000"

        for x in parsed_event_list:
            type_list = self.actions[x["topics"][0]]
            buyer = zero_address
            seller = zero_address
            nft_id = int(x["topics"][3], 16)

            if self.actions[x["topics"][0]] in ["LIST"]:
                seller = "0x" + blockchain.parse_tx(x["data"])[1][0][-40:]
                price = int(blockchain.parse_tx(x["data"])[1][1], 16) / pow(10, 18)

            elif self.actions[x["topics"][0]] in ["REMOVAL"]:
                seller = blockchain.connect.get_tx(x["meta"]["txID"])["origin"]
                price = 0

            elif self.actions[x["topics"][0]] in ["SALE"]:
                buyer = "0x" + blockchain.parse_tx(x["data"])[1][0][-40:]
                price = int(blockchain.connect.get_tx(x["meta"]["txID"])["clauses"][0]["value"], 16)/pow(10, 18)

            elif self.actions[x["topics"][0]] in ["ACCEPT_OFFER"]:
                buyer = "0x" + blockchain.parse_tx(x["data"])[1][1][-40:]
                price = int(blockchain.parse_tx(x["data"])[1][2], 16) / pow(10, 18)

            elif self.actions[x["topics"][0]] in ["MAKE_OFFER"]:
                if nft_id == 0:
                    nft_id = -1
                    type_list = "COLLECTION_OFFER"
                buyer = blockchain.connect.get_tx(x["meta"]["txID"])["origin"]
                price = int(blockchain.parse_tx(x["data"])[1][1], 16) / pow(10, 18)

            else:
                seller = "0x" + x["topics"][3][-40:]
                try:
                    price = int(blockchain.parse_tx(x["data"])[1][0], 16) / pow(10, 18)
                except Exception as err:
                    price = 0

            try:
                final.append({"market": "World of V",
                              "project": PROJECTS["0x" + x["topics"][2][-40:]],
                              "nft_id": nft_id,
                              "seller": seller, "buyer": buyer,
                              "price": price, "type": type_list,
                              "timestamp": x["meta"]["blockTimestamp"], "block": x["meta"]["blockNumber"],
                              "txID": x["meta"]["txID"]})
            except Exception as err:
                print("Error:", err)

        df = pd.DataFrame.from_dict(final)

        return df

    def get_profile(self, user_address: str):
        return blockchain.get_profile(profile_contract_address=self.profile_contract_address,
                                      method_hash=self.profile_method_hash,
                                      user_address=user_address)

    @staticmethod
    def get_nft_meta(token_sc_address: str, nft_id: int, gateway: str):
        if token_sc_address.lower() == "0x5e6265680087520dc022d75f4c45f9ccd712ba97".lower():
            return blockchain.get_community_nft_meta(token_sc_address=token_sc_address,
                                                     nft_id=nft_id,
                                                     gateway=gateway)
        else:
            return blockchain.get_nft_meta(token_sc_address=token_sc_address,
                                           nft_id=nft_id,
                                           gateway=gateway)
