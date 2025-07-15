import streamlit as st
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_ollama import OllamaLLM
import regex as re
import random
from utils import clean_response

prompts_dir = "./prompts"

llm = OllamaLLM(
    model="llama2", callback_manager=CallbackManager([StreamingStdOutCallbackHandler()])
)

# Setup
st.title("Practice Salary Negotiation")

if "llm" not in st.session_state:
    st.session_state['llm'] = llm

if "reset" not in st.session_state:
    st.session_state.reset = False

if "messages" not in st.session_state or st.session_state.reset:
    st.session_state.messages = []

if "initialized" not in st.session_state or st.session_state.reset:
    st.session_state.initialized = False

if "information" not in st.session_state or st.session_state.reset:
    st.session_state.information = dict()

if "negotiation_data" not in st.session_state or st.session_state.reset:
    st.session_state.negotiation_data = {'current_offer': None, 'max_offer': None}

st.session_state.reset = False
accepted = False
declined = False
job_title = st.session_state.information.get('title', '')


def reset_chat():
    st.session_state.messages = []
    st.session_state.initialized = False
    st.session_state.information = dict()


# Initialize
if not st.session_state.initialized:
    with st.chat_message("Recruiter"):
        st.write("Welcome to the Salary Negotiation Chatbot!")

    with st.form("Initial information"):
        st.write("Please enter the following job information:")
        industry = st.text_input("Industry:")
        title = st.text_input("Job Title:")
        city = st.text_input("City:")

        submitted = st.form_submit_button("Confirm")

        if submitted:
            # Reject incomplete input
            if len(industry) < 3 or len(title) < 3 or len(city) < 2:
                with st.chat_message("Recruiter"):
                    st.write("Please complete the form!")

            else:

                # Validate input
                with st.chat_message("Recruiter"):
                    with st.spinner("Validating input..."):
                        check_initial_info = []

                        with open(f"{prompts_dir}/check_initial_info_prompt.txt", "r", encoding='utf-8') as f:
                            check_initial_info_prompt = f.read()
                            check_title = llm(check_initial_info_prompt +
                                              f"{title} is a job title.").strip().rstrip('.').split()[-1]
                            check_city = llm(check_initial_info_prompt +
                                             f"There is at least one city called {city}.").strip().rstrip('.').split()[-1]
                initial_info_error = ""
                if check_title.lower() == 'false':
                    initial_info_error = "job title"
                if check_city.lower() == 'false':
                    if initial_info_error:
                        initial_info_error += " and city"
                    else:
                        initial_info_error += "city"

                if initial_info_error:
                    with st.chat_message("Recruiter"):
                        st.write(f"Please enter valid {initial_info_error}!")
                else:
                    st.session_state.initialized = True
                    st.session_state.information = {'industry': industry, 'job_title': title, 'city': city}

                    with st.chat_message("Recruiter"):
                        with st.spinner("Thank you! We can now begin..."):

                            # Prompt initialize starting and max offers
                            with open(f"{prompts_dir}/salary_prompt.txt", "r", encoding='utf-8') as f:
                                current_offer = llm(f.read().format(industry=industry, title=title,
                                                                    city=city, offer='STARTING OFFER'))
                                current_offer = float(re.sub(r'[^\d.]', '', current_offer))

                            with open(f"{prompts_dir}/salary_prompt.txt", "r", encoding='utf-8') as f:
                                max_offer = llm(f.read().format(industry=industry, title=title,
                                                                city=city, offer='MAX OFFER'))
                                max_offer = float(re.sub(r'[^\d.]', '', max_offer))

                            st.session_state.negotiation_data['max_offer'] = max_offer
                            st.session_state.negotiation_data['current_offer'] = current_offer

                            # Write initital offer email
                            with open(f"{prompts_dir}/system_prompt.txt", "r", encoding='utf-8') as f:
                                system_prompt = f.read().format(industry=industry, title=title,
                                                                city=city, starting_salary=current_offer)

                            st.session_state.messages.append({"role": "Recruiter", "content": system_prompt})
                            response = clean_response(llm(system_prompt), job_title)
                    with st.chat_message("Recruiter"):
                        st.write(response)
                        st.session_state.messages.append({"role": "Recruiter", "content": response})

