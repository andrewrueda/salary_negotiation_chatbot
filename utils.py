
def clean_response(response, job_title=""):
    cleaned_response = response.replace('[Candidate Name]', 'Candidate')
    cleaned_response = cleaned_response.replace('[Candidate]', 'Candidate')
    cleaned_response = cleaned_response.replace('[Recruiter Name]', 'Recruiter')
    cleaned_response = cleaned_response.replace('[Recruiter]', 'Recruiter')
    cleaned_response = cleaned_response.replace('[Job Title]', job_title)
    cleaned_response = cleaned_response.replace('[Company Name]', 'Business Time Inc.')
    cleaned_response = cleaned_response.replace('[Your Name]', '')
    return cleaned_response



