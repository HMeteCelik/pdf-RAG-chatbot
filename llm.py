from langchain_ollama import ChatOllama
from langchain_ollama import OllamaEmbeddings

llm = ChatOllama(
    model="qwen3:4b-instruct-2507-q4_K_M",
    temperature=1,
    num_ctx=8192,
)
embeddings = OllamaEmbeddings(model="bge-m3:567m")