# Chat Loop
if st.session_state.initialized:
    if prompt := st.chat_input("What is your response?  Hint: It pays to be nice!"):
        with st.chat_message("Candidate"):
            st.write(prompt)

        # Validate
        with st.spinner("Validating input..."):
            prompt_bow = prompt.split()
            random.shuffle(prompt_bow)

            with open(f"{prompts_dir}/check_response.txt", "r", encoding='utf-8') as f:
                check_response = llm(f.read().format(prompt_bow=prompt_bow))

        if len(check_response) > 1:
            for keyword in ['GOOD', 'STRANGE', 'RUDE']:
                find_keyword = re.compile(r'\b{}\b'.format(re.escape(keyword)))
                if find_keyword.search(check_response):
                    check_response = keyword

        if check_response.lower().strip() != 'good':
            # Terminate: negotiation breakdown
            with st.chat_message("Recruiter"):
                with st.spinner("Drafting response..."):
                    with open(f"{prompts_dir}/withdraw_prompt.txt", "r", encoding="utf-8") as f:
                        response = clean_response(llm(f.read().format(bad=check_response)), job_title)
                    st.write(response)

            with st.form("Fail"):
                st.write("Unfortunately, you did not get the job.\n Try again?")
                st.form_submit_button('Yes', on_click=reset_chat)

        else:
            # Determine candidate's most recent negotiation move
            st.session_state.messages.append({"role": "Candidate", "content": prompt})

            if st.session_state.messages[-1]["role"] != "Recruiter":
                with st.chat_message("Recruiter"):
                    with st.spinner("Drafting response..."):

                        dialogue = f"Candidate: {st.session_state.messages[0]['content']}"
                        for message in st.session_state.messages[-2:-1]:
                            if message["role"] == "Candidate":
                                dialogue += f"Candidate: {message['content']}\n\n"
                            else:
                                dialogue += f"Recruiter: {message['content']}\n\n"

                        with open(f"{prompts_dir}/check_end_prompt.txt", "r", encoding='utf-8') as f:
                            check_end_prompt = llm(f.read().format(last_response=prompt))

                            get_accept = re.compile('ACCEPTED')
                            get_decline = re.compile('DECLINED')

                            if get_accept.search(check_end_prompt[-10:]):
                                # Terminate: accept offer
                                accepted = True
                                with open(f"{prompts_dir}/finalize_prompt.txt", "r", encoding='utf-8') as f:
                                    dialogue += f.read().format(last_message=prompt)
                                    response = clean_response(llm(dialogue), job_title)

                            elif get_decline.search(check_end_prompt[-10:]):
                                # Terminate: decline job
                                declined = True
                                with open(f"{prompts_dir}/goodbye_prompt.txt", "r", encoding='utf-8') as f:
                                    dialogue += f.read().format(last_message=prompt)
                                    response = clean_response(llm(dialogue), job_title)

                            else:
                                # Reason through candidate's offer and determine counter offer
                                with open(f"{prompts_dir}/counter_offer_prompt.txt", "r", encoding='utf-8') as f:
                                    counter_offer = f.read().format(prompt=prompt,
                                                                    max_offer=st.session_state.negotiation_data[
                                                                        'max_offer'],
                                                                    current_offer=st.session_state.negotiation_data[
                                                                        'current_offer'])

                                dialogue += f"Candidate: {counter_offer}\n\n"
                                response = clean_response(llm(dialogue), job_title)

                                print("\nmax_update:")
                                with open(f"{prompts_dir}/update_data.txt", "r", encoding='utf-8') as f:
                                    update_max = f.read().format(last_response=prompt,
                                                                 old_offer=st.session_state.negotiation_data[
                                                                     'max_offer'],
                                                                 compare='LEAST')
                                    st.session_state.negotiation_data['max_offer'] = llm(update_max).split(" ")[-1]
                                print("\n------")
                                print("\ncurrent_update:")
                                with open(f"{prompts_dir}/update_data.txt", "r", encoding='utf-8') as f:
                                    update_current = f.read().format(last_response=response,
                                                                     old_offer=st.session_state.negotiation_data[
                                                                         'current_offer'],
                                                                     compare='GREATEST')
                                    st.session_state.negotiation_data['current_offer'] = llm(update_current).split(" ")[-1]

                        placeholder = st.empty()
                        full_response = ''
                        for word in response.split(" "):
                            if word:
                                if word[-7:] == 'Action:' or word[-5:] == 'Note:':
                                    break
                                if word.strip()[-1] == "0":
                                    full_response += word + "\n"
                                else:
                                    full_response += word + " "
                            placeholder.markdown(full_response)
                        placeholder.markdown(full_response)

                        # End game
                        if accepted:
                            with st.form("Success"):
                                st.write(f"Congratulations on getting your job offer"
                                         f" for a salary of {st.session_state.negotiation_data['current_offer']}!"
                                         f"\n Try again?")
                                st.form_submit_button('Yes', on_click=reset_chat)
                        elif declined:
                            with st.form("Failure"):
                                st.write(f"Unfortunately, you did not get the offer you wanted. \n Try again?")
                                st.form_submit_button('Yes', on_click=reset_chat)

                        # Continue loop
                        else:
                            message = {"role": "Recruiter", "content": full_response}
                            st.session_state.messages.append(message)

                            print(f"\nbuffer:")
                            print(st.session_state['negotiation_data'])
                            print()