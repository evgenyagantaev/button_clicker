"""
ImageAnalyzer module for analyzing screenshots using OpenAI's vision models.
"""

import os
import base64
import openai
from openai import OpenAI
import re


class ImageAnalyzer:
    """
    Class for analyzing images using OpenAI's vision models.
    
    Attributes:
        api_key: The OpenAI API key.
        api_base: The base URL for the OpenAI API.
        model: The model to use for image analysis.
    """
    
    def __init__(self, api_key, api_base, model):
        """
        Initialize an ImageAnalyzer with the given API credentials and model.
        
        Args:
            api_key: The OpenAI API key.
            api_base: The base URL for the OpenAI API.
            model: The model to use for image analysis.
        """
        self.api_key = api_key
        self.api_base = api_base
        
        # Clean up model name if needed - some providers need special handling
        if "/" in model:
            self.model = model.split("/")[-1]  # Use just the model name part
            print(f"Using cleaned model name: {self.model} (from {model})")
        else:
            self.model = model
            
        # Configure OpenAI client
        try:
            self.client = OpenAI(
                api_key=api_key,
                base_url=api_base
            )
            print(f"OpenAI client initialized with base URL: {api_base}")
        except Exception as e:
            print(f"Error initializing OpenAI client: {e}")
            raise
    
    def encode_image(self, image_path):
        """
        Encode an image to base64 format.
        
        Args:
            image_path: The path to the image file.
            
        Returns:
            str: The base64-encoded image.
        """
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def analyze_image(self, image_path):
        """
        Analyze an image using the OpenAI API.
        
        Args:
            image_path: The path to the image file.
            
        Returns:
            dict: The API response.
            
        Raises:
            Exception: If the API call fails.
        """
        try:
            # Encode the image
            base64_image = self.encode_image(image_path)
            
            # Prepare the messages
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "What you think the person in the image is doing?"},
                        {
                            "type": "image_url",
                            "image_url": f"data:image/jpeg;base64,{base64_image}",
                        },
                    ],
                }
            ]
            
            print(f"Sending request to OpenAI API using model {self.model}")
            
            # Call the API using the new client
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.8,
                n=1,
                max_tokens=300,
            )
            
            # Print the response
            print(f"\nModel analysis response: {response.choices[0].message.content}")
            
            return response
        except Exception as e:
            print(f"Error in analyze_image: {e}")
            import traceback
            print(traceback.format_exc())
            raise
    
    def detect_text_in_image(self, image_path):
        """
        Detect if both 'Accept' and 'Reject' are present in an image.
        
        Args:
            image_path: The path to the image file.
            
        Returns:
            bool: True if both 'Accept' and 'Reject' are detected, False otherwise.
            
        Raises:
            Exception: If the API call fails.
        """
        try:
            # Encode the image
            base64_image = self.encode_image(image_path)
            
            # Prepare the messages with a specific question about the presence of both words
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Are both the words 'Accept' and 'Reject' present in this image? Answer with yes or no."},
                        {
                            "type": "image_url",
                            "image_url": f"data:image/jpeg;base64,{base64_image}",
                        },
                    ],
                }
            ]
            
            print(f"Sending detection request to OpenAI API using model {self.model}")
            
            # Call the API using the new client
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,  # Lower temperature for more deterministic answers
                n=1,
                max_tokens=50,  # Short response is sufficient
            )
            
            # Extract the response text from the new response format
            response_text = response.choices[0].message.content.lower()
            
            # Print the model's response
            print(f"\nModel detection response: {response_text}")
            
            # Check if the response indicates both words are present
            # Look for positive indicators
            if re.search(r'\byes\b', response_text) or re.search(r'both.*present', response_text):
                print("DETECTION RESULT: Both 'Accept' and 'Reject' are present")
                return True
            
            # Look for specific mentions of both words together
            if re.search(r'accept.*reject', response_text) and re.search(r'both', response_text):
                print("DETECTION RESULT: Both 'Accept' and 'Reject' are present")
                return True
            
            print("DETECTION RESULT: Both 'Accept' and 'Reject' are not present")    
            return False
        except Exception as e:
            print(f"Error in detect_text_in_image: {e}")
            import traceback
            print(traceback.format_exc())
            raise 