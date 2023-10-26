
app_id = ""
app_secret = ""
redirect_url = ""

from fyers_api import fyersModel, accessToken
import os, time
import pandas as pd
from fyers_api.Websocket import ws
import threading


def get_access_toekn():
    if not os.path.exists("access_token.txt"):
        session = accessToken.SessionModel(client_id=app_id, secret_key=app_secret,redirect_uri=redirect_url, response_type="code", grant_type="authorization_code")
        response = session.generate_authcode()
        print("Login Url : ", response)
        auth_code = input("Enter Auth Code : ")
        session.set_token(auth_code)
        access_token = session.generate_token()["access_token"]
        with open("access_token.txt", "w") as f:
            f.write(access_token)
    else:
        with open("access_token.txt", "r") as f:
            access_token = f.read()
    return access_token


access_token = get_access_toekn()
fyers = fyersModel.FyersModel(client_id=app_id, token=access_token, log_path="")
print(fyers.get_profile())

# link = 'https://public.fyers.in/sym_details/NSE_FO.csv'
#
# headers_name = ["Fytoken", "Symbol Details", "Exchange Instrument type", "Minimum lot size", "Tick size",
#                             "ISIN", "Trading Session", "Last update date", "Expiry date", "Symbol ticker", "Exchange",
#                             "Segment",
#                             "Scrip code", "Name", "Underlying scrip code", "Strike price", "Option type"]
# pd.read_csv(link, names=headers_name).to_csv("NSE_FO.csv")


ws_access_token = f"{app_id}:{access_token}"
data_type = "symbolData"
run_background = False
symbol = ["NSE:SBIN-EQ", "NSE:ONGC-EQ","NSE:RELIANCE-EQ", "NSE:UPL-EQ", "NSE:ACC-EQ", "NSE:LUPIN-EQ", "NSE:BANKNIFTY2251933300PE"]
live_data = {}


def custom_message(msg):
    # print("new msg..")
    for symbol_data in msg:
        live_data[symbol_data['symbol']] = {"LTP": symbol_data['ltp']}
    # print(live_data)


fyersSocket = ws.FyersSocket(access_token=ws_access_token,run_background=False,log_path="")
fyersSocket.websocket_data = custom_message


def subscribe_new_symbol(symbol_list):
    global fyersSocket, data_type
    fyersSocket.subscribe(symbol=symbol_list, data_type=data_type)


threading.Thread(target=subscribe_new_symbol, args=(symbol,)).start()
while True:
    print(f"Loop: {live_data}")
    time.sleep(1)
