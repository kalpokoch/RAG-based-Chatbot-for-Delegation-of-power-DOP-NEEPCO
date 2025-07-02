# Complete Setup and Running Instructions for NEEPCO DOP RAG Chatbot

"""
STEP-BY-STEP SETUP GUIDE
========================

1. Install Requirements:
   pip install sentence-transformers chromadb transformers torch datasets

2. Prepare your files:
   - Make sure you have: Context/combined_context.jsonl
   - Make sure you have: Dataset/combined_dataset.jsonl

3. Run scripts in order:

"""

# STEP 1: Create context chunks
def step1_create_chunks():
    print("Step 1: Creating context chunks...")
    from prepare_context_chunks import create_context_chunks
    
    chunks = create_context_chunks("Context/combined_context.jsonl")
    
    # Save chunks
    import json
    with open("processed_chunks.json", "w", encoding='utf-8') as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Created {len(chunks)} context chunks")
    return chunks

# STEP 2: Setup vector database
def step2_setup_database():
    print("Step 2: Setting up vector database...")
    from create_vector_database import setup_vector_database
    
    db = setup_vector_database()
    print("✓ Vector database ready")
    return db

# STEP 3: Test the system
def step3_test_system():
    print("Step 3: Testing the complete system...")
    from rag_chatbot import NEEPCOPolicyChatbot
    
    # Initialize chatbot
    chatbot = NEEPCOPolicyChatbot()
    
    # Test questions
    test_questions = [
        "Who approves resignation for executives E-7 and above?",
        "What is the authority for study leave approval?",
        "Who can form interview panels?"
    ]
    
    for question in test_questions:
        print(f"\nTesting: {question}")
        response = chatbot.chat(question)
        print(f"Answer: {response['answer']}")
        print(f"Sources: {len(response['sources'])} policy sections found")

# COMPLETE SETUP FUNCTION
def complete_setup():
    """Run complete setup process"""
    try:
        print("🚀 Starting NEEPCO DOP RAG Chatbot Setup...")
        print("=" * 50)
        
        # Step 1: Create chunks
        chunks = step1_create_chunks()
        
        # Step 2: Setup database  
        db = step2_setup_database()
        
        # Step 3: Test system
        step3_test_system()
        
        print("\n🎉 Setup Complete!")
        print("You can now run: python rag_chatbot.py")
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        print("Please check your file paths and try again.")

# QUICK START FUNCTION
def quick_start():
    """Quick start for users who have already setup"""
    print("🚀 Starting NEEPCO DOP Chatbot...")
    from rag_chatbot import main
    main()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "setup":
        complete_setup()
    else:
        # Ask user what they want to do
        print("NEEPCO DOP RAG Chatbot")
        print("=" * 30)
        print("1. Complete Setup (first time)")
        print("2. Start Chatbot (if already setup)")
        
        choice = input("Choose option (1 or 2): ").strip()
        
        if choice == "1":
            complete_setup()
        elif choice == "2":
            quick_start()
        else:
            print("Invalid choice. Please run again.")

# USAGE EXAMPLES:
"""
# First time setup:
python setup_and_run.py setup

# Or interactive:
python setup_and_run.py

# Direct chatbot start:
python rag_chatbot.py
"""