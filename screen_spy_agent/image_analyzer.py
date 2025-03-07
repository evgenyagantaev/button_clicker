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
    
    def detect_text_in_image(self, image_path, text_to_detect="Accept Reject"):
        """
        Detect if a specific text phrase is present in an image.
        
        Args:
            image_path: The path to the image file.
            text_to_detect: The text phrase to look for in the image (default: "Accept Reject").
            
        Returns:
            bool: True if the text phrase is detected, False otherwise.
            
        Raises:
            Exception: If the API call fails.
        """
        try:
            # Encode the image
            base64_image = self.encode_image(image_path)
            
            # Prepare the messages with a specific question about the presence of the text
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f'Is the phrase "{text_to_detect}" present in this image? Answer with yes or no.'},
                        {
                            "type": "image_url",
                            "image_url": f"data:image/jpeg;base64,{base64_image}",
                        },
                    ],
                }
            ]
            
            print(f"Sending detection request to OpenAI API using model {self.model}")
            print(f"Looking for text: \"{text_to_detect}\" in the image")
            
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
            
            # Check if the response indicates the text is present
            if re.search(r'\byes\b', response_text) or re.search(f'{text_to_detect.lower()}.*present', response_text, re.IGNORECASE):
                print(f"DETECTION RESULT: \"{text_to_detect}\" is present")
                return True
            
            print(f"DETECTION RESULT: \"{text_to_detect}\" is not present")    
            return False
        except Exception as e:
            print(f"Error in detect_text_in_image: {e}")
            import traceback
            print(traceback.format_exc())
            raise 