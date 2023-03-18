import openai
from tiktoken import Tokenizer, TokenizerException

def count_tokens(text: str) -> int:
    tokenizer = Tokenizer()
    try:
        tokens = tokenizer.tokenize(text)
        return len(tokens)
    except TokenizerException as e:
        print(f"Error: {e}")
        return 0