import re
import json
import os
import sys
import glob

# Regex to match chat lines with speaker and content
CHAT_LINE_RE = re.compile(r'^\[([^\]]*)\]\[(.*?)\](.*)$|^\[([^\]]*)\](.*)$|^(\[.*?\])?(.*)$')

# Regex to match timestamps
TIME_STAMP_RE = re.compile(r'\[\d{1,2}:\d{2}\]')

# Regex to match timestamps at the beginning of a sentence (e.g., 20:06)
BEGIN_TIME_RE = re.compile(r'^\d{1,2}:\d{2}\s*')

# Helper to clean up speaker and message
def parse_line(line):
    # Try to extract speaker and message
    match = CHAT_LINE_RE.match(line.strip())
    if not match:
        return None, line.strip()
    # Try to get speaker and message
    if match.group(1) is not None:
        speaker = match.group(1).strip()
        message = match.group(3).strip()
    elif match.group(4) is not None:
        speaker = match.group(4).strip()
        message = match.group(5).strip()
    else:
        speaker = None
        message = match.group(7).strip()
    # Remove all timestamps like [14:51]
    message = TIME_STAMP_RE.sub('', message).strip()
    # Remove timestamps like 14:51 at the beginning of a sentence
    message = BEGIN_TIME_RE.sub('', message).strip()
    return speaker, message

def extract_qa_pairs(turns):
    qa_pairs = []
    for i, (speaker, message) in enumerate(turns[:-1]):
        # If message ends with a question mark, treat as question
        if message.endswith('？') or message.endswith('?'):
            # Find the next non-empty message as answer
            for j in range(i+1, len(turns)):
                next_speaker, next_message = turns[j]
                if next_message:
                    qa_pairs.append({
                        'question': message,
                        'answer': next_message
                    })
                    break
    return qa_pairs

def process_file(file_path):
    turns = []
    with open(file_path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('202'):  # skip date lines
                continue
            speaker, message = parse_line(line)
            if message:
                turns.append((speaker, message))
    return extract_qa_pairs(turns)

def main():
    if len(sys.argv) != 3:
        print(f"Usage: python {sys.argv[0]} <input_dir> <output_jsonl>")
        sys.exit(1)
    input_dir = sys.argv[1]
    output_file = sys.argv[2]
    all_qa_pairs = []
    txt_files = glob.glob(os.path.join(input_dir, '*.txt'))
    for txt_file in txt_files:
        qa_pairs = process_file(txt_file)
        all_qa_pairs.extend(qa_pairs)
    # Filter out QA pairs where the answer contains a question mark
    filtered_qa_pairs = [qa for qa in all_qa_pairs if '?' not in qa['answer'] and '？' not in qa['answer']]
    with open(output_file, 'w', encoding='utf-8') as out:
        for qa in filtered_qa_pairs:
            out.write(json.dumps(qa, ensure_ascii=False) + '\n')
    print(f"Extracted {len(filtered_qa_pairs)} QA pairs from {len(txt_files)} files to {output_file}")

if __name__ == '__main__':
    main() 