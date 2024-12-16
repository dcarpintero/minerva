---
title: minerva
emoji: 🔬
colorFrom: blue
colorTo: indigo
sdk: gradio
sdk_version: 5.9.0
app_file: app.py
pinned: false
---

## Minerva: A Multi-Agent LLM System for Digital Scam Protection

Digital scams inflict devastating impacts in our society. Over the past five years, $37.4 billion was lost in the United States alone due to online fraud [1]. Beyond these direct losses, the hidden costs of processing nearly 4 million fraud claims [1] has overwhelmed institutional and enterprise resources, while victims face psychological disruptions and eroding trust in novel technologies.

To address this challenge, we explore the use of a multi-agent system leveraging Large Language Models (LLMs) to protect users from digital scams. MINERVA implements a cooperative team of specialized agents using the AutoGen framework (v0.4.0) [2], where each agent focuses on a specific aspect of scam detection - from optical character recognition and URL verification to content analysis and multilingual processing. These agents work in concert to provide clear, actionable guidance to users.

### Agents with Tools

We define the following agents whose roles are specified in [./config/agents.yaml](./config/agents.yaml):

- OCR Agent: *Extracts text from an image using pytesseract or the LLM-Vision capabilities.*
- Link Checker: *Verifies the legitimacy of URLs using Google SafeBrowsing API.*
- Content Analyst: *Analyzes the extracted text for scam patterns.*
- Decision Maker: *Synthesizes the analyses and makes final determination.*
- Summarizer: *Generates a summary of the final determination.*
- Language Translation Specialist: *Translates the summary to the user language.*

### Orchestration

We orchestrate the agents to cooperate in RoundRobin fashion. The termination is triggered after all agents have completed their tasks, or if no text can be extracted from the image provided.

### App

The results and workflow can be tested at https://huggingface.co/spaces/dcarpintero/minerva

### References

- [1] [FBI's Internet Crime Complaint Center (IC3), 2023 Internet Crime Report](https://www.ic3.gov/AnnualReport/Reports/2023_IC3Report.pdf)
- [2] [AutoGen](https://github.com/microsoft/autogen/)
