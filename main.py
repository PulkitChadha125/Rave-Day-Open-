import AngelIntegration,AliceBlueIntegration
import time
import traceback
from datetime import datetime, timedelta
import pandas as pd
result_dict={}
from py_vollib.black_scholes.implied_volatility import implied_volatility
from py_vollib.black_scholes.greeks.analytical import delta
AliceBlueIntegration.load_alice()
AliceBlueIntegration.get_nfo_instruments()


def convert_julian_date(date_object):
    year = date_object.year
    month = date_object.month
    day = date_object.day
    a = (14 - month) // 12
    y = year + 4800 - a
    m = month + 12 * a - 3
    jdn = day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045
    return jdn


def get_delta(strikeltp,underlyingprice,strike,timeexpiery,riskfreeinterest,flag):
    # flag me  call  'c' ya put 'p'
    from py_vollib.black_scholes.greeks.analytical import delta
    iv= implied_volatility(price=strikeltp,S=underlyingprice,K=strike,t=timeexpiery,r=riskfreeinterest,flag=flag)
    value = delta(flag,underlyingprice,strike,timeexpiery,riskfreeinterest,iv)
    print("delta",value)
    return value


def option_delta_calculation(symbol,expiery,Tradeexp,strike,optiontype,underlyingprice,MODE):
    date_obj = datetime.strptime(Tradeexp, "%d-%b-%y")
    formatted_date = date_obj.strftime("%d%b%y").upper()
    optionsymbol = f"{symbol}{formatted_date}{strike}{optiontype}"


    fein = 'NFO'
    if symbol == "BANKEX" or symbol == "SENSEX":
        fein = "BFO"
        if MODE == "WEEKLY":
            date_obj = datetime.strptime(Tradeexp, '%d-%b-%y')
            formatted_date = f"{date_obj.strftime('%y')}{int(date_obj.strftime('%m'))}{date_obj.strftime('%d')}"
            optionsymbol=f"{symbol}{formatted_date}{strike}{optiontype}"

        #
        if MODE == "MONTHLY":
            date_obj = datetime.strptime(Tradeexp, '%d-%b-%y')
            formatted_date = f"{date_obj.strftime('%y')}{date_obj.strftime('%b').upper()}"
            optionsymbol=f"{symbol}{formatted_date}{strike}{optiontype}"
            print("delta optionsymbol: ", optionsymbol)

    optionltp=AngelIntegration.get_ltp(segment=fein, symbol=optionsymbol,
                             token=get_token(optionsymbol))
    if MODE == "WEEKLY":
        distanceexp = datetime.strptime(expiery, "%d-%b-%y")  # Convert string to datetime object if necessary
        print("MONTHLY: ", distanceexp)
    if MODE == "MONTHLY":
        distanceexp = datetime.strptime(expiery, "%d-%b-%y")  # Convert string to datetime object if necessary
        print("MONTHLY: ",distanceexp)
    t= (distanceexp-datetime.now())/timedelta(days=1)/365
    print("t: ",t)
    if optiontype=="CE":
        fg="c"
    else :
        fg = "p"
    value=get_delta(strikeltp=optionltp, underlyingprice=underlyingprice, strike=strike, timeexpiery=t,flag=fg ,riskfreeinterest=0.1)
    return value

def round_down_to_interval(dt, interval_minutes):
    remainder = dt.minute % interval_minutes
    minutes_to_current_boundary = remainder
    rounded_dt = dt - timedelta(minutes=minutes_to_current_boundary)
    rounded_dt = rounded_dt.replace(second=0, microsecond=0)
    return rounded_dt

def determine_min(minstr):
    min = 0
    if minstr == "1":
        min = 1
    if minstr == "3":
        min = 3
    if minstr == "5":
        min = 5
    if minstr == "15":
        min = 15
    if minstr == "30":
        min = 30

    return min

