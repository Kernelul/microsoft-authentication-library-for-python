"""
The configuration file would look like this (sans those // comments):

{
    "authority": "https://login.microsoftonline.com/Enter_the_Tenant_Name_Here",
    "client_id": "your_client_id",
    "scope": ["https://graph.microsoft.com/.default"],
        // Specific to Client Credentials Grant i.e. acquire_token_for_client(),
        // you don't specify, in the code, the individual scopes you want to access.
        // Instead, you statically declared them when registering your application.
        // Therefore the only possible scope is "resource/.default"
        // (here "https://graph.microsoft.com/.default")
        // which means "the static permissions defined in the application".

    "thumbprint": "790E... The thumbprint generated by AAD when you upload your public cert",
    "private_key_file": "filename.pem",
        // For information about generating thumbprint and private key file, refer:
        // https://github.com/AzureAD/microsoft-authentication-library-for-python/wiki/Client-Credentials#client-credentials-with-certificate

    "endpoint": "https://graph.microsoft.com/v1.0/users"
        // For this resource to work, you need to visit Application Permissions
        // page in portal, declare scope User.Read.All, which needs admin consent
        // https://github.com/Azure-Samples/ms-identity-python-daemon/blob/master/2-Call-MsGraph-WithCertificate/README.md
}

You can then run this sample with a JSON configuration file:

    python sample.py parameters.json
"""

import sys  # For simplicity, we'll read config file from 1st CLI param sys.argv[1]
import json
import logging

import requests
import msal


# Optional logging
# logging.basicConfig(level=logging.DEBUG)  # Enable DEBUG log for entire script
# logging.getLogger("msal").setLevel(logging.INFO)  # Optionally disable MSAL DEBUG logs

config = json.load(open(sys.argv[1]))

# Create a preferably long-lived app instance which maintains a token cache.
app = msal.ConfidentialClientApplication(
    config["client_id"], authority=config["authority"],
    client_credential={"thumbprint": config["thumbprint"], "private_key": open(config['private_key_file']).read()},
    # token_cache=...  # Default cache is in memory only.
                       # You can learn how to use SerializableTokenCache from
                       # https://msal-python.readthedocs.io/en/latest/#msal.SerializableTokenCache
    )

# Since MSAL 1.23, acquire_token_for_client(...) will automatically look up
# a token from cache, and fall back to acquire a fresh token when needed.
result = app.acquire_token_for_client(scopes=config["scope"])

if "access_token" in result:
    # Calling graph using the access token
    graph_data = requests.get(  # Use token to call downstream service
        config["endpoint"],
        headers={'Authorization': 'Bearer ' + result['access_token']},).json()
    print("Graph API call result: %s" % json.dumps(graph_data, indent=2))
else:
    print(result.get("error"))
    print(result.get("error_description"))
    print(result.get("correlation_id"))  # You may need this when reporting a bug

