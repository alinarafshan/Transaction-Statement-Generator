"""
A Transaction Statement Generator.
Created by Ali Narafshan Oct 2nd, 2017
"""


# helper function for a string representation of shares BOUGHT
def bought_to_str(shares, ticker, price):
    """ Returns a string representation of shares BOUGHT """
    return ('    - You bought ' + shares + ' shares of ' +
            ticker + ' at a price of ' + price + ' per share\n')


# helper function for a string representation of shares SOLD
def sold_to_str(shares, ticker, price, profit):
    """ Returns a string representation of shares SOLD """
    return ('    - You sold ' + shares + ' shares of ' + ticker
            + ' at a price of ' + price + ' per share for a '
            + ('profit' if float(profit[1:]) >= 0 else 'loss') + ' of '
            + profit + '\n')


# helper function for a string representation of all shares OWNED
def shares_to_str(dic1, income):
    """ Returns a string representation of all shares OWNED """
    result = ''
    for ticker in dic1:
        if dic1[ticker][0] != 0:
            result += ('    - ' + str(dic1[ticker][0]) + ' shares of ' + ticker
                       + ' at ' + '${:.2f}'.format(dic1[ticker][1]) +
                       ' per share\n')
    result += '    - ' + ('${:.2f}'.format(income) if income != 0
                          else '$0') + ' of dividend income\n'
    return result


# helper function for a string representation of shares SPLIT
def split_to_str(stock, split, shares):
    """ Returns a string representation of shares SPLIT """
    return ('    - ' + stock + ' split ' + split + ' to 1, and you have ' +
            str(shares) + ' shares\n')


# helper function for a string representation of dividend income
def dividend_to_str(stock, dividend, shares):
    """ Returns a string representation of dividend income """
    return ('    - ' + stock + ' paid out ' + '${:.2f}'.format(float(dividend))
            + ' dividend per share, and you have ' + str(shares) + ' shares\n')


# helper function to check stock actions and modify results
def stock_action_checker(stock_lst_element, temp_tickers, dividend_obj,
                         tickers, action_prev_date, stock_element_date):
    """ Returns a string representation of modified info
        according to stock action changes """
    result = ''
    temp_ticker = stock_lst_element['stock']
    temp_dividend = stock_lst_element['dividend']
    temp_split = stock_lst_element['split']

    # checks to see if stock is owned and acts accordingly
    if temp_ticker in temp_tickers:
        if temp_dividend != '':
            dividend_obj[0] += (float(temp_dividend) *
                                temp_tickers[temp_ticker][0])
        if temp_split != '':
            prev_total_paid = (temp_tickers[temp_ticker][0] *
                               temp_tickers[temp_ticker][1])
            tickers[temp_ticker][0] = (
                temp_tickers[temp_ticker][0] * int(temp_split))
            tickers[temp_ticker][1] = round(
                prev_total_paid / temp_tickers[temp_ticker][0],
                2)

        # checks if the date is already recorded in result and
        # adds stock actions to it
        if action_prev_date == stock_element_date:
            if temp_split != '':
                result += split_to_str(temp_ticker, temp_split,
                                       tickers[temp_ticker][0])
            if temp_dividend != '':
                result += dividend_to_str(
                    temp_ticker, temp_dividend,
                    tickers[temp_ticker][0])

        # adds new date in result if it doesn't already exist
        # adds stock actions to it
        else:
            result += ('On ' + stock_element_date.replace('/', '-')
                       + ', you have:\n')
            result += shares_to_str(tickers, dividend_obj[0])
            result += '  Transactions:\n'
            if temp_split != '':
                result += split_to_str(temp_ticker, temp_split,
                                       tickers[temp_ticker][0])
            if temp_dividend != '':
                result += dividend_to_str(temp_ticker, temp_dividend,
                                          tickers[temp_ticker][0])
    return result


