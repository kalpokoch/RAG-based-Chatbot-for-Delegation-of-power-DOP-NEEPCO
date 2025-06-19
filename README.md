# RAG-based-Chatbot-for-Delegation-of-power-DOP-NEECO
# 🧠 Delegation of Powers (DOP) Chatbot Dataset

This dataset is designed to train or support a Retrieval-Augmented Generation (RAG) or fine-tuning based chatbot that can answer questions related to the **Delegation of Powers (DOP)** document of NEEPCO. It covers every clause, designation-based powers, remarks, and conditions described in the official documentation.

---

## 📦 Dataset Structure

The dataset is organized into separate `.yaml` files for each major section or clause of the DOP. Each YAML file contains **instruction-based Q&A pairs** using the following structure:

```yaml
- instruction: <Natural language question>
  input: <Optional context if required; usually empty>
  output: |
    <Structured, factual answer copied or summarized from the document>

