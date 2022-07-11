import pandas as pd


def create_MAPPINGS(key: str, value: str):
    df = pd.read_csv("../local/projects_config.csv", sep=";")
    dictionary = {}
    for _, r in df.iterrows():
        dictionary.update({r[key].lower(): r[value].lower()})
    return dictionary


# PROJECT CONFIGS
PROJECTS = create_MAPPINGS(key="token_contract", value="project")
GATEWAYS = create_MAPPINGS(key="project", value="gateway")
PJ_NAMES = create_MAPPINGS(key="project", value="project_name")
TOKEN_SCS = create_MAPPINGS(key="project", value="token_contract")

URL = "https://mainnet.veblocks.net"

VESEA_ADDRESS_URL = "https://www.vesea.io/profile?address="
VESEA_MARKETPLACE_URL = "https://vesea.io/collections.html"

VESEA_MARKET_ADDRESS = "0xBeCf72C58BE308B961e3E7CDa9e8611E19e87BA7".lower()
VESEA_OFFERS_ADDRESS = "0xF02e1Cf743fB36468F90c8daa2119313cD99dB2d".lower()
VESEA_PROFILE_ADDRESS = "0x242035f42C59119b9A22D4270506c07Fb792e55C".lower()

VESEA_GATEWAY = "https://vesea.mypinata.cloud/ipfs/"


WOV_ADDRESS_URL = "https://marketplace.worldofv.art/profile/"
WOV_MARKETPLACE_URL = "https://marketplace.worldofv.art"

WOV_MARKET_ADDRESS = "0xc3F851F9f78c92573620582BF9002f0C4a114B67".lower()
WOV_OFFERS_ADDRESS = "0xE56861c0bB8012EC955DA4E4122895ED2A46d229".lower()
WOV_PROFILE_ADDRESS = "0xc7592f90a6746e5d55e4a1543b6cae6d5b11d258".lower()

WOV_GATEWAY = "https://opengateway.mypinata.cloud/ipfs/"

# CODE MAPPING TO PRINT
MODES = {"LIST": "🟩 **LISTED**",
         "EDIT": "🟩 **LISTED (EDIT)**",
         "SALE": "🟥 **SOLD**",
         "MAKE_OFFER": "📥 **OFFER**",
         "COLLECTION_OFFER": "📥 **COLLECTION OFFER**",
         "ACCEPT_OFFER": "✅ **OFFER ACCEPTED**",
         "REJECT_OFFER": "❌ **OFFER REJECTED**"}
