"""
Plaid API Client Wrapper
Handles bank connection, transaction fetching, and subscription detection
"""

import os
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from decimal import Decimal
import plaid
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.transactions_get_request_options import TransactionsGetRequestOptions


class PlaidClient:
    """
    Wrapper for Plaid API interactions.
    
    Handles:
    - Link token creation for Plaid Link UI
    - Public token exchange for access tokens
    - Transaction fetching and syncing
    - Subscription detection from recurring charges
    """
    
    def __init__(self):
        """Initialize Plaid client with environment configuration"""
        configuration = plaid.Configuration(
            host=self._get_plaid_host(),
            api_key={
                'clientId': os.getenv('PLAID_CLIENT_ID'),
                'secret': os.getenv('PLAID_SECRET'),
            }
        )
        
        api_client = plaid.ApiClient(configuration)
        self.client = plaid_api.PlaidApi(api_client)
    
    def _get_plaid_host(self) -> str:
        """Get Plaid API host based on environment"""
        env = os.getenv('PLAID_ENV', 'sandbox')
        
        hosts = {
            'sandbox': plaid.Environment.Sandbox,
            'development': plaid.Environment.Development,
            'production': plaid.Environment.Production
        }
        
        return hosts.get(env, plaid.Environment.Sandbox)
    
    async def create_link_token(self, user_id: str, user_name: str) -> str:
        """
        Generate a Plaid Link token for initializing Plaid Link UI.
        
        The mobile app uses this token to open Plaid Link and let users
        connect their bank account.
        
        Args:
            user_id: Sub-Zero user ID
            user_name: User's name for Plaid UI
            
        Returns:
            str: Link token for Plaid Link initialization
        """
        try:
            request = LinkTokenCreateRequest(
                user=LinkTokenCreateRequestUser(
                    client_user_id=user_id
                ),
                client_name="Sub-Zero",
                products=[Products("transactions")],
                country_codes=[CountryCode("US")],
                language='en',
                redirect_uri=os.getenv('PLAID_REDIRECT_URI', 'subzero://plaid-redirect')
            )
            
            response = self.client.link_token_create(request)
            return response['link_token']
            
        except plaid.ApiException as e:
            raise Exception(f"Error creating link token: {e}")
    
    async def exchange_public_token(self, public_token: str) -> Dict[str, str]:
        """
        Exchange Plaid Link public token for access token.
        
        After user completes Plaid Link flow, exchange the one-time public token
        for a permanent access token to fetch transactions.
        
        Args:
            public_token: One-time token from Plaid Link success callback
            
        Returns:
            dict: Contains 'access_token' and 'item_id'
        """
        try:
            request = ItemPublicTokenExchangeRequest(
                public_token=public_token
            )
            
            response = self.client.item_public_token_exchange(request)
            
            return {
                'access_token': response['access_token'],
                'item_id': response['item_id']
            }
            
        except plaid.ApiException as e:
            raise Exception(f"Error exchanging public token: {e}")
    
    async def get_transactions(
        self,
        access_token: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict]:
        """
        Fetch transactions from Plaid for subscription detection.
        
        Retrieves transaction history from the connected bank account.
        Default: Last 90 days of transactions.
        
        Args:
            access_token: Plaid access token from bank_connections table
            start_date: Start of transaction range (default: 90 days ago)
            end_date: End of transaction range (default: today)
            
        Returns:
            List of transaction dictionaries
        """
        if not start_date:
            start_date = datetime.now() - timedelta(days=90)
        if not end_date:
            end_date = datetime.now()
        
        try:
            request = TransactionsGetRequest(
                access_token=access_token,
                start_date=start_date.date(),
                end_date=end_date.date(),
                options=TransactionsGetRequestOptions()
            )
            
            response = self.client.transactions_get(request)
            transactions = response['transactions']
            
            # Handle pagination if needed
            while len(transactions) < response['total_transactions']:
                request.options.offset = len(transactions)
                response = self.client.transactions_get(request)
                transactions.extend(response['transactions'])
            
            return [self._format_transaction(t) for t in transactions]
            
        except plaid.ApiException as e:
            raise Exception(f"Error fetching transactions: {e}")
    
    def _format_transaction(self, transaction) -> Dict:
        """Format Plaid transaction for internal use"""
        return {
            'id': transaction['transaction_id'],
            'date': transaction['date'],
            'name': transaction['name'],
            'merchant_name': transaction.get('merchant_name', transaction['name']),
            'amount': float(transaction['amount']),
            'category': transaction.get('category', []),
            'pending': transaction['pending']
        }
    
    async def detect_subscriptions(self, transactions: List[Dict]) -> List[Dict]:
        """
        Analyze transactions to detect recurring subscription charges.
        
        Detection algorithm:
        1. Group transactions by merchant name
        2. Look for recurring charges (same amount, ~30 day intervals)
        3. Filter out one-time purchases
        4. Return detected subscriptions with metadata
        
        Args:
            transactions: List of formatted transactions
            
        Returns:
            List of detected subscription dictionaries
        """
        # Group by merchant
        merchant_charges = {}
        for txn in transactions:
            merchant = txn['merchant_name']
            if merchant not in merchant_charges:
                merchant_charges[merchant] = []
            merchant_charges[merchant].append(txn)
        
        detected_subscriptions = []
        
        for merchant, charges in merchant_charges.items():
            # Skip if less than 2 charges (need pattern)
            if len(charges) < 2:
                continue
            
            # Sort by date
            charges.sort(key=lambda x: x['date'])
            
            # Check for recurring pattern
            amounts = [c['amount'] for c in charges]
            
            # Simple heuristic: same amount, multiple occurrences
            if len(set(amounts)) == 1 and len(charges) >= 2:
                # Calculate average interval between charges
                from datetime import datetime
                dates = [datetime.strptime(c['date'], '%Y-%m-%d') if isinstance(c['date'], str) else c['date'] for c in charges]
                intervals = [(dates[i+1] - dates[i]).days for i in range(len(dates)-1)]
                avg_interval = sum(intervals) / len(intervals) if intervals else 0
                
                # If charges are roughly monthly (25-35 days)
                if 25 <= avg_interval <= 35:
                    detected_subscriptions.append({
                        'merchant_name': merchant,
                        'normalized_name': self._normalize_merchant_name(merchant),
                        'monthly_price': Decimal(str(amounts[0])),
                        'last_charge_date': charges[-1]['date'],
                        'status': 'active',
                        'logo_url': None,  # TODO: Add logo lookup service
                        'cancellation_url': None  # TODO: Add URL lookup
                    })
        
        return detected_subscriptions
    
    def _normalize_merchant_name(self, merchant_name: str) -> str:
        """
        Normalize merchant name for better matching.
        
        Examples:
        - "SPOTIFY USA" -> "Spotify"
        - "NETFLIX.COM" -> "Netflix"
        - "Adobe* Creative Cloud" -> "Adobe Creative Cloud"
        """
        # Simple normalization - can be enhanced with merchant database
        name = merchant_name.strip()
        name = name.replace('*', '').replace('.COM', '').replace('.com', '')
        name = ' '.join(name.split())  # Normalize whitespace
        return name.title()
