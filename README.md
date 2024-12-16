<!-- 
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
-->

## Minerva: A Multi-Agent LLM System for Digital Scam Protection

Digital scams inflict devastating impacts in our society. Over the past five years, $37.4 billion was lost in the United States alone due to online fraud [1]. Beyond these direct losses, the hidden costs of processing nearly 4 million fraud claims [1] has overwhelmed institutional and enterprise resources, while victims face psychological disruptions and eroding trust in novel technologies.

To address this challenge, we explore the use of a multi-agent system leveraging Large Language Models (LLMs) to protect users from digital scams. MINERVA implements a cooperative team of specialized agents using the AutoGen framework (v0.4.0) [2], where each agent leverages tool calling and LLM capabilities to focus on a specific aspect of scam detection - from optical character recognition and URL verification to content analysis and multilingual processing. The workflow is trigerred by a user sending a MultiModal message (screenshot of a digital communication) to the AI team, and terminates after all agents have completed their tasks or a termination message is trigerred. After this analysis the user receives clear, actionable guidance in their own language.

Beyond immediate protection, this project improves digital literacy by providing users with explanations about detected scams, while building trust in AI-powered safety tools. Moreover, by creating an open, anonymized, up-to-date scam database with the reported scams, it will facilitate fine-tuning using up-to-date scam patterns.

### Agents with Tools

We define the following agents whose roles are specified in [./config/agents.yaml](./config/agents.yaml):

- OCR Agent: *Extracts text from an image using pytesseract or the LLM-Vision capabilities.*
- Link Checker: *Verifies the legitimacy of URLs using Google SafeBrowsing API.*
- Content Analyst: *Analyzes the extracted text for scam patterns.*
- Decision Maker: *Synthesizes the analyses and makes final determination.*
- Summarizer: *Generates a summary of the final determination.*
- Language Translation Specialist: *Translates the summary to the user language.*

### Orchestration

In [./agents.py](./agents.py) we create the agents and define the following workflow:
- cooperation as a team in RoundRobin fashion
- the user triggers the process with a MultiModal message (image)
- the termination is enabled all agents have completed their tasks, or if no text can be extracted by the OCR specialist in the image provided.

### App

This scam prediction process can be easily tested at https://huggingface.co/spaces/dcarpintero/minerva

### Streaming Workflow

To visualize the flow of messages among the agents we define a formatter in [./formatter.py](./formatter.py) that is integrated into the App.

### Analysis with Multi-Lingual Messages

<p align="center">
  <img src="./results/minerva.results.panel.png">
</p>

### References

- [1] [FBI's Internet Crime Complaint Center (IC3), 2023 Internet Crime Report](https://www.ic3.gov/AnnualReport/Reports/2023_IC3Report.pdf)
- [2] [AutoGen](https://github.com/microsoft/autogen/)
