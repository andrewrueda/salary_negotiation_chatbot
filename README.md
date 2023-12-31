# Salary Negotiation Chatbot

## Overview

This is CounterChat, a customized chatbot using LLaMa2 to simulate a salary negotiation through email dialogue. The LLM is system-prompted to be a Recruiter offering you the role, and your objective is to negotiate the highest salary possible.

CounterChat is tightly guardrailed with narrow constraints in an effort to avoid this issue...


<figure>
  <img src="files/chevygpt.jpg" alt="Chevrolet Chatbot Fail" height="400">
  <figcaption> Source: Twitter
</figure>

***

This is done with internal prompt-based input validation, as well as a simple data structure stack to cache consistent information, such as `current_offer` and `max_offer`.

A professional tone will help your cause, whereas rude or off-topic trolling will likely get the offer withdrawn.

Try it out!

## Setup

### Ollama

This program uses Ollama to load LLaMa2 onto your machine.

[Download](https://ollama.ai/download)

#### Manual Installation

Linux:
```
curl https://ollama.ai/install.sh | sh
```

for more: [GitHub](https://github.com/jmorganca/ollama)

### Run Locally Using Streamlit

Install the requirements in your own environment:

```
pip install -r requirements.txt
```

To run the program, run the following shell script:

```
bash run_negotiate.sh
```

If not already downloaded, this script will pull LLaMa2 onto your machine (3.8GB).

## Usage

### Input Initial Information:

Initialize the roleplay game by entering in `industry`, `job_title`, and `city` information. Incomplete or nonsensical input will be rejected.

<img src="files/validating_input.png" alt="Validating Input" height="250"> <img src="files/invalidated_input.png" alt="Invalidated Input" height="250">

### Chat

Engage in dialogue with CounterChat to try and maximize your salary! The salary range should be appropriate for the job details. The Recruiter's decisions won't always be the same for the same input.

<img src="files/counter_offer.png" alt="Conter Offer" height="275">

The Negotiation will have an official end if you agree upon an offer, if you decline the job, or if the offer is withdrawn:

<img src="files/accepted_result.png" alt="Accepted Result" height="275"> <img src="files/decline_result.png" alt="Decline Result" height="275">
<img src="files/withdraw_result.png" alt="Withdraw Result" height="275">