# main function
def statement_generator(action_lst, stock_lst):
    """ Returns a string representation of stock statement
        according to stock changes """

    result = '"""\n'
    temp_result = '  Transactions:\n'
    temp_tickers = {}
    tickers = {}
    dividend_obj = [0]
    j = 0

    # checks action list has elements in it; if not, it doesn't run the program
    if len(action_lst) > 0:
        action_prev_date = action_lst[0]['date'][:10]

        # checks stock list has elements in it
        if len(stock_lst) > 0:
            stock_element_date = stock_lst[0]['date']
        else:
            stock_element_date = None

        # traverses action list
        for i in range(len(action_lst)):
            cur_ticker = action_lst[i]['ticker']
            cur_shares = int(action_lst[i]['shares'])
            cur_price = float(action_lst[i]['price'])
            action_cur_date = action_lst[i]['date'][:10]

            # records changes of previous date in result
            # when next element's date changes
            if action_prev_date != action_cur_date:
                result += ('On ' + action_prev_date.replace('/', '-')
                           + ', you have:\n')
                result += shares_to_str(tickers, dividend_obj[0])
                result += temp_result
                temp_result = '  Transactions:\n'
                temp_tickers = tickers

                # traverses stock list and records changes in result if any
                # element's date is before the next element's date in action
                # list or there is no more element in action list
                while (stock_element_date is not None
                       and (action_cur_date > stock_element_date or
                            action_cur_date is None)
                       and len(stock_lst) > j):
                    if stock_element_date > action_lst[0]['date']:
                        result += stock_action_checker(stock_lst[j],
                                                       temp_tickers,
                                                       dividend_obj, tickers,
                                                       action_prev_date,
                                                       stock_element_date)
                    j += 1
                    if len(stock_lst) > j:
                        stock_element_date = stock_lst[j]['date']
            action_prev_date = action_cur_date

            # updates shares accordingly if stock was previously purchased
            if cur_ticker in tickers:
                previous_shares = tickers[cur_ticker][0]
                previous_price = tickers[cur_ticker][1]

                # for shares sold bought
                if action_lst[i]['action'] == 'BUY':
                    total_paid = (previous_shares * previous_price +
                                  cur_shares * cur_price)
                    total_shares = previous_shares + cur_shares
                    price_per_share = round(total_paid / total_shares, 2)
                    tickers[cur_ticker] = [total_shares, price_per_share]
                    temp_result += bought_to_str(str(cur_shares), cur_ticker,
                                                 '${:.2f}'.format(cur_price))

                # for shares sold
                else:
                    cur_profit = ((cur_price - tickers[cur_ticker][1]) *
                                  cur_shares)
                    tickers[cur_ticker][0] -= int(action_lst[i]['shares'])
                    temp_result += sold_to_str(str(cur_shares), cur_ticker,
                                               '${:.2f}'.format(cur_price),
                                               '${:.2f}'.format(cur_profit))

            # add stock to tickers if it doesn't exist
            else:
                tickers[cur_ticker] = [cur_shares, cur_price]
                temp_result += bought_to_str(str(cur_shares), cur_ticker,
                                             '${:.2f}'.format(cur_price))

        # adds the last date of action list to the result
        result += 'On ' + action_prev_date.replace('/', '-') + ', you have:\n'

        # checks for changes in stock list for the last date of action list
        if action_prev_date == stock_element_date:
            while (stock_element_date is not None and len(stock_lst) > j
                   and action_prev_date == stock_element_date):
                temp_result += stock_action_checker(stock_lst[j], temp_tickers,
                                                    dividend_obj, tickers,
                                                    action_prev_date,
                                                    stock_element_date)
                j += 1
                if len(stock_lst) > j:
                    stock_element_date = stock_lst[j]['date']
            result += shares_to_str(tickers, dividend_obj[0])

        # adds the last record of action list to the result if no changes
        else:
            result += shares_to_str(tickers, dividend_obj[0])
        result += temp_result

        # traverses stock list and records changes in result if there are
        # elements in stock list with date equal to the last element's date in
        # action list or if there are elements with date later than the last
        # element's date in in action list
        while stock_element_date is not None and len(stock_lst) > j:
            temp_tickers = tickers
            result += stock_action_checker(stock_lst[j], temp_tickers,
                                           dividend_obj, tickers,
                                           action_prev_date,
                                           stock_element_date)
            j += 1
            if len(stock_lst) > j:
                stock_element_date = stock_lst[j]['date']

    return result + '"""'


if __name__ == '__main__':

    actions = [
                {'date': '1992/07/14 11:12:30', 'action': 'BUY',
                 'price': '12.3', 'ticker': 'AAPL', 'shares': '500'},
                {'date': '1992/09/13 11:15:20', 'action': 'SELL',
                 'price': '15.3', 'ticker': 'AAPL', 'shares': '100'},
                {'date': '1992/10/14 15:14:20', 'action': 'BUY',
                 'price': '20', 'ticker': 'MSFT', 'shares': '300'},
                {'date': '1992/10/17 16:14:30', 'action': 'SELL',
                 'price': '20.2', 'ticker': 'MSFT', 'shares': '200'},
                {'date': '1992/10/19 15:14:20', 'action': 'BUY',
                 'price': '21', 'ticker': 'MSFT', 'shares': '500'},
                {'date': '1992/10/23 16:14:30', 'action': 'SELL',
                 'price': '18.2', 'ticker': 'MSFT', 'shares': '600'},
                {'date': '1992/10/25 10:15:20', 'action': 'SELL',
                 'price': '20.3', 'ticker': 'AAPL', 'shares': '300'},
                {'date': '1992/10/25 16:12:10', 'action': 'BUY',
                 'price': '18.3', 'ticker': 'MSFT', 'shares': '500'}
    ]

    stock_actions = [
                        {'date': '1992/08/14', 'dividend': '0.10', 'split': '',
                         'stock': 'AAPL'},
                        {'date': '1992/09/01', 'dividend': '', 'split': '3',
                         'stock': 'AAPL'},
                        {'date': '1992/10/15', 'dividend': '0.20', 'split': '',
                         'stock': 'MSFT'},
                        {'date': '1992/10/16', 'dividend': '0.20', 'split': '',
                         'stock': 'ABC'}
    ]

    print(statement_generator(actions, stock_actions))
