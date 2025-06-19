# RAG-based-Chatbot-for-Delegation-of-power-DOP-NEECO
# 🧠 Delegation of Powers (DOP) Chatbot Dataset

This dataset is designed to train or support a Retrieval-Augmented Generation (RAG) or fine-tuning based chatbot that can answer questions related to the **Delegation of Powers (DOP)** document of NEEPCO. It covers every clause, designation-based powers, remarks, and conditions described in the official documentation.

---

## 📦 Dataset Structure

The dataset is organized into separate `.yaml` files for each major section or clause of the DOP. Each YAML file contains **instruction-based Q&A pairs** using the following structure:

## For each Designated Post you will have to create varitaion of questions for the same answer. Atleast 5 variations of questions
(Imagine it in a way that you are giving the prompt to the chatbot according to which the chatbot will provide you the answer)
ex. What is DOP?
    What is Delegation of Power?
    DOP full form?

ex. Director Technical can sanction how much amount for approved projects?
    Discuss the power of Director Technical for approved projects?
    DT power for approved projects
    etc.

NOTE : For each sub-clause you will have to prepare the same way.

```yaml
- instruction: <Natural language question>
  input: <Optional context if required; usually empty>
  output: |
    <Structured, factual answer copied or summarized from the document>
