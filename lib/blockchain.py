import requests
import sys
import pandas as pd
from thor_requests.connect import Connect

sys.path.append("..")
from local.config import URL, VESEA_MARKET_ADDRESS, VESEA_OFFERS_ADDRESS, WOV_MARKET_ADDRESS, WOV_OFFERS_ADDRESS


class Blockchain:

    def __init__(self, url=URL):
        self.url = url
        self.dictionary = self.__build_dictionary__()
        self.connect = Connect(url=url)

    @staticmethod
    def __build_dictionary__():
        df = pd.read_csv("../local/projects_config.csv", sep=";")
        result = {}

        for _, r in df.iterrows():
            result.update({r["project"]: r["token_contract"]})

        return result

    @staticmethod
    def parse_tx(clause, topic_size=64):
        # all clause data has topics of 64 and a init consisting on the remainder chars.
        code = clause[:len(clause) % topic_size]
        topic_array = clause[len(clause) % topic_size:]

        topics = [topic_array[i:i + topic_size] for i in range(0, len(topic_array), topic_size)]

        return code, topics

    def post_event_log(self, tx_body):
        r = requests.post(
            url=self.url + "/logs/event",
            headers={"accept": "application/json", "Content-Type": "application/json"},
            json=tx_body,
            timeout=20,
        )

        return r.json()

    def get_market_event_log_data(self, markets: list, init_block: int, end_block: int):

        block_range = {"unit": "block", "from": init_block, "to": end_block}

        criteria = [{"address": x} for x in markets]

        tx_body = {"range": block_range,
                   "criteriaSet": criteria,
                   "order": "desc"}

        return self.post_event_log(tx_body=tx_body)

    def get_transfer_event_log_data(self, collections: list, init_block: int, end_block: int):

        block_range = {"unit": "block", "from": init_block, "to": end_block}

        # Topic0 is the topic that contains the transfer hash, which is specifically 0xddf25... for standard NFT smart contracts on vechain.
        criteria = [{"address": x, "topic0": "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"} for x in collections]

        tx_body = {"range": block_range,
                   "criteriaSet": criteria,
                   "order": "desc"}

        return self.post_event_log(tx_body=tx_body)

    def get_profile(self, profile_contract_address: str, method_hash: str, user_address: str):
        profile_name = user_address[:6] + "..." + user_address[-4:]

        clauses = {"to": profile_contract_address, "value": "0",
                   "data": method_hash + user_address[2:].zfill(64).lower()}

        tx_body = {"clauses": [clauses]}

        try:
            r = requests.post(
                url="https://sync-mainnet.vechain.org/accounts/*",
                headers={"accept": "application/json", "Content-Type": "application/json"},
                json=tx_body,
                timeout=20,
            )
            r = self.parse_tx(r.json()[0]["data"])[1][-1]
            if int(r, 16) != 0:
                profile_name = str(bytes.fromhex(r).decode('utf-8'))

        except Exception as err:
            print("Error:", err)
            pass

        return profile_name.replace("\x00", "")

    @staticmethod
    # Default method that applies to all NFT Smart Contracts on Vechain
    # "0xc87b56dd" is the hash of the method to query for the token URI given the NFT ID.
    # Hosting Gateway for IPFS METADATA depends on which platform minted the token.
    def __get_token_uri__(token_sc_address, nft_id, gateway):
        clauses = {"to": token_sc_address, "value": "0", "data": "0xc87b56dd" + hex(nft_id)[2:].zfill(64)}

        tx_body = {"clauses": [clauses]}

        r = requests.post(
            url="https://sync-mainnet.vechain.org/accounts/*",
            headers={"accept": "application/json", "Content-Type": "application/json"},
            json=tx_body,
            timeout=20,
        )
        token_uri = bytes.fromhex(r.json()[0]["data"][2 + 128:]).decode('utf-8').strip()
        token_uri = token_uri.replace("\x00", "", -1)
        return token_uri.replace("ipfs://", gateway)

    # Method to get metadata from the URI: image and attributes -> Pretty standard for Vechain NFTs.
    def get_nft_meta(self, token_sc_address: str, nft_id: int, gateway: str):
        token_uri = self.__get_token_uri__(token_sc_address=token_sc_address,
                                           nft_id=nft_id,
                                           gateway=gateway)

        result = requests.get(url=token_uri)
        result = result.json()

        # Some collections have a field "Image" rather than "image", this clause is to prevent the code from crashing!
        try:
            image_path = result["image"].replace("ipfs://", gateway)
        except:
            image_path = result["Image"].replace("ipfs://", gateway)

        # Not all NFTs have attributes, but so far all have a description. This clause handles it.
        try:
            attributes = ["**" + str(x["trait_type"]) + "**: " + str(x["value"]) for x in result["attributes"] if
                          x["trait_type"] != "Wealth Index"]
            "\n".join(attributes)

        except Exception as err:
            print("ERROR:", err)
            try:
                attributes = [result["Description"]]
            except Exception as err:
                print("ERROR:", err)
                attributes = [result["description"]]

        return image_path, attributes

    # The WOV community NFT token contract has a specific method to query the the METADATA URI
    # The rest is similar to the other method above.
    @staticmethod
    def __get_community_token_uri__(token_sc_address: str, nft_id: int, gateway: str):
        clauses = {"to": token_sc_address, "value": "0", "data": "0x4edea111" + hex(nft_id)[2:].zfill(64)}

        tx_body = {"clauses": [clauses]}

        r = requests.post(
            url="https://sync-mainnet.vechain.org/accounts/*",
            headers={"accept": "application/json", "Content-Type": "application/json"},
            json=tx_body,
            timeout=20,
        )
        token_uri = bytes.fromhex(r.json()[0]["data"][384:384+128]).decode('utf-8').strip()
        token_uri = token_uri.replace("\x00", "", -1)
        token_uri = token_uri.replace(".", "", -1)
        token_uri = gateway + token_uri

        return token_uri

    # The community token metadata is different, because metadata has a different structure from standard mints.
    def get_community_nft_meta(self, token_sc_address: str, nft_id: int, gateway: str):
        token_uri = self.__get_community_token_uri__(token_sc_address=token_sc_address,
                                                     nft_id=nft_id,
                                                     gateway=gateway)

        result = requests.get(url=token_uri)
        result = result.json()
        try:
            image_path = gateway + result["fileHash"]
        except:
            image_path = ""

        try:
            attributes = ["**" + str(x) + "**: " + result[x] for x in ["collectionName", "name", "description"]]
            "\n".join(attributes)

        except Exception as err:
            print("ERROR:", err)
            try:
                attributes = [result["Description"]]
            except Exception as err:
                print("ERROR:", err)
                attributes = [result["description"]]

        return image_path, attributes

    # NOT HAPPY WITH THIS STILL, but it is working. I am lazy to build 2 more decoder functions. Work in progress!
    def get_market_event_log_data_for(self, project_sc: str, market: str, init_block: int, end_block: int):

        if market in ["wov"]:
            markets = [VESEA_OFFERS_ADDRESS, VESEA_MARKET_ADDRESS]
            topic = "topic1"
        else:
            markets = [WOV_OFFERS_ADDRESS, WOV_MARKET_ADDRESS]
            topic = "topic2"

        block_range = {"unit": "block", "from": init_block, "to": end_block}

        criteria = [{"address": x, topic: project_sc} for x in markets]

        tx_body = {"range": block_range,
                   "criteriaSet": criteria,
                   "order": "desc"}

        return self.post_event_log(tx_body=tx_body)