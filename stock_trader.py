import yfinance as yf



users = {}
current_user = None
STARTING_BALANCE = 10000.00

POPULAR_STOCKS = ["AAPL", "MSFT", "NVDA", "AMZN", "GOOGL"]


def register():
    print("\n--- Create Account ---")
    username = input("Enter a username: ")
    password = input("Enter a password: ")

    if not username or not password:
        print("Username and password cannot be empty.")
        return

    if username in users:
        print("Username already exists.")
        return

    users[username] = {
        "password": password,
        "balance": STARTING_BALANCE,
        "holdings": {},
        "transactions": []
    }

    print("Account created successfully!")


def login():
    global current_user

    print("\n--- Login ---")
    username = input("Username: ")
    password = input("Password: ")

    if username in users and users[username]["password"] == password:
        current_user = username
        print(f"\nWelcome, {username}!")
        return True

    print("Invalid username or password.")
    return False


def logout():
    global current_user
    current_user = None
    print("Logged out successfully.")


def get_stock_price(ticker):
    try:
        stock = yf.Ticker(ticker)
        history = stock.history(period="1d", interval="1m")

        if history.empty:
            price = stock.fast_info["lastPrice"]
        else:
            price = history["Close"].dropna().iloc[-1]

        if price <= 0:
            return None, None

        try:
            name = stock.info.get("shortName", ticker)
        except Exception:
            name = ticker

        return float(price), name

    except Exception:
        return None, None


def search_stock():
    ticker = input("\nEnter stock ticker: ").upper()
    price, name = get_stock_price(ticker)

    if price is None:
        print("Unable to retrieve stock information. Check the ticker.")
        return

    print(f"\nCompany: {name}")
    print(f"Ticker: {ticker}")
    print(f"Current Price: ${price:.2f}")


def view_account():
    user = users[current_user]

    print("\n--- Account Information ---")
    print(f"Username: {current_user}")
    print(f"Available Balance: ${user['balance']:.2f}")

    print("\n--- Stock Holdings ---")

    if not user["holdings"]:
        print("You do not currently own any stocks.")
        return

    for ticker, holding in user["holdings"].items():
        shares = holding["shares"]
        avg_price = holding["average_price"]

        price, name = get_stock_price(ticker)

        print(f"\n{ticker} - {name if name else ticker}")
        print(f"Shares Owned: {shares:.4f}")
        print(f"Average Purchase Price: ${avg_price:.2f}")

        if price is not None:
            market_value = shares * price
            print(f"Current Price: ${price:.2f}")
            print(f"Market Value: ${market_value:.2f}")
        else:
            print("Unable to retrieve current market value.")


def popular_stocks():
    print("\n--- Top 5 Popular Stocks ---")

    available_stocks = []

    for ticker in POPULAR_STOCKS:
        price, name = get_stock_price(ticker)

        if price is not None:
            available_stocks.append(ticker)
            print(f"{len(available_stocks)}. {name} ({ticker}) - ${price:.2f}")

    if not available_stocks:
        print("Unable to retrieve popular stocks.")
        return

    try:
        choice = int(input("\nSelect a stock to purchase (0 to cancel): "))
    except ValueError:
        print("Invalid selection.")
        return

    if choice == 0:
        return

    if choice < 1 or choice > len(available_stocks):
        print("Invalid selection.")
        return

    ticker = available_stocks[choice - 1]

    buy_stock(ticker)

def buy_stock(ticker=None):
    user = users[current_user]

    if ticker is None:
        ticker = input("\nEnter stock ticker to buy: ").upper()

    price, name = get_stock_price(ticker)

    if price is None:
        print("Unable to retrieve stock information. Check the ticker.")
        return

    print(f"\nCompany: {name}")
    print(f"Current Price: ${price:.2f}")

    try:
        shares = float(input("Enter number of shares to buy: "))
    except ValueError:
        print("Please enter a valid number.")
        return

    if shares <= 0:
        print("Number of shares must be greater than zero.")
        return

    total = shares * price

    if total > user["balance"]:
        print("Insufficient funds.")
        return

    new_balance = user["balance"] - total

    print("\n========== PURCHASE PREVIEW ==========")
    print(f"Stock: {name} ({ticker})")
    print(f"Shares: {shares:.4f}")
    print(f"Price per Share: ${price:.2f}")
    print(f"Transaction Cost: ${total:.2f}")
    print("--------------------------------------")
    print(f"Current Balance: ${user['balance']:.2f}")
    print(f"Projected Balance: ${new_balance:.2f}")
    print("======================================")

    confirm = input("\nConfirm purchase? (y/n): ").strip().lower()
    if confirm != "y":
        print("Purchase cancelled.")
        return

    if ticker in user["holdings"]:
        holding = user["holdings"][ticker]
        old_shares = holding["shares"]
        old_average = holding["average_price"]

        new_shares = old_shares + shares
        new_average = (
            (old_shares * old_average) + (shares * price)
        ) / new_shares

        holding["shares"] = new_shares
        holding["average_price"] = new_average

    else:
        user["holdings"][ticker] = {
            "shares": shares,
            "average_price": price
        }

    user["balance"] -= total

    user["transactions"].append({
        "action": "BUY",
        "ticker": ticker,
        "shares": shares,
        "price": price,
        "total": total
    })

    print(f"\nSuccessfully purchased {shares:.4f} shares of {ticker}.")


