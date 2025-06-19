import json
import os
import requests
import time
from typing import Dict, List, Optional

def process_batch(batch: List[Dict], output_file: str) -> None:
    """Process a batch of records and append to output file."""
    print(f"Processing batch of {len(batch)} records")
    enhanced_batch = []
    client = DeepSeekClient(api_key="sk-3df2c3784e224031badb11204c2fffbf")
    
    if not batch:
        print("Warning: Empty batch received")
        return
    
    # Batch process questions for efficiency
    questions = [record.get('question', '') for record in batch]
    responses = []
    
    # Process in chunks of 50 to avoid rate limits
    for i in range(0, len(questions), 50):
        chunk = questions[i:i+50]
        for question in chunk:
            response = client.generate_response(question)
            responses.append(response or "I'd love to chat more about this!")
        time.sleep(1)  # Brief pause between chunks
    
    # Combine with original records
    for record, answer2 in zip(batch, responses):
        
        enhanced_record = {
            **record,
            'answer2': answer2
        }
        enhanced_batch.append(enhanced_record)
    
    # Append batch to output file
    with open(output_file, 'a', encoding='utf-8') as f:
        for record in enhanced_batch:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')

class DeepSeekClient:
    def __init__(self, api_key: str, base_url: str = "https://api.deepseek.com"):
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        })

    def generate_response(self, question: str, max_retries: int = 3) -> Optional[str]:
        """Generate a sweet response using DeepSeek API."""
        if not question.strip():
            return ""
            
        prompt = (
            f"Assume you are a very sweet young woman. "
            f"Respond to this in a kind, gentle manner, in Chinese only: {question}"
        )
        print(f"Generating response for: {question[:50]}...")
        
        payload = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 100
        }
        
        for attempt in range(max_retries):
            try:
                response = self.session.post(
                    f"{self.base_url}/v1/chat/completions",
                    json=payload,
                    timeout=30
                )
                response.raise_for_status()
                return response.json()["choices"][0]["message"]["content"]
            except Exception as e:
                if attempt == max_retries - 1:
                    print(f"Failed to generate response: {str(e)}")
                    return None
                time.sleep(2 ** attempt)

def generate_sweet_response(question: str) -> str:
    """Generate a sweet response using DeepSeek API."""
    client = DeepSeekClient(api_key="sk-3df2c3784e224031badb11204c2fffbf")
    response = client.generate_response(question)
    return response or "I'd love to chat more about this!"

def process_large_json(input_file: str, output_file: str, batch_size: int = 100) -> None:
    """Process large JSON file in batches."""
    print(f"Starting processing, batch size: {batch_size}")
    
    # Verify output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Clear output file if it exists
    if os.path.exists(output_file):
        print(f"Removing existing output file: {output_file}")
        os.remove(output_file)
    
    batch = []
    processed_records = 0
    
    with open(input_file, 'r', encoding='utf-8') as f:
        # Try to parse as JSON array first
        try:
            data = json.load(f)
            if isinstance(data, list):
                print(f"Processing JSON array with {len(data)} records")
                for i, record in enumerate(data):
                    batch.append(record)
                    processed_records += 1
                    
                    if len(batch) >= batch_size:
                        print(f"Processing records {i-batch_size+1}-{i+1}")
                        process_batch(batch, output_file)
                        batch = []
            else:
                raise ValueError("Input is not a JSON array")
        except json.JSONDecodeError:
            # Fall back to JSONL processing
            print("Input is not JSON array, trying JSONL format")
            f.seek(0)
            for i, line in enumerate(f):
                try:
                    record = json.loads(line)
                    batch.append(record)
                    processed_records += 1
                    
                    if len(batch) >= batch_size:
                        print(f"Processing records {i-batch_size+1}-{i+1}")
                        process_batch(batch, output_file)
                        batch = []
                except json.JSONDecodeError as e:
                    print(f"Error parsing line {i+1}: {str(e)}")
                    continue
    
    # Process remaining records
    if batch:
        print(f"Processing final batch of {len(batch)} records")
        process_batch(batch, output_file)
    
    print(f"Total records processed: {processed_records}")

if __name__ == '__main__':
    input_path = 'data/test_input.json'
    output_path = 'data/test_input_enhanced.jsonl'
    
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} not found")
        exit(1)
        
    print(f"Processing {input_path}...")
    process_large_json(input_path, output_path, batch_size=10)  # Smaller batch for testing
    print(f"Enhanced dataset saved to {output_path}")
    
    # Verify output
    if os.path.exists(output_path):
        print("Sample output:")
        with open(output_path, 'r') as f:
            for i, line in enumerate(f):
                if i >= 3: break
                print(line.strip())
    else:
        print("Error: Output file was not created")
