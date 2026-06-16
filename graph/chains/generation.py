from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from llm import llm

prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question.\n"
     "If you don't know the answer, just say that you don't know.\n"
     "Use maximum 5 sentences maximum and keep the answer concise.\n"
     "Detect the language of the user's question and respond strictly in that same language — entirely in Turkish or entirely in English, never mixed.\n"
     "If the question contains both languages, use the dominant one.\n"
     "Keep technical and domain-specific terms in their original English form even when responding in Turkish.\n"
     "\nContext: {context}"
     ),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{question}"),
])

generator = prompt | llm | StrOutputParser()