def delete_file_contents(file_name):
    try:
        # Open the file in write mode, which truncates it (deletes contents)
        with open(file_name, 'w') as file:
            file.truncate(0)
        print(f"Contents of {file_name} have been deleted.")
    except FileNotFoundError:
        print(f"File {file_name} not found.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
def get_user_settings():
    global result_dict
    # Symbol,lotsize,Stoploss,Target1,Target2,Target3,Target4,Target1Lotsize,Target2Lotsize,Target3Lotsize,Target4Lotsize,BreakEven,ReEntry
    try:
        csv_path = 'TradeSettings.csv'
        df = pd.read_csv(csv_path)
        df.columns = df.columns.str.strip()
        result_dict = {}
        # Symbol,EMA1,EMA2,EMA3,EMA4,lotsize,Stoploss,Target,Tsl
        for index, row in df.iterrows():
            # Symbol,Quantity,Timeframe,TF_INT,EXPIERY,BASESYMBOL,EntryTime,ExitTime,strikestep,StrikeNumber,USEEXPIERY,TradeExpiery,AliceblueTradeExp,PRODUCT_TYPE,Target1,Target2,Tp1Qty,Segement,Fetchdelay

            symbol_dict = {
                'Symbol': row['Symbol'],'Timeframe':row['Timeframe'],"Quantity":row['Quantity'],'EXPIERY': row['EXPIERY'], 'Votex_length':row['Votex_length'],
                 "BASESYMBOL": row['BASESYMBOL'],'exch':None,'EntryTime': row['EntryTime'], "ExitTime": row['ExitTime'],
                'strikestep': row['strikestep'], "StrikeNumber": row['StrikeNumber'],'USEEXPIERY': row['USEEXPIERY'], "TradeExpiery": row['TradeExpiery'],
                'AliceblueTradeExp': row['AliceblueTradeExp'], "PRODUCT_TYPE": row['PRODUCT_TYPE'],"InitialOnce":None,
                'FifteenHigh': None, "FifteenLow":None,"Bp":None,"Sp":None,"BUY":False,"SHORT":False,'Segement':row['Segement'],
                'Previoustrade':None,"RevTrade":False,"aliceexp": None,'TimeBasedExit':None,"segemntfetch":None,
                'Sp_Period':row['Sp_Period'],'Sp_Mul':row['Sp_Mul'],"runtime": datetime.now(),'TF_INT': row['TF_INT'],'UseSp': row['UseSp'],
                'secondlastcol':None,"DayopenOnce":False,"previousclose":None,"ltp":None,"DayOpenVal":None,
                'putstrike': None, 'callstrike': None,'Initial':None,"Fetchdelay":row['Fetchdelay'],'Target1':row['Target1'],
                'Target2':row['Target2'],'Tp1Qty':row['Tp1Qty'],'tp1val':None,'tp2':None,'remain':None,'tsl':None,'Ep':None,
                'tp1done':False,'tp2donebuy':False,'tp2donesell':False
            }
            result_dict[row['Symbol']] = symbol_dict
        print("result_dict: ", result_dict)
    except Exception as e:
        print("Error happened in fetching symbol", str(e))

get_user_settings()
def get_api_credentials():
    credentials = {}

    try:
        df = pd.read_csv('Credentials.csv')
        for index, row in df.iterrows():
            title = row['Title']
            value = row['Value']
            credentials[title] = value
    except pd.errors.EmptyDataError:
        print("The CSV file is empty or has no data.")
    except FileNotFoundError:
        print("The CSV file was not found.")
    except Exception as e:
        print("An error occurred while reading the CSV file:", str(e))

    return credentials


credentials_dict = get_api_credentials()
stockdevaccount=credentials_dict.get('stockdevaccount')
api_key=credentials_dict.get('apikey')
username=credentials_dict.get('USERNAME')
pwd=credentials_dict.get('pin')
totp_string=credentials_dict.get('totp_string')
AngelIntegration.login(api_key=api_key,username=username,pwd=pwd,totp_string=totp_string)

AngelIntegration.symbolmpping()


def get_token(symbol):
    df= pd.read_csv("Instrument.csv")
    row = df.loc[df['symbol'] == symbol]
    if not row.empty:
        token = row.iloc[0]['token']
        return token

def write_to_order_logs(message):
    with open('OrderLog.txt', 'a') as file:  # Open the file in append mode
        file.write(message + '\n')



def getstrikes_put(ltp, step , strikestep):
    result = {}
    result[int(ltp)] = None

    for i in range(step):
        result[int(ltp + strikestep * (i + 1))] = None
    return result

def getstrikes_call(ltp, step , strikestep):
    result = {}
    result[int(ltp)] = None
    for i in range(step):
        result[int(ltp - strikestep * (i + 1))] = None

    return result


def get_max_delta_strike(strikelist):
    max_delta = -float("inf")  # Initialize with negative infinity
    max_delta_strike = None
    for strike, delta in strikelist.items():
        if delta > max_delta:
            max_delta = delta
            max_delta_strike = strike
    return max_delta_strike

def round_to_nearest(number, nearest):
    return round(number / nearest) * nearest

def main_strategy():
    try:
        for symbol, params in result_dict.items():
            symbol_value = params['Symbol']
            timestamp = datetime.now()
            timestamp = timestamp.strftime("%d/%m/%Y %H:%M:%S")
            EntryTime = params['EntryTime']
            EntryTime = datetime.strptime(EntryTime, "%H:%M").time()
            ExitTime = params['ExitTime']
            ExitTime = datetime.strptime(ExitTime, "%H:%M").time()
            current_time = datetime.now().time()
            if isinstance(symbol_value, str):
                if current_time > EntryTime and current_time < ExitTime and datetime.now() >= params["runtime"]:
                    params["segemntfetch"] = 'NSE'
                    if symbol_value == "BANKEX" or symbol_value == "SENSEX":
                        params["segemntfetch"] = "BSE"

                    if (params['BASESYMBOL'] != "BANKEX" and params['BASESYMBOL'] != "SENSEX"
                                and params['BASESYMBOL'] != "NIFTY" and params['BASESYMBOL'] != "BANKNIFTY"
                                and params['BASESYMBOL'] != "FINNIFTY" and params['BASESYMBOL'] != "MIDCPNIFTY"):
                        params["segemntfetch"] = "MCX"

                    if params['Fetchdelay'] == True:
                        time.sleep(4)

                    spotdata = AngelIntegration.get_historical_data(symbol=params['Symbol'],
                                                                        token=get_token(params['Symbol']),
                                                                        timeframe=params["Timeframe"],
                                                                        segment=params["segemntfetch"],
                                                                        )
                    last_row = spotdata.iloc[-1]
                    last_rowtime = last_row['date']  # Assuming this is a pandas Timestamp

                    given_time = last_rowtime.time()

                    curr_time = datetime.now()

                    if curr_time.hour == given_time.hour and curr_time.minute == given_time.minute:
                        second_last_row = spotdata.iloc[-2]
                        print("second_last_row time: ", second_last_row['date'])
                        if params["DayopenOnce"] == False:
                            params["DayopenOnce"] = True
                            params["DayOpenVal"]=second_last_row['open']

                        params["previousclose"]=  second_last_row['close']

                    else:
                        second_last_row = spotdata.iloc[-1]
                        print("second_last_row time: ", second_last_row['date'])
                        if params["DayopenOnce"] == False:
                            params["DayopenOnce"] = True
                            params["DayOpenVal"] = second_last_row['open']

                        params["previousclose"] = second_last_row['close']

                    next_specific_part_time = datetime.now() + timedelta(
                        seconds=determine_min(str(params["TF_INT"])) * 60)
                    next_specific_part_time = round_down_to_interval(next_specific_part_time,
                                                                     determine_min(str(params["TF_INT"])))
                    print("Next datafetch time = ", next_specific_part_time)
                    params['runtime'] = next_specific_part_time
                    params["ltp"] = AngelIntegration.get_ltp(segment=params["segemntfetch"], symbol=params['Symbol'],
                                                             token=get_token(params['Symbol']))
                    #         sell
                    if ((params['Initial']== None or params['Initial']== "BUY") and params["previousclose"]<=params["DayOpenVal"]
                            and  params["DayOpenVal"] is not None and params['tp2donesell'] ==False):

                        if params['Segement'] == "MCX":
                            if params['Initial'] == "BUY" and params['remain'] == params['Quantity']:
                                OrderLog = f"{timestamp} Buy STOP AND REVERSE  @ {symbol_value} @ {params['ltp']}, lots exited  {params['remain']} "
                                print(OrderLog)
                                write_to_order_logs(OrderLog)
                                AliceBlueIntegration.NormalBuyExit(producttype=params["producttype"],
                                                                   exch=params['Segement'],
                                                                   symbol=params['BASESYMBOL'],
                                                                   quantity=params['remain'])
                                params['remain'] = 0

                            params['tp1done']= False

                            params[ 'tp2donesell']= False
                            params['Initial'] = "SHORT"
                            params['Ep'] =params["ltp"]
                            params['tp1val'] = params["ltp"] - params["Target1"]
                            params['tp2'] = params["ltp"] - params["Target2"]
                            params['remain'] = params['Quantity']
                            OrderLog = f"{timestamp} Sell @ {symbol_value} @ {params['ltp']}, tp1: {params['tp1val'] },tp2:{params['tp2']}"
                            print(OrderLog)
                            write_to_order_logs(OrderLog)
                            AliceBlueIntegration.NormalSell(producttype=params["producttype"], exch=params['Segement'],
                                                           symbol=params['BASESYMBOL'], quantity=params['Quantity'])

                        if params['Segement'] == "NSE":
                            if params['Initial'] == "BUY" and params['remain'] == params['Quantity']:
                                AliceBlueIntegration.buyexit(quantity=params["remain"], exch=params['exch'],
                                                             symbol=params['BASESYMBOL'],
                                                             expiry_date=params['aliceexp'],
                                                             strike=params["callstrike"], call=True,
                                                             producttype=params["producttype"])

                                OrderLog = (f"{timestamp} Buy STOP AND REVERSE@ {symbol_value} , exit contract ={params['callstrike']}"
                                            f" contract ={params['BASESYMBOL']},strike={params['callstrike']}CE, lots exited  {params['remain']}")
                                print(OrderLog)
                                write_to_order_logs(OrderLog)
                                params['remain'] = 0

                            params['Initial'] = "SHORT"
                            params['Ep'] = params["ltp"]
                            params['tp1done'] = False

                            params['tp2donesell'] = False
                            params['tp1val'] = params["ltp"] - params["Target1"]
                            params['tp2'] = params["ltp"] - params["Target2"]
                            params['remain'] = params['Quantity']
                            strikelist = getstrikes_put(
                                ltp=round_to_nearest(number=params["ltp"], nearest=params['strikestep']),
                                step=params['StrikeNumber'],
                                strikestep=params['strikestep'])
                            print("Strikes to check for delta put:", strikelist)
                            for strike in strikelist:
                                date_format = '%d-%b-%y'

                                delta = float(
                                    option_delta_calculation(symbol=params['BASESYMBOL'],
                                                             expiery=str(params['TradeExpiery']),
                                                             Tradeexp=params['TradeExpiery'],
                                                             strike=strike,
                                                             optiontype="PE",
                                                             underlyingprice=params["ltp"],
                                                             MODE=params["USEEXPIERY"]))
                                strikelist[strike] = delta

                            print("strikelist: ", strikelist)
                            final = get_max_delta_strike(strikelist)
                            print("Final strike: ", final)
                            params['putstrike'] = final
                            optionsymbol = f"NSE:{symbol}{params['TradeExpiery']}{final}PE"
                            params['exch'] = "NFO"
                            if symbol_value == "BANKEX" or symbol_value == "SENSEX":
                                params["exch"] = "BFO"

                            aliceexp = datetime.strptime(params['AliceblueTradeExp'], '%d-%b-%y')
                            aliceexp = aliceexp.strftime('%Y-%m-%d')
                            params['aliceexp'] = aliceexp
                            print("exch: ", params['exch'])
                            print("symbol: ", symbol)

                            AliceBlueIntegration.buy(quantity=int(params["Quantity"]), exch=params['exch'],
                                                     symbol=params['BASESYMBOL'],
                                                     expiry_date=params['aliceexp'],
                                                     strike=params['putstrike'], call=False,
                                                     producttype=params["producttype"])



                            OrderLog = f"{timestamp} Sell @ {symbol_value} option contract ={optionsymbol}@ {params['ltp']}, tp1: {params['tp1val'] },tp2:{params['tp2']}"
                            print(OrderLog)
                            write_to_order_logs(OrderLog)

                    #         buy



                    if ((params['Initial']== None or params['Initial']== "SHORT") and params["previousclose"]>=params["DayOpenVal"]
                            and params["DayOpenVal"] is not None and params['tp2donebuy'] ==False):

                        if params['Segement'] == "MCX":
                            if params['Initial'] == "SHORT" and params['remain'] == params['Quantity']:
                                OrderLog = f"{timestamp} SELL STOP AND REVERSE @ {symbol_value} @ {params['ltp']}, lots exited  {params['remain']}"
                                print(OrderLog)
                                write_to_order_logs(OrderLog)
                                AliceBlueIntegration.NormalSellExit(producttype=params["producttype"],
                                                                    exch=params['Segement'],
                                                                    symbol=params['BASESYMBOL'],
                                                                    quantity=params['remain'])
                                params['remain'] = 0



                            params['Initial'] = "BUY"
                            params['Ep'] = params["ltp"]
                            params['tp1val'] = params["ltp"]+params["Target1"]
                            params['tp2'] = params["ltp"]+params["Target2"]
                            params['tp1done'] = False

                            params['tp2donebuy'] = False
                            params['remain']=params['Quantity']
                            OrderLog = f"{timestamp} Buy @ {symbol_value} @ {params['ltp']}, tp1: {params['tp1val'] },tp2:{params['tp2']} "
                            print(OrderLog)
                            write_to_order_logs(OrderLog)
                            AliceBlueIntegration.NormalBuy(producttype=params["producttype"], exch=params['Segement'], symbol=params['BASESYMBOL'], quantity=params['Quantity'])

                        if params['Segement']=="NSE":
                            if params['Initial'] == "SHORT" and params['remain'] == params['Quantity']:
                                AliceBlueIntegration.buyexit(quantity=params["remain"], exch=params['exch'],
                                                             symbol=params['BASESYMBOL'],
                                                             expiry_date=params['aliceexp'],
                                                             strike=params["putstrike"], call=False,
                                                             producttype=params["producttype"])
                                OrderLog = f"{timestamp} SELL STOP AND REVERSE @ {symbol_value} contract ={params['BASESYMBOL']},strike={params['putstrike']}PE, lots exited  {params['remain']}"
                                print(OrderLog)
                                write_to_order_logs(OrderLog)
                                params['remain'] = params['Quantity'] - params['Tp1Qty']

                            params['Initial'] = "BUY"
                            params['Ep'] = params["ltp"]
                            params['tp1val'] = params["ltp"] + params["Target1"]
                            params['tp2'] = params["ltp"] + params["Target2"]
                            params['tp1done'] = False

                            params['tp2donebuy'] = False
                            params['remain'] = params['Quantity']
                            strikelist = getstrikes_call(
                                ltp=round_to_nearest(number=params["ltp"], nearest=params['strikestep']),
                                step=params['StrikeNumber'],
                                strikestep=params['strikestep'])
                            print("Strikes to check for delta call:", strikelist)
                            for strike in strikelist:
                                date_format = '%d-%b-%y'

                                delta = float(
                                    option_delta_calculation(symbol=params['BASESYMBOL'],
                                                             expiery=str(params['TradeExpiery']),
                                                             Tradeexp=params['TradeExpiery'],
                                                             strike=strike,
                                                             optiontype="CE",
                                                             underlyingprice=params["ltp"],
                                                             MODE=params["USEEXPIERY"]))
                                strikelist[strike] = delta

                            print("strikelist: ", strikelist)
                            final = get_max_delta_strike(strikelist)
                            print("Final strike: ", final)
                            params['callstrike'] = final

                            optionsymbol = f"NSE:{params['BASESYMBOL']}{params['TradeExpiery']}{final}CE"
                            params['exch'] = "NFO"
                            if symbol_value == "BANKEX" or symbol_value == "SENSEX":
                                params["exch"] = "BFO"
                            aliceexp = datetime.strptime(params['AliceblueTradeExp'], '%d-%b-%y')
                            aliceexp = aliceexp.strftime('%Y-%m-%d')
                            params['aliceexp'] = aliceexp
                            print("exch: ", params['exch'])

                            AliceBlueIntegration.buy(quantity=int(params["Quantity"]), exch=params['exch'],
                                                     symbol=params['BASESYMBOL'],
                                                     expiry_date=params['aliceexp'],
                                                     strike=params['callstrike'], call=True,
                                                     producttype=params["producttype"])


                            OrderLog=f"{timestamp} Buy @ {symbol_value} option contract ={optionsymbol}, tp1: {params['tp1val'] },tp2:{params['tp2']} "
                            print(OrderLog)
                            write_to_order_logs(OrderLog)

                    if params['Initial'] == "SHORT":
                        if  params['tsl'] is not None and params["ltp"] <= params['tsl'] and params['tp1done'] == True:
                            params['tsl']=None
                            params['Initial']=None
                            OrderLog = f"{timestamp} Buy Exit tsl @ {symbol_value} @ {params['ltp']}, lots exited  {params['remain']}"
                            print(OrderLog)
                            write_to_order_logs(OrderLog)
                            AliceBlueIntegration.NormalSellExit(producttype=params["producttype"],
                                                                exch=params['Segement'],
                                                                symbol=params['BASESYMBOL'],
                                                                quantity=params['remain'])
                            params['remain'] = 0

                        if params['tp1val'] is not None and params["ltp"] <= params['tp1val'] :
                            if params['Segement'] == "MCX":
                                params['tp1val'] = None
                                params["tsl"] = params['Ep']
                                params['tp1done'] = True

                                OrderLog = f"{timestamp} Sell Exit tp1 @ {symbol_value} @ {params['ltp']}, lots exited  {params['Tp1Qty']}"
                                print(OrderLog)
                                write_to_order_logs(OrderLog)
                                AliceBlueIntegration.NormalSellExit(producttype=params["producttype"],
                                                                    exch=params['Segement'],
                                                                    symbol=params['BASESYMBOL'],
                                                                    quantity=params['Tp1Qty'])
                                params['remain'] = params['Quantity'] - params['Tp1Qty']

                            if params['Segement'] == "NSE":
                                params['tp1val'] = None
                                params["tsl"] = params['Ep']
                                params['tp1done'] = True

                                AliceBlueIntegration.buyexit(quantity=params["Tp1Qty"], exch=params['exch'],
                                                             symbol=params['BASESYMBOL'],
                                                             expiry_date=params['aliceexp'],
                                                             strike=params["putstrike"], call=False,
                                                             producttype=params["producttype"])
                                OrderLog = f"{timestamp} Sell Exit tp1 @ {symbol_value} contract ={params['BASESYMBOL']},strike={params['putstrike']}PE, lots exited  {params['Tp1Qty']}"
                                print(OrderLog)
                                write_to_order_logs(OrderLog)
                                params['remain'] = params['Quantity'] - params['Tp1Qty']

                        if params['tp2'] is not None and params["ltp"] <= params['tp2'] :
                            if params['Segement'] == "MCX":
                                params['tp2'] = None
                                params['tsl'] = None

                                params['tp2donesell'] = True
                                params['Initial'] = None
                                OrderLog = f"{timestamp} Sell Exit tp2 @ {symbol_value} @ {params['ltp']}, lots exited  {params['remain']}"
                                print(OrderLog)
                                write_to_order_logs(OrderLog)
                                AliceBlueIntegration.NormalSellExit(producttype=params["producttype"],
                                                                    exch=params['Segement'],
                                                                    symbol=params['BASESYMBOL'],
                                                                    quantity=params['remain'])
                                params['remain'] = 0

                            if params['Segement'] == "NSE":
                                params['tp2'] = None
                                params['tsl'] = None

                                params['tp2donesell'] = True
                                params['Initial'] = None
                                AliceBlueIntegration.buyexit(quantity=params["remain"], exch=params['exch'],
                                                             symbol=params['BASESYMBOL'],
                                                             expiry_date=params['aliceexp'],
                                                             strike=params["putstrike"], call=False,
                                                             producttype=params["producttype"])
                                OrderLog = f"{timestamp} Sell Exit tp2 @ {symbol_value} contract ={params['BASESYMBOL']},strike={params['putstrike']}PE, lots exited  {params['remain']}"
                                print(OrderLog)
                                write_to_order_logs(OrderLog)
                                params['remain'] =0


                    if params['Initial'] == "BUY":
                        if  params['tsl'] is not None and params["ltp"] <= params['tsl'] and params['tp1done'] == True:
                            params['tsl']=None
                            params['Initial']=None
                            OrderLog = f"{timestamp} Buy Exit TSL @ {symbol_value} @ {params['ltp']}, lots exited  {params['remain']} "
                            print(OrderLog)
                            write_to_order_logs(OrderLog)
                            AliceBlueIntegration.NormalBuyExit(producttype=params["producttype"],
                                                               exch=params['Segement'],
                                                               symbol=params['BASESYMBOL'],
                                                               quantity=params['remain'])
                            params['remain']=0

                        if params['tp1val'] is not None and  params["ltp"] >= params['tp1val'] :
                            if params['Segement'] == "MCX":
                                params['tp1val'] = None
                                params["tsl"] = params['Ep']
                                params['tp1done'] = True
                                OrderLog = f"{timestamp} Buy Exit Tp1 @ {symbol_value} @ {params['ltp']}, lots exited  {params['Tp1Qty']} "
                                print(OrderLog)
                                write_to_order_logs(OrderLog)
                                AliceBlueIntegration.NormalBuyExit(producttype=params["producttype"],
                                                                   exch=params['Segement'],
                                                                   symbol=params['BASESYMBOL'],
                                                                   quantity=params['Tp1Qty'])
                                params['remain'] = params['Quantity'] - params['Tp1Qty']

                            if params['Segement'] == "NSE":
                                params['tp1val'] = None
                                params["tsl"] = params['Ep']
                                params['tp1done'] = True
                                AliceBlueIntegration.buyexit(quantity=params["Tp1Qty"], exch=params['exch'],
                                                             symbol=params['BASESYMBOL'],
                                                             expiry_date=params['aliceexp'],
                                                             strike=params["callstrike"], call=True,
                                                             producttype=params["producttype"])

                                OrderLog = f"{timestamp} Buy Exit Tp1 @ {symbol_value} , exit contract ={params['callstrike']} contract ={params['BASESYMBOL']},strike={params['callstrike']}CE, lots exited  {params['Tp1Qty']}"
                                print(OrderLog)
                                write_to_order_logs(OrderLog)
                                params['remain'] = params['Quantity'] - params['Tp1Qty']

                        if params['tp2'] is not None and params["ltp"] >= params['tp2']:
                            if params['Segement'] == "MCX":
                                params['tp2'] = None
                                params['tsl'] = None

                                params['tp2donebuy'] = True
                                params['Initial'] = None
                                OrderLog = f"{timestamp} Buy Exit tp2 @ {symbol_value} @ {params['ltp']}, lots exited  {params['remain']} "
                                print(OrderLog)
                                write_to_order_logs(OrderLog)
                                AliceBlueIntegration.NormalBuyExit(producttype=params["producttype"],
                                                                   exch=params['Segement'],
                                                                   symbol=params['BASESYMBOL'],
                                                                   quantity=params['remain'])
                                params['remain'] = 0

                            if params['Segement'] == "NSE":
                                params['tp2'] = None
                                params['tsl'] = None
                                params['Initial'] = None
                                params['tp2donebuy'] = True
                                AliceBlueIntegration.buyexit(quantity=params["remain"], exch=params['exch'],
                                                             symbol=params['BASESYMBOL'],
                                                             expiry_date=params['aliceexp'],
                                                             strike=params["callstrike"], call=True,
                                                             producttype=params["producttype"])

                                OrderLog = f"{timestamp} Buy Exit Tp2 @ {symbol_value} , exit contract ={params['callstrike']} contract ={params['BASESYMBOL']},strike={params['callstrike']}CE, lots exited  {params['remain']}"
                                print(OrderLog)
                                write_to_order_logs(OrderLog)
                                params['remain'] = 0

    except Exception as e:
        print("Error in main strategy : ", str(e))
        traceback.print_exc()


while True:
    main_strategy()
    time.sleep(5)
