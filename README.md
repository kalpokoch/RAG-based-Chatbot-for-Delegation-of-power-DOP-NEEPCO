# Project Summary: RAG-based Chatbot for Delegation of Power (DOP) - NEEPCO

## Purpose

This project aims to build a robust, retrieval-augmented generation (RAG) chatbot to assist users in navigating and understanding the Delegation of Power (DOP) policies of NEEPCO (North Eastern Electric Power Corporation Limited). The chatbot is designed to provide accurate, reference-backed answers to questions about authority, policy clauses, and operational procedures, streamlining access to organizational rules and reducing manual effort in document lookup.

---

## Dataset Overview

### Structure

- **Format:** JSON Lines (`.jsonl`)
- **File:** `Dataset/combined_dataset.jsonl`
- **Fields:**
  - `instruction`: The user question or prompt (e.g., "Who approves resignation for executives E-7 and above?")
  - `input`: Additional input/context for the instruction (often blank)
  - `output`: The answer to the instruction, typically a concise fact, explanation, or policy reference

#### Example Entry
```json
{"instruction": "Who approves resignation of executives E-7 and above?", "input": "", "output": "CMD"}
```

### Content

- Contains hundreds of real-world, policy-related questions and their precise answers, focused on DOP at NEEPCO.
- Covers a wide range of topics, such as:
  - Authority and approval powers (e.g., approvals for leave, resignation, hiring)
  - Limits and conditions (e.g., financial ceilings, grade restrictions)
  - Operational rules (e.g., process for study leave, panel formation)
  - Policy navigation (e.g., which section or clause covers a topic)
- Multiple phrasings and paraphrases improve chatbot robustness to natural user language.

---

## Context Overview

### Structure

- **Format:** JSON Lines (`.jsonl`)
- **File:** `Context/combined_context.jsonl`
- **Fields:**
  - `section`: Roman numeral or letter indicating major policy section (e.g., "I", "II")
  - `title`: Title of the section or policy area (e.g., "Interview List Preparation")
  - `clause`: Clause number within the section
  - `subclauses`: (optional) List of subclauses with `id` and `description`
  - `extent_of_power`: (optional) Specifies the limits or full powers delegated
  - `authority`: (optional) Role or designation assigned the authority
  - `remarks`: (optional) Additional notes or conditions

#### Example Entry
```json
{
  "section": "II",
  "title": "Acceptance of Resignation of employees including waiver of notice period",
  "clause": 9,
  "extent_of_power": [{"Executives up to E-8": "Full Powers"}, {"Non-Executives": "Full Powers"}],
  "authority": "CMD, Director, HOP/HOD (depending on grade)"
}
```

### Content

- Encodes the official DOP policy in a structured, machine-readable format.
- Each entry reflects a specific policy clause, approval authority, scope/limits, and any special instructions.
- Granularity allows for precise retrieval and matching to user queries.

---

## Alignment & Integration

- **Alignment:** The dataset questions are mapped directly to the policy clauses in the context file. This enables accurate retrieval of source policy for chatbot answers.
- **Integration in RAG:** When a user asks a question, the chatbot retrieves the most relevant context entry, then either surfaces the policy clause directly or generates a natural language answer based on that clause, providing source-backed responses.

---

## Project Purpose and Impact

### Why This Matters

- **Policy Clarity:** NEEPCO’s DOP document is comprehensive and complex. Employees and stakeholders often need quick, reliable answers about authority, limits, and processes.
- **Efficiency:** The chatbot reduces time spent searching through policy manuals or waiting for manual clarifications.
- **Governance:** Ensures consistent, policy-compliant answers, reducing the risk of procedural or authority errors.
- **Scalability:** The approach can be extended to cover other corporate policies or adapted to similar organizations.

### Key Features

- **Retrieval-Augmented Generation:** Combines semantic and lexical search with generative AI for both accuracy and flexibility.
- **Explainability:** Answers are reference-backed and traceable to specific clauses.
- **User-Friendliness:** Handles varied natural language queries with high precision.
- **Extensible Design:** Adding new clauses or updating policy is as simple as modifying the context file.

---

## Example Workflow

1. **User asks:** "Who can approve study leave for E-7 grade executives?"
2. **Chatbot retrieves:** Context entry for "Sanction of study leave" (Section/Clause specifying CMD as the authority for E-7+)
3. **Chatbot responds:** "CMD approves study leave for E-7 and above," optionally citing the clause/section.

---

## Conclusion

This project provides an intelligent, structured, and reference-backed solution for navigating DOP policies at NEEPCO. By leveraging a well-aligned dataset and policy context, the chatbot dramatically enhances organizational efficiency, governance, and access to information.
