import os
import sys
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# Load environment variables from the .env file
from dotenv import load_dotenv

# The override=True tells Python to prioritize the .env file over the terminal
load_dotenv(override=True)

def check_keys():
    """Check if required API keys are present as requested by the assignment."""
    missing_keys = []
    if not os.environ.get("OPENAI_API_KEY"):
        missing_keys.append("OPENAI_API_KEY")
    if not os.environ.get("LANGCHAIN_API_KEY"):
        missing_keys.append("LANGCHAIN_API_KEY")
    
    if missing_keys:
        print(f"Error: The following required environment variables are missing: {', '.join(missing_keys)}")
        print("Please check your .env file or export them in your terminal.")
        sys.exit(1)

def main():

    # 1. Verify keys are safe and present
    check_keys()

    # 2. Initialize the OpenAI chat model via LangChain
    llm = ChatOpenAI(model="gpt-3.5-turbo")

    # 3. Define the input
    input_text = "Tell me a historical fact about Tamil Nadu."
    print(f"Input: {input_text}")

    # 4. Invoke the model and print the response
    try:
        response = llm.invoke(input_text)
        print(f"Output: {response.content}")
    except Exception as e:
        print(f"An error occurred during execution: {e}")

if __name__ == "__main__":
    main()