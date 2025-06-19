# RAG-based-Chatbot-for-Delegation-of-power-DOP-NEECO
🧱 Dataset Structure & Convention
This dataset follows an instruction-tuning format commonly used in training LLMs like Mistral-7B, LLaMA, or Falcon. The goal is to train or use a chatbot to understand and respond to queries about Delegation of Powers (DOP), including designation-wise limits and clause-specific meanings.

Each file contains a list of Q&A pairs, defined as:

yaml
Copy
Edit
- instruction: <User's natural language question>
  input: <Context, if needed (usually blank)>
  output: <Factual structured answer from the document>
Each clause or section (e.g., procurement powers, financial guidelines) is stored in a dedicated YAML file:

mathematica
Copy
Edit
Dataset/
├── section1_index.yaml
├── section2_financial.yaml
├── section5_procurement.yaml
├── ...
🔁 Role-Based Variations (Post-wise)
For each sub-clause (like 1(a), 1(b), etc.), it is essential to create variations per post/designation, such as:

D(T)

ED

CGM

GM

DGM

Sr. M

✅ Example for Clause 1(a)
yaml
Copy
Edit
- instruction: What is the delegation limit for CGM for approved projects under Clause 1(a)?
  input: ""
  output: ₹15 crore

- instruction: What is the delegation limit for GM under Clause 1(a)?
  input: ""
  output: ₹10 crore

- instruction: Can DGM approve technical sanction for approved projects?
  input: ""
  output: Yes, up to ₹5 crore.

- instruction: Can a Senior Manager approve projects under Clause 1(a)?
  input: ""
  output: No, the limit is NIL.

- instruction: Who has full power for Clause 1(a) technical sanctions?
  input: ""
  output: D(T) and ED have full powers.

- instruction: What does Clause 1(a) of procurement powers state?
  input: ""
  output: Technical sanction to detailed estimates for works/ services/ supplies for approved project
