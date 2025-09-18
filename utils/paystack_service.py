"""
Paystack Payment Service
Handles all Paystack payment operations
"""

import requests
from flask import current_app
import logging

logger = logging.getLogger(__name__)

class PaystackService:
    def __init__(self):
        self.secret_key = current_app.config['PAYSTACK_SECRET_KEY']
        self.public_key = current_app.config['PAYSTACK_PUBLIC_KEY']
        self.base_url = 'https://api.paystack.co'
        self.headers = {
            'Authorization': f'Bearer {self.secret_key}',
            'Content-Type': 'application/json'
        }
    
    def initialize_transaction(self, email, amount, reference, callback_url=None, metadata=None):
        """
        Initialize a Paystack transaction
        
        Args:
            email (str): Customer email
            amount (int): Amount in kobo (Nigerian currency)
            reference (str): Unique transaction reference
            callback_url (str): Callback URL after payment
            metadata (dict): Additional metadata
            
        Returns:
            dict: Paystack response
        """
        try:
            # Convert amount from Naira to kobo
            amount_kobo = int(amount * 100)
            
            transaction_data = {
                'email': email,
                'amount': amount_kobo,
                'reference': reference,
                'currency': 'NGN',
                'callback_url': callback_url or f"{current_app.config.get('BASE_URL', 'http://localhost:5000')}/payment/callback",
                'metadata': metadata or {}
            }
            
            url = f"{self.base_url}/transaction/initialize"
            response = requests.post(url, headers=self.headers, json=transaction_data)
            
            if response.status_code == 200:
                data = response.json()
                if data['status']:
                    logger.info(f"Transaction initialized successfully: {reference}")
                    return {
                        'success': True,
                        'data': data['data'],
                        'message': data['message']
                    }
                else:
                    logger.error(f"Failed to initialize transaction: {data.get('message', 'Unknown error')}")
                    return {
                        'success': False,
                        'message': data.get('message', 'Failed to initialize transaction')
                    }
            else:
                logger.error(f"HTTP error {response.status_code}: {response.text}")
                return {
                    'success': False,
                    'message': f'HTTP error {response.status_code}: {response.text}'
                }
                
        except Exception as e:
            logger.error(f"Error initializing transaction: {str(e)}")
            return {
                'success': False,
                'message': f'Error initializing transaction: {str(e)}'
            }
    
    def verify_transaction(self, reference):
        """
        Verify a Paystack transaction
        
        Args:
            reference (str): Transaction reference
            
        Returns:
            dict: Verification response
        """
        try:
            url = f"{self.base_url}/transaction/verify/{reference}"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                if data['status'] and data['data']['status'] == 'success':
                    logger.info(f"Transaction verified successfully: {reference}")
                    return {
                        'success': True,
                        'data': data['data'],
                        'message': 'Transaction verified successfully'
                    }
                else:
                    logger.warning(f"Transaction verification failed: {reference}")
                    return {
                        'success': False,
                        'message': 'Transaction verification failed'
                    }
            else:
                logger.error(f"HTTP error {response.status_code}: {response.text}")
                return {
                    'success': False,
                    'message': f'HTTP error {response.status_code}: {response.text}'
                }
                
        except Exception as e:
            logger.error(f"Error verifying transaction: {str(e)}")
            return {
                'success': False,
                'message': f'Error verifying transaction: {str(e)}'
            }
    
    def create_customer(self, email, first_name=None, last_name=None, phone=None):
        """
        Create a Paystack customer
        
        Args:
            email (str): Customer email
            first_name (str): Customer first name
            last_name (str): Customer last name
            phone (str): Customer phone number
            
        Returns:
            dict: Customer creation response
        """
        try:
            customer_data = {
                'email': email,
                'first_name': first_name or '',
                'last_name': last_name or '',
                'phone': phone or ''
            }
            
            url = f"{self.base_url}/customer"
            response = requests.post(url, headers=self.headers, json=customer_data)
            
            if response.status_code == 200:
                data = response.json()
                if data['status']:
                    logger.info(f"Customer created successfully: {email}")
                    return {
                        'success': True,
                        'data': data['data'],
                        'message': 'Customer created successfully'
                    }
                else:
                    logger.error(f"Failed to create customer: {data.get('message', 'Unknown error')}")
                    return {
                        'success': False,
                        'message': data.get('message', 'Failed to create customer')
                    }
            else:
                logger.error(f"HTTP error {response.status_code}: {response.text}")
                return {
                    'success': False,
                    'message': f'HTTP error {response.status_code}: {response.text}'
                }
                
        except Exception as e:
            logger.error(f"Error creating customer: {str(e)}")
            return {
                'success': False,
                'message': f'Error creating customer: {str(e)}'
            }
    
    def get_transaction_status(self, reference):
        """
        Get transaction status
        
        Args:
            reference (str): Transaction reference
            
        Returns:
            dict: Transaction status
        """
        try:
            url = f"{self.base_url}/transaction/verify/{reference}"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                if data['status']:
                    return {
                        'success': True,
                        'data': data['data'],
                        'status': data['data']['status']
                    }
                else:
                    return {
                        'success': False,
                        'message': 'Failed to get transaction status'
                    }
            else:
                logger.error(f"HTTP error {response.status_code}: {response.text}")
                return {
                    'success': False,
                    'message': f'HTTP error {response.status_code}: {response.text}'
                }
                
        except Exception as e:
            logger.error(f"Error getting transaction status: {str(e)}")
            return {
                'success': False,
                'message': f'Error getting transaction status: {str(e)}'
            }
