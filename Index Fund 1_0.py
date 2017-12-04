import urllib2
import json
import time
from poloniex import poloniex


N = 11  # number of currencies in the fund excluding BTC
var = .03  # % variance between assets
All = 1.0 / float(N + 1)  # % per asset

pt = 'https://poloniex.com/public?command=returnTicker'  # polo ticker command string
ct = 'https://api.coinmarketcap.com/v1/ticker/?limit='  # cmc ticker command string
minVal = .00000001  # minimum amount on polo
delay = 14  # seconds

api = 'YOUR POLONIEX API KEY HERE'  # api key from polo
sec = 'YOUR POLONIEX SECRET KEY HERE'  # secret key from polo


def current_list(Cd):
    for i in Cd.keys():
        if float(Cd[i]) == 0:
            Cd.pop(i, None)
    Cl = Cd.keys()  # list of current holdings on polo
    return (Cl)

def wait(orderNumber, curr, amount_curr, den, isBuy):
    tlapse = 0
    OpenOrders = poloniex.returnOpenOrders(poloniex(api, sec), 'BTC_' + curr)
    time.sleep(delay)
    while OpenOrders != []:  # [] if no open orders
        if tlapse > 30:
            # cancel order
            print('cancel')
            poloniex.cancel(poloniex(api, sec), 'BTC_' + str(curr),orderNumber)
            if isBuy == True:
                print('rebuy')
                buydef(curr, amount_curr, den)
            else:
                print('resell')
                selldef(curr, amount_curr, den)
            time.sleep(delay)
        else:
            print('t:' + str(tlapse))
            time.sleep(delay)
            tlapse += 1
        OpenOrders = poloniex.returnOpenOrders(poloniex(api, sec), 'BTC_' + str(curr))

def buydef(curr, amount_curr, den):
    print(str(type(curr)) + ' ' + str(curr))
    print(str(type(amount_curr)) + ' ' + str(amount_curr))
    print(str(type(den)) + ' ' + str(den))
    rate = json.load(urllib2.urlopen(pt))['BTC_' + curr]['last']
    print(rate)
    time.sleep(delay)
    Order = poloniex.buy(poloniex(api, sec), 'BTC_' + curr, str(float(rate) - minVal), str(amount_curr))
    time.sleep(delay)
    print(Order['orderNumber'])
    time.sleep(delay)
    wait(Order['orderNumber'],curr, amount_curr, den, True)

def selldef(curr, amount_curr, den):
    rate = json.load(urllib2.urlopen(pt))['BTC_' + curr]['last']
    time.sleep(delay)
    Order = poloniex.sell(poloniex(api, sec), 'BTC_' + curr, str(float(rate) + minVal), str(amount_curr))
    time.sleep(delay)
    wait(Order['orderNumber'],curr, amount_curr, den, False)

def find_high(Cd, Cl, Tpt, den):
    high = 0
    for i in Cl:
        if i != 'BTC':
            rate = Tpt['BTC_' + str(i)]['last']
            per = float(rate) * float(Cd[i]) / den
            if per > high:
                high = per
                curr = i
    return (high, curr)

def find_low(Cd, Cl, Tpt, den):
    low = 1
    for i in Cl:
        if i != 'BTC':
            rate = Tpt['BTC_' + str(i)]['last']
            per = float(rate) * float(Cd[i]) / den
            if per < low:
                print(low)
                low = per
                curr = i
                print(i)
                print(per)
    return (low, curr)


