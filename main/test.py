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

def process_questions(input_file="questions.txt", output_file="answers.txt"):

    try:
        # Read all questions
        with open(input_file, 'r', encoding='utf-8') as f:
            questions = [line.strip() for line in f if line.strip()]
        
        if not questions:
            print(f"No questions found in {input_file}")
            return
        
        print(f"Found {len(questions)} questions to process...\n")
        
        # Open output file for writing
        with open(output_file, 'w', encoding='utf-8') as f:
            for i, question in enumerate(questions, 1):
                print(f"Processing question {i}/{len(questions)}: {question[:50]}...")
                
                try:
                    # Get context and generate answer
                    context = retriever.invoke(question)
                    answer = chain.invoke({"context": context, "question": question})
                    
                    # Write to file
                    f.write(f"{question}\n")
                    f.write(f"{answer}\n")
                    f.write("\n")  # Empty line between Q&A pairs
                    
                    # Flush to ensure it's written (useful for monitoring progress)
                    f.flush()
                    
                    print(f"✓ Completed\n")
                    
                except Exception as e:
                    print(f"✗ Error processing question: {e}\n")
                    # Write error to file
                    f.write(f"{question}\n")
                    f.write(f"ERROR: {str(e)}\n")
                    f.write("\n")
                    f.flush()
        
        print(f"\n{'='*50}")
        print(f"✓ All questions processed!")
        print(f"✓ Answers saved to: {output_file}")
        print(f"{'='*50}")
        
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Run the batch processing
    process_questions()