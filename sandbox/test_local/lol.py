def transfer_money(accounts, sender, receiver, amount):
    if not isinstance(accounts, dict):
        raise ValueError("Accounts must be a dictionary, expected dict but got {}".format(type(accounts)))

    if not accounts:
        raise ValueError("Accounts dictionary is empty")

    if not isinstance(amount, (int, float)):
        raise ValueError("Invalid transfer amount, expected int or float but got {}".format(type(amount)))

    if amount <= 0:
        raise ValueError("Invalid transfer amount, amount must be greater than zero")

    if not isinstance(sender, str) or not isinstance(receiver, str):
        raise ValueError("Account names must be strings, sender: {}, receiver: {}".format(type(sender), type(receiver)))

    if sender not in accounts or receiver not in accounts:
        raise ValueError("Account not found, sender: {}, receiver: {}".format(sender, receiver))

    if not isinstance(accounts[sender], (int, float)) or not isinstance(accounts[receiver], (int, float)):
        raise ValueError("Account balance must be numeric, sender balance: {}, receiver balance: {}".format(type(accounts[sender]), type(accounts[receiver])))

    if accounts[sender] < amount:
        raise ValueError("Not enough balance, sender balance: {}, amount: {}".format(accounts[sender], amount))

    updated_accounts = accounts.copy()
    updated_accounts[sender] = accounts[sender] - amount
    updated_accounts[receiver] = accounts[receiver] + amount

    return updated_accounts


accounts = {
    "Alice": 1000,
    "Bob": 500
}

try:
    updated_accounts = transfer_money(accounts, "Alice", "Bob", 1500)
    print(updated_accounts)
except ValueError as e:
    print(e)