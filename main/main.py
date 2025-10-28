from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from vector import retriever

model = OllamaLLM(model="llama3")

template = """
Tu es un assistant qui répond à la question {question} uniquement en te basant sur le contexte suivant 
sans mentionner la question, le nom des documents ou leurs ID: {context}
"""

prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model

while True:
    print("\n-----------------------------------")
    user_input = input("your question : (press q to quit) ")
    print("\n")
    if user_input.lower() == 'q':
        break
    context = retriever.invoke(user_input)
    result = chain.invoke({"context": context, "question": user_input})
    print(result) 