import tiktoken

encoding = tiktoken.encoding_for_model("gpt-4o") 

tokens = encoding.encode("Hey whats up")
print(tokens) # [25216, 55993, 869]

reconstruct = encoding.decode(tokens)
print(reconstruct) # Hey whats up