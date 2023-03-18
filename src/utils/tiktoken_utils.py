import tiktoken

encoding = tiktoken.encoding_for_model("gpt-4")
def count_tokens(text: str) -> int:
    tokenizer = Tokenizer()
    try:
        tokens = encoding.encode(text)
        return len(tokens)
    except TokenizerException as e:
        print(f"Error: {e}")
        return 0
