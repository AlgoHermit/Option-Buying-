from pya3 import *
close_thread = False
stk = None
ep = None
ty = None
exp = None
def begin():
    import yfinance as yf
    from datetime import date, datetime, timedelta
    from time import sleep
    # from strategies import crossover, crossunder
    # import orders
    import telepot 
    import pytz
    from threading import Thread



 # Initialising the telegram bot
    token = '''Enter telegram token id''' # Optbot
    receiver = '''Enter telegram receiver id'''
    Bot = telepot.Bot(token)
    response = Bot.getUpdates()

    #Alice blue instance 
    username = '''Enter Alice blue username'''
    api_key = '''Enter APIkey'''
    alice = Aliceblue(user_id=username,api_key=api_key)
    print(alice.get_session_id())

    alice.get_contract_master("NFO") # Getting the NFO master contract for searching option LTP
    

# Dates
    check_holiday = yf.download(tickers='IOC.NS', period='5D', interval='1d')

    today =  datetime.today() # local
    todayIST = today.astimezone(pytz.timezone('Asia/Kolkata'))
    prev_day = (todayIST - timedelta(days=1)).strftime("%Y-%m-%d")
    days_back = 0 # This is for passing lookback days for get_hist() if last day was a holiday
    if prev_day not in check_holiday.index:
        x = 1
        while prev_day not in check_holiday.index:
            x += 1
            prev_day = (todayIST - timedelta(days=x)).strftime("%Y-%m-%d")
        days_back = x+1

    # prev_day = prev_day.strftime("%Y-%m-%d")
    todayIST = todayIST.strftime("%Y-%m-%d")

    print(f"Todays date:{todayIST}, Last working day:{prev_day}")
    Bot.sendMessage(receiver, f"Todays date:{todayIST}\nLast working day:{prev_day}")

    LTP = 0
    socket_opened = False
    subscribe_flag = False
    subscribe_list = []

    def socket_open():  # Socket open callback function
        print("Connected")
        nonlocal socket_opened
        socket_opened = True
        if subscribe_flag:  # This is used to resubscribe the script when reconnect the socket.
            alice.subscribe(subscribe_list)

    def socket_close():  # On Socket close this callback function will trigger
        nonlocal socket_opened, LTP
        socket_opened = False
        LTP = 0
        print("Closed")

    def socket_error(message):  # Socket Error Message will receive in this callback function
        nonlocal LTP
        LTP = 0
        print("Error :", message)

    def feed_data(message):  # Socket feed data will receive in this callback function
        nonlocal LTP, subscribe_flag
        feed_message = json.loads(message)
        if feed_message["t"] == "ck":
            print("Connection Acknowledgement status :%s (Websocket Connected)" % feed_message["s"])
            subscribe_flag = True
            print("subscribe_flag :", subscribe_flag)
            print("-------------------------------------------------------------------------------")
            pass
        elif feed_message["t"] == "tk":
            print("Token Acknowledgement status :%s " % feed_message)
            if 'lp' in feed_message: LTP = float(feed_message['lp'])
            print("-------------------------------------------------------------------------------")
            pass
        

    # Socket Connection Request
    alice.start_websocket(socket_open_callback=socket_open, socket_close_callback=socket_close,
                        socket_error_callback=socket_error, subscription_callback=feed_data, run_in_background=True,market_depth=False)

    while not socket_opened:
        pass
    


    def callopt():
        C = True
        alice.subscribe([alice.get_instrument_by_symbol('INDICES','NIFTY 50')])
        sleep(0.3)
        pp = LTP
        
        while C:
            if close_thread:break
            alice.subscribe([alice.get_instrument_by_symbol('INDICES','NIFTY 50')])
            sleep(0.2)
            diff = round(abs(100-(LTP*100/pp)), 4)
            try:
                Bot.sendMessage(receiver, f'Pivot Price: {pp}\nLTP: {LTP}\nChng: {diff}')
            except:
                pass
            if LTP < pp and diff >= 0.1:
                print(f'Exit @ {LTP}')
                alice.subscribe([alice.get_instrument_for_fno(exch="NFO",symbol='NIFTY', expiry_date=exp, is_fut=False,strike=stk, is_CE=True)]) 
                sleep(0.5)
                print(f'P/L: {round((LTP-ep)*50, 2)}')
                Bot.sendMessage(receiver, f'Exit @ {LTP}\nP/L: {round((LTP-ep)*50, 2)}') 
                C = False
                

            elif LTP > pp and diff >= 0.03:
                pp = LTP
                print(f'Trailing Stop moved to {pp}')
                Bot.sendMessage(receiver, f'Trailing Stop moved to {pp}') 
            sleep(1)
              
    def putopt():
        P = True
        alice.subscribe([alice.get_instrument_by_symbol('INDICES','NIFTY 50')])
        sleep(0.3)
        pp = LTP
        while P:
            if close_thread: break
            alice.subscribe([alice.get_instrument_by_symbol('INDICES','NIFTY 50')])
            sleep(0.2)
            diff = round(abs(100-(LTP*100/pp)), 4)
            try:
                Bot.sendMessage(receiver, f'Pivot Price: {pp}\nLTP: {LTP}\nChng: {diff}')
            except:
                pass
            if LTP > pp and diff >= 0.1:
                print(f'Exit @ {LTP}')
                alice.subscribe([alice.get_instrument_for_fno(exch="NFO",symbol='NIFTY', expiry_date=exp, is_fut=False,strike=stk, is_CE=False)])
                sleep(0.5)
                Bot.sendMessage(receiver, f'Exit @ {LTP}\nP/L: {round((LTP-ep)*50, 2)}')
                print(f'P/L: {round((LTP-ep)*50, 2)}')                
                P = False
                

            elif LTP < pp and diff >= 0.03:
                pp = LTP
                print(f'Trailing Stop moved to {pp}')
                Bot.sendMessage(receiver, f'Trailing Stop moved to {pp}')
            sleep(1)

    def main():
            while True:
                today =  datetime.today()
                time = today.astimezone(pytz.timezone('Asia/Kolkata')).strftime("%H:%M:%S")
                if time >= "09:15:00":
                    print('Start running...')
                    Bot.sendMessage(receiver, 'Start running...\n(Option buying)')
                    Bot.sendMessage(receiver, f"Option selected: {ty}\nStrike: {stk}\nEntry Price: {ep}\nExpiry: {exp}")
                    if ty.lower() == 'call':
                        callopt()
                    else:
                        putopt()
                    # callopt()

                    while True:
                        print('FINISHED RUNNING!!!')
                        sleep(180)
                else: 
                        print(f"Waiting for market open...{time}")
                        Bot.sendMessage(receiver, f"Waiting for market open...{time}")
                        sleep(60)

    main()
