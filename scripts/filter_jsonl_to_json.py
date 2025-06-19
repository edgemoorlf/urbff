import json
import sys
from pathlib import Path

def filter_jsonl(input_path, output_path=None):
    """Filter JSONL file to JSON, removing entries with empty question/answer fields.
    
    Args:
        input_path: Path to input JSONL file
        output_path: Optional output path (defaults to input path with .json extension)
    """
    if output_path is None:
        output_path = Path(input_path).with_suffix('.json')
    
    filtered = []
    with open(input_path, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                data = json.loads(line)
                question = data.get('question', '').strip()
                answer = data.get('answer', '').strip()
                if question and answer:
                    filtered.append(data)
            except json.JSONDecodeError:
                continue
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(filtered, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <input.jsonl> [output.json]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    filter_jsonl(input_file, output_file)