def sell_stock():
    user = users[current_user]

    ticker = input("\nEnter stock ticker to sell: ").upper()

    if ticker not in user["holdings"]:
        print("You do not own this stock.")
        return

    price, name = get_stock_price(ticker)

    if price is None:
        print("Unable to retrieve stock information. Check the ticker.")
        return

    holding = user["holdings"][ticker]
    owned_shares = holding["shares"]

    print(f"\nCompany: {name}")
    print(f"Current Price: ${price:.2f}")
    print(f"Shares Owned: {owned_shares:.4f}")

    try:
        shares = float(input("Enter number of shares to sell: "))
    except ValueError:
        print("Please enter a valid number.")
        return

    if shares <= 0:
        print("Number of shares must be greater than zero.")
        return

    if shares > owned_shares:
        print("You cannot sell more shares than you own.")
        return

    total = shares * price

    new_balance = user["balance"] + total

    print("\n============ SALE PREVIEW ============")
    print(f"Stock: {name} ({ticker})")
    print(f"Shares to Sell: {shares:.4f}")
    print(f"Price per Share: ${price:.2f}")
    print(f"Transaction Proceeds: ${total:.2f}")
    print("--------------------------------------")
    print(f"Current Balance: ${user['balance']:.2f}")
    print(f"Projected Balance: ${new_balance:.2f}")
    print("======================================")

    confirm = input("\nConfirm sale? (y/n): ").strip().lower()

    if confirm != "y":
        print("Sale cancelled.")
        return

    holding["shares"] -= shares

    if holding["shares"] < 1e-8:
        del user["holdings"][ticker]

    user["balance"] += total

    user["transactions"].append({
        "action": "SELL",
        "ticker": ticker,
        "shares": shares,
        "price": price,
        "total": total
    })

    print(f"\nSuccessfully sold {shares:.4f} shares of {ticker}.")


def transaction_history():
    transactions = users[current_user]["transactions"]

    print("\n--- Transaction History ---")

    if not transactions:
        print("No transactions have been made.")
        return

    for transaction in transactions:
        print(
            f"{transaction['action']} | "
            f"{transaction['ticker']} | "
            f"{transaction['shares']:.4f} shares | "
            f"${transaction['price']:.2f} per share | "
            f"Total: ${transaction['total']:.2f}"
        )


def help_menu():
    print("\n==============================")
    print("          HELP MENU")
    print("==============================")

    print("\n--- Getting Started ---")
    print("Welcome to Stock Trader Simulator!")
    print(f"Every new account starts with ${STARTING_BALANCE:.2f}.")

    print("\n--- How to Use the Simulator ---")

    print("\n1. Search for a Stock")
    print("   Select 'Search Stock' and enter a stock ticker.")
    print("   The simulator will display the company name and current price.")

    print("\n2. Buy Stocks")
    print("   Select 'Buy Stock' and enter the ticker symbol.")
    print("   Enter the number of shares you want to purchase.")
    print("   Review the total cost and confirm your purchase.")

    print("\n3. Buy Popular Stocks")
    print("   Select 'Buy Popular Stocks' to view the top 5 popular stocks.")
    print("   Choose a stock from the list to purchase shares.")

    print("\n4. Sell Stocks")
    print("   Select 'Sell Stock' and enter the ticker symbol.")
    print("   Enter the number of shares you want to sell.")
    print("   Review the total proceeds and confirm your sale.")

    print("\n5. View Your Account")
    print("   Check your available balance and current stock holdings.")
    print("   You can also view the estimated market value of your holdings.")

    print("\n6. Transaction History")
    print("   Review your previous stock purchases and sales.")

    print("\n--- Support ---")
    print("For assistance, please contact:")
    print("figuebry@oregonstate.edu")

    input("\nPress Enter to return to the main menu...")


def main():
    while True:
        print("\n==============================")
        print("     STOCK TRADER SIMULATOR")
        print("==============================")
        print("Keep track of your stocks!")
        print("Create a list of stocks to watch!")
        print("==============================")
        print("1. Login")
        print("2. Create Account")
        print("3. Exit")

        choice = input("\nSelect an option: ")

        if choice == "1":
            if login():
                while current_user:
                    print("\n==============================")
                    print("          MAIN MENU")
                    print("==============================")
                    print("1. Search Stock")
                    print("2. Buy Stock")
                    print("3. Buy Popular Stocks")
                    print("4. Sell Stock")
                    print("5. View Account")
                    print("6. Transaction History")
                    print("7. Help")
                    print("8. Logout")

                    option = input("\nSelect an option: ")

                    if option == "1":
                        search_stock()
                    elif option == "2":
                        buy_stock()
                    elif option == "3":
                        popular_stocks()
                    elif option == "4":
                        sell_stock()
                    elif option == "5":
                        view_account()
                    elif option == "6":
                        transaction_history()
                    elif option == "7":
                        help_menu()
                    elif option == "8":
                        logout()
                    else:
                        print("Invalid option. Please try again.")

        elif choice == "2":
            register()

        elif choice == "3":
            print("Thank you for using Stock Trader Simulator!")
            break

        else:
            print("Invalid option. Please try again.")


if __name__ == "__main__":
    main()
