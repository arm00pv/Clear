import datetime

class YodleeClient:
    """
    A mock client for the Yodlee API.
    """

    def __init__(self, api_key, secret):
        """
        Initializes the Yodlee client.
        In a real implementation, the api_key and secret would be used
        to authenticate with the Yodlee API.
        """
        self.api_key = api_key
        self.secret = secret

    def get_transactions(self, user_id):
        """
        Fetches transactions for a given user from the Yodlee API.
        This mock implementation returns a hardcoded list of transactions.
        """
        # In a real implementation, this would make an API call to Yodlee.
        # For this simulation, we'll return a hardcoded list of transactions
        # that includes some BNPL providers.
        return [
            {
                "date": datetime.date(2025, 7, 1),
                "description": "AMAZON",
                "amount": 50.00,
            },
            {
                "date": datetime.date(2025, 7, 2),
                "description": "STARBUCKS",
                "amount": 5.50,
            },
            {
                "date": datetime.date(2025, 7, 3),
                "description": "KLARNA* WIDGET CO",
                "amount": 25.00,
            },
            {
                "date": datetime.date(2025, 7, 4),
                "description": "UBER",
                "amount": 15.75,
            },
            {
                "date": datetime.date(2025, 7, 5),
                "description": "AFTERPAY* FASHION STORE",
                "amount": 45.00,
            },
            {
                "date": datetime.date(2025, 7, 7),
                "description": "AFFIRM* GADGETS INC",
                "amount": 150.00,
            },
            {
                "date": datetime.date(2025, 7, 10),
                "description": "KLARNA* ANOTHER THING",
                "amount": 30.00,
            },
        ]