while True:
    # Find Largest 'N' Volumes Shared by Polo and CMC
    Dl = []  # Desired List - list of top 'N' volumes
    T_size = 3 * N
    # Find Largest N Volumes Shared by Polo and CMC
    Tpt = json.load(urllib2.urlopen(pt))
    while len(Dl) != N+1:
        Dl = []
        T = json.load(urllib2.urlopen(ct + str(T_size)))
        print(T)
        # [{"id": "bitcoin","name": "Bitcoin","symbol": "BTC","rank": "1","price_usd": "4844.27","price_btc": "1.0",
        # "24h_volume_usd": "2502080000.0","market_cap_usd": "80114173940.0","available_supply": "16537925.0",
        # "total_supply": "16537925.0","percent_change_1h": "-0.42","percent_change_24h": "2.92",
        # "percent_change_7d": "10.69","last_updated": "1504302871"},{"id": "ethereum","name": "Ethereum",
        # "symbol": "ETH","rank": "2","price_usd": "386.736","price_btc": "0.0795598","24h_volume_usd": "860910000.0",
        # "market_cap_usd": "36497866965.0","available_supply": "94374113.0","total_supply": "94374113.0",
        # "percent_change_1h": "0.0","percent_change_24h": "0.92","percent_change_7d": "16.45",
        # "last_updated": "1504302866"},
        lenDl = 0
        for i in range(0, len(T) - 1):
            if lenDl < N+1:
                try:
                    print(T[i]['symbol'])
                    Tpt['BTC_' + str(T[i]['symbol'])]
                    print('try')
                    Dl.append(T[i]['symbol'])
                    print(Dl)
                except KeyError:
                    print('continue')
                    print(T[i]['symbol'])
                    if T[i]['symbol'] == 'BTC':
                        Dl.append(u'BTC')
                    continue
            lenDl = len(Dl)
        print(lenDl)
        if lenDl < N+1:
            T_size += 3 * (N - lenDl)
    T = []
    print(Dl)
    # Leaves Dl, a list of desired currencies

    # CANCEL OPEN ORDERS
    # make dictionary of open orders
    cancelled = 0
    while cancelled == 0:
        Oo = poloniex.returnOpenOrders(poloniex(api, sec), 'all')
        # {"BTC_1CR":[],"BTC_AC":[{"orderNumber":"120466","type":"sell","rate":"0.025","amount":"100","total":"2.5"},
        # {"orderNumber":"120467","type":"sell","rate":"0.04","amount":"100","total":"4"}], ... }
        Ool = Oo.keys()
        i = 0
        while len(Ool) != 0:
            try:
                poloniex.cancel(poloniex(api, sec), Ool[0], Oo[Ool[0]][0]['orderNumber'])
                del (Oo[Ool[0]][0])
                i += 1
            except IndexError:
                del (Ool[0])
        if i == 0:
            cancelled = 1
        else:
            time.sleep(delay)
    Oo = {}

    time.sleep(7)
    # RETRIEVE CURRENT HOLDINGS
    Cd = poloniex.returnBalances(poloniex(api, sec))
    Cl = current_list(Cd)
    print(Cl)
    print(Cd)

    # BUILD TOTAL BTC VALUE
    den = 0
    for i in Cl:
        if i == 'BTC':
            den += float(Cd[i])
        else:
            price = Tpt['BTC_' + str(i)]['last']
            den += float(Cd[i]) * float(price)
    print(den)


    btc_needed = 0
    # BuyList = []

    # SELL
    print('SELL PROTOCOL')
    for i in Cl:
        if i != 'BTC':
            j = 0
            inDl = 0
            while j < len(Dl) and inDl == 0:
                if i == Dl[j]:
                    print('match; check')
                    inDl = 1
                    rate = Tpt['BTC_' + str(i)]['last']
                    print('curr: ' + str(i) + '   rate: ' + rate)
                    per = float(rate) * float(Cd[i]) / den
                    print(per)
                    if per > All + var:  # Sell excess of currencies which are outside of allocation amount
                        print('sell excess')
                        selldef(i, float(Cd[i]), den)
                    elif per < All - var:
                        btc_needed += All * den - float(Cd[i]) * float(rate)  # in currency
                        # BuyList.append({i:Cd[i]})
                        # print(BuyList)
                else:  # go to the next in the Dl
                    print('next')
                    j += 1
            print(btc_needed)
            # Sell all of the amount you have of a currency that dropped out of the Desired List
            if inDl == 0:
                print('not in Dl')
                rate = Tpt['BTC_' + str(i)]['last']
                amount = float(Cd[i])
                sell_all = True
                print('sell all')
                selldef(i, float(Cd[i]), den)

    # ACCOUNT FOR btc_needed OF CURRENCIES NOT IN Cl
    for i in Dl:
        try:
            Cd[i]
        except KeyError:
            btc_needed += All * den
            continue

    # MAKE SURE THERE'S ENOUGH BTC TO BUY LOW CURRENCIES
    btc_needed = 1.01 * btc_needed  # for excess BTC to make sure calculation time doesn't interfere with rate based calculations

    Cd = poloniex.returnBalances(poloniex(api, sec))
    Cl = current_list(Cd)
    while Cd['BTC'] < btc_needed:
        high = find_high(Cd, Cl, Tpt, den)
        if btc_needed > (high[0] - All) * den:
            rate = Tpt['BTC_' + str(high[1])]['last']
            amount = float(Cd[high[1]]) - All * den * float(rate)
            selldef(high[1], amount, den)
        else:
            selldef(high[1], btc_needed, den)
        Cd = poloniex.returnBalances(poloniex(api, sec))
        Cl = current_list(Cd)
        # calculate needed btc
        btc_needed = 0
        for i in Cl:
            rate = Tpt['BTC_' + str(i)]['last']
            per = float(rate) * float(Cd[i]) / den
            if per < All - var:
               btc_needed += All * den - float(Cd[i]) * float(rate)  # in currency
               #BuyList.append({i: Cd[i]})
               #print(BuyList)

    # BUY
    t = 0
    print('BUY')
    for i in Dl:
        if i != 'BTC':
            rate = Tpt['BTC_' + str(i)]['last']
            try:
                per = float(rate) * float(Cd[i]) / den
                print(str(i) + '   per: ' + str(round(per*100,4)))
                if per < All - var:
                    amount = All * den / float(rate) - float(Cd[i])
                    print(str(type(i)) + ' ' + str(i))
                    print(str(type(amount)) + ' ' + str(amount))
                    print(str(type(den)) + ' ' + str(den))
                    buydef(i, amount, den)
                elif abs(per - All) > t:
                    t = abs(per - All)
            except KeyError:
                amount = All * den / float(rate)
                print(str(type(i)) + ' ' + str(i))
                print(str(type(amount)) + ' ' + str(amount))
                print(str(type(den)) + ' ' + str(den))
                buydef(i, amount, den)
                continue
    print('End BUY')

    Cd = poloniex.returnBalances(poloniex(api, sec))
    Cl = current_list(Cd)

    #Step 2
    while float(Cd['BTC']) < (All - var) * den or float(Cd['BTC']) > (All + var) * den:
        print(Cd['BTC'])
        if float(Cd['BTC']) < (All - var) * den:
            print('btc low')
            high = find_high(Cd, Cl, Tpt, den)  # (high percentage, currency)
            print(high)
            rate = Tpt['BTC_' + str(high[1])]['last']
            print(rate)
            amount = round(float(Cd[high[1]]) - All * den / float(rate),8)
            print(amount)
            print(str(type(high[1])))
            print(str(type(amount)))
            print(str(type(den)))
            selldef(high[1], amount, den)
            print('selldeffed')
        else:
            print('btc high')
            low = find_low(Cd, Cl, Tpt, den)  # (low percentage, currency)
            print(low)
            rate = Tpt['BTC_' + str(low[1])]['last']
            print(rate)
            amount = round(All * den / float(rate) - float(Cd[low[1]]),8)
            print(amount)
            print(str(type(low[1])))
            print(str(type(amount)))
            print(str(type(den)))
            buydef(low[1], amount, den)
            print('buydeffed')
        time.sleep(delay)
        Cd = poloniex.returnBalances(poloniex(api, sec))
        Cl = current_list(Cd)
    # Am I broke?
    if den < .05:
        break
    print(str(var - t))
    if var - t > .015:
        time.sleep((var - t) * 10000 * delay)
    else:
        time.sleep(60 * delay)
