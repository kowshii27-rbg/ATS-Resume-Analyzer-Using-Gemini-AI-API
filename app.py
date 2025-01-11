import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf
from dotenv import load_dotenv
import json
import base64

# Load environment variables
load_dotenv()

# Configure Google Gemini API
GOOGLE_API_KEY = "Your_gemini_api"  
genai.configure(api_key=GOOGLE_API_KEY)

def add_watermark():
    st.markdown(
        """
        <style>
        .watermark {
            position: fixed;
            bottom: 20px;
            right: 20px;
            opacity: 0.7;
            z-index: 1000;
            color: #1f1f1f;
            font-size: 16px;
            font-weight: bold;
            background-color: rgba(255, 255, 255, 0.8);
            padding: 5px 10px;
            border-radius: 5px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        </style>
        <div class='watermark'>Done by Kowshik</div>
        """,
        unsafe_allow_html=True
    )

def get_gemini_response(input_text, pdf_content, prompt):
    """
    Calls the Gemini AI model to get a response.
    """
    try:
        model = genai.GenerativeModel('gemini-pro')
        full_prompt = f"{prompt}\n\nResume Content:\n{pdf_content}\n\nJob Description:\n{input_text}"
        response = model.generate_content(full_prompt)
        
        # Clean the response text
        response_text = response.text.strip()
        
        # Remove any markdown code block indicators if present
        response_text = response_text.replace('```json', '').replace('```', '').strip()
        
        # Parse the JSON
        return json.loads(response_text)
    except json.JSONDecodeError as e:
        return {
            "JD Match": "0%",
            "MissingKeywords": ["Error parsing response"],
            "Profile Summary": "Failed to analyze resume. Please try again.",
            "Improvement Suggestions": ["Please try submitting again"]
        }
    except Exception as e:
        return {
            "JD Match": "0%",
            "MissingKeywords": [str(e)],
            "Profile Summary": "An error occurred during analysis.",
            "Improvement Suggestions": ["Please try submitting again"]
        }

def input_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in range(len(reader.pages)):
        page = reader.pages[page]
        text += str(page.extract_text())
    return text

# prompt template with stricter formatting
input_prompt = """
You are an ATS (Applicant Tracking System) analyzer. Your task is to return ONLY a JSON response in the exact format shown below, with no additional text or explanations:

{
    "JD Match": "85%",
    "MissingKeywords": ["keyword1", "keyword2"],
    "Profile Summary": "Clear summary text here",
    "Improvement Suggestions": ["suggestion1", "suggestion2"]
}

Analyze the resume against the job description considering:
1. Technical skills match
2. Experience relevance
3. Required qualifications
4. Core competencies

IMPORTANT: 
- Ensure the response is ONLY the JSON object
- Use proper JSON formatting with double quotes
- Do not add any explanation text before or after the JSON
- Percentage should be a string like "85%"
- Arrays should contain at least 2 items
"""

## streamlit app
st.title("Smart ATS")
add_watermark()
st.text("Improve Your Resume ATS")
jd = st.text_area("Paste the Job Description")
uploaded_file = st.file_uploader("Upload Your Resume", type="pdf", help="Please upload the pdf")

submit = st.button("Submit")

if submit:
    if uploaded_file is not None:
        text = input_pdf_text(uploaded_file)
        response = get_gemini_response(jd, text, input_prompt)
        
        st.subheader("ATS Analysis Results")
        try:
            # Display JD Match
            st.markdown(f"### Match Score: {response['JD Match']}")
            
            # Display Missing Keywords
            st.markdown("### Missing Keywords")
            for keyword in response['MissingKeywords']:
                st.markdown(f"- {keyword}")
            
            # Display Profile Summary
            st.markdown("### Profile Summary")
            st.write(response['Profile Summary'])
            
            # Display Improvement Suggestions
            st.markdown("### Improvement Suggestions")
            for suggestion in response['Improvement Suggestions']:
                st.markdown(f"- {suggestion}")
                
        except (json.JSONDecodeError, KeyError) as e:
            st.error("Failed to parse the response. Showing raw response:")
            st.write(response)
    else:
        st.error("Please upload the resume and provide the job description.")