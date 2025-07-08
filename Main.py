import os
import streamlit as st
import requests
import json
import pandas as pd
from dotenv import load_dotenv


from Services.pdf_processor import PDFProcessor
from Services.email_sender import EmailSender
from Services.llm_handler import LLMHandler
from Services.candidate_scorer import Candidate
from Services.cache_handler import CacheHandler

os.environ["TOKENIZERS_PARALLELISM"] = "false"

load_dotenv()

input_query = """ """


def main():
    """Main application function with enhanced UI."""

    # Add page title and favicon
    st.set_page_config(page_title="GenAI CV Job Description Ranker",
                       page_icon="🔍",
                       layout="wide")


    # Inject custom CSS for styling
    st.markdown(
        """
        <style>
        body {
            font-family: 'Arial', sans-serif;
            background-color: #f9f9f9;
        }
        .stButton>button {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 10px 20px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            margin: 4px 2px;
            cursor: pointer;
            border-radius: 8px;
            transition: background-color 0.3s, color 0.3s;
        }
        .stButton>button:hover {
            background-color: #45a049;
            color: white;
        }
        .stSidebar {
            background-color: #f0f0f0;
            padding: 10px;
            border-radius: 8px;
        }
        .candidate-card {
            background-color: white;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .candidate-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
        }
        .candidate-card h3 {
            color: #333;
            margin-bottom: 10px;
        }
        .candidate-card p {
            color: #555;
            margin: 5px 0;
        }
        .candidate-card span {
            font-weight: bold;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Add a header
    st.title("🤖 Talent Acquisition Specialist")
    st.markdown("""
        <h3 style="color: #4CAF50;">Welcome to the AI-powered Talent Acquisition Specialist!</h3>
        <p>Upload resumes and provide a job description to find the best matches.</p>
    """, unsafe_allow_html=True)

    # Sidebar for file upload
    
    st.sidebar.image("templates\image.png", use_container_width=True)

    st.sidebar.header("⚙️ Settings")
    threshold = st.sidebar.number_input(
        "Set Matching Score Threshold (%)",
        min_value=0,
        max_value=100,
        value=60,
        step=1
    )
    st.sidebar.header("📂 Upload Resumes")
    uploaded_files = st.sidebar.file_uploader(
            "Choose CV files", type=["pdf", "docx"], accept_multiple_files=True)


    # Input for job description
    st.markdown("### 📝 Enter Job Description")
    query = st.text_area("Paste the job description below:", height=200, value=input_query)

    uploaded_file = st.file_uploader("Upload a Job Description File (PDF or DOCX)", type=["pdf", "docx"])

    if uploaded_file is not None:
        # Extract text from the uploaded PDF
        pdf_text = PDFProcessor.extract_text_from_file(uploaded_file)
        query = pdf_text


    if st.button("Match Candidates"):

        cache = CacheHandler()
        embedding_model = LLMHandler.get_embedding_model()
        if uploaded_files and query.strip():
            try:
                with st.spinner('Processing CVs...'):
                    documents_with_metadata = PDFProcessor.process_multiple_documents(uploaded_files)

                    if not documents_with_metadata:
                        st.warning("No text found in the uploaded files.")
                        return
                    


                    candidate_names = list(set(doc.metadata['candidate_name']
                                               for doc in documents_with_metadata))

                    results = []
                    # all_personal_info = []  
                    progress_bar = st.progress(0)


                    # Process each candidate separately
                    for i, name in enumerate(candidate_names):




                        
                        # Filter documents for the specific candidate
                        candidate_documents = [
                            doc for doc in documents_with_metadata if doc.metadata.get('candidate_name') == name]

                        # Create a QA chain specific to this candidate
                        qa_chain = LLMHandler.create_qa_chain_with_scoring(
                            candidate_documents, embedding_model, name)
                        
                        
                        # Concatenate all text chunks for that candidate
                        resume_text = "\n".join(doc.page_content for doc in candidate_documents)

                        
                        # GROQ_API_KEY = os.getenv("GROQ_API_KEY")
                        # # 👉 1. Extract personal information via Groq
                        # prompt = f"""
                        #     Extract the following information from the candidate's resume:

                        #     - Full Name
                        #     - Email Address
                        #     - Mobile Number
                        #     - Date of Birth (if available)
                        #     - Location / Address (City, State or full address)

                        #     Resume:
                        #     \"\"\"{resume_text}\"\"\"

                        #     ⛔ Respond ONLY with a valid JSON object.
                        #     ⛔ Do NOT include any explanation, headers, or notes.
                        #     ⛔ If any field is missing or not found, return its value as null.

                        #     ✅ Example:
                        #     {{
                        #     "Full Name": "John Doe",
                        #     "Email Address": "john.doe@example.com",
                        #     "Mobile Number": "+91-1234567890",
                        #     "Date of Birth": null,
                        #     "Location / Address": null
                        #     }}
                        #     """

                        # response = requests.post(
                        #     "https://api.groq.com/openai/v1/chat/completions",
                        #     headers={
                        #         "Authorization": f"Bearer {GROQ_API_KEY}",
                        #         "Content-Type": "application/json"
                        #     },
                        #     json={
                        #         "model": "llama3-70b-8192",
                        #         "messages": [
                        #             {"role": "system", "content": "You are an expert at extracting structured data from resumes."},
                        #             {"role": "user", "content": prompt}
                        #         ]
                        #     }
                        # )

                        # data = response.json()

                        # # Try to extract content first
                        # try:
                        #     content = data['choices'][0]['message']['content'].strip()
                        # except (KeyError, IndexError) as e:
                        #     st.warning(f"⚠️ Invalid response structure for {name}: {str(e)}")
                        #     content = ""

                        # # Try to parse JSON
                        # try:
                        #     personal_info = json.loads(content)
                        # except json.JSONDecodeError:
                        #     st.warning(f"⚠️ Failed to parse JSON personal info for {name}. Raw response: {content}")
                        #     personal_info = {}


                        # print("Extracted info for", name)
                        # print(personal_info)
                        # personal_info["Candidate Name"] = name
                        # # Append to the list
                        # all_personal_info.append(personal_info)



                        if qa_chain:
                            # # Check cache first
                            # cached_score = cache.get_cached_result(query, resume_text)

                            # if cached_score:
                            #     score = cached_score
                            # else:
                            score = Candidate.analyze_candidate(qa_chain, query, name, resume_text)
                            
                            cache.store_result(query, resume_text, score)

                            # Only append candidates with a score > 0
                            if score["rating"] > 0:
                                results.append(
                                    {
                                    "name": name,
                                    # "personal_info": personal_info,
                                     "individual_scores": score.get("individual_scores", {}),
                                     "score": score["rating"],
                                     "reason": score["reason"],
                                     "documents": candidate_documents
                                     })
                                
                        # Update progress
                        progress_bar.progress((i + 1) / len(candidate_names))

                    # Sort and display only candidates with a score > 0
                    if results:
                        ranked_candidates = sorted(results,
                                                   key=lambda x: x['score'],
                                                   reverse=True)
                        st.session_state.ranked_candidates = ranked_candidates
                        st.session_state.sent_emails = set()
                    else:
                        st.warning("No candidates scored above 0.")
                        st.stop()


                    # if all_personal_info:
                    #     df_info = pd.DataFrame(all_personal_info)
                    #     csv_filename = "extracted_personal_info.csv"
                    #     df_info.to_csv(csv_filename, index=False)

                    #     st.success("✅ All personal info saved to CSV.")
                    #     st.download_button("📥 Download Personal Info CSV", data=df_info.to_csv(index=False), file_name=csv_filename, mime="text/csv")
                    # else:
                    #     st.warning("⚠️ No personal information was extracted to save.")


            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.stop()
        else:
            st.info("Please upload CVs and enter a job description to begin matching.")
            st.stop()


    if 'ranked_candidates' in st.session_state and st.session_state.ranked_candidates:
        st.subheader("🏆 Ranked Candidates")
        for rank, candidate in enumerate(st.session_state.ranked_candidates, 1):
            st.markdown(f"""
                <div class="candidate-card">
                    <h3>{rank}. {candidate['name']}</h3>
                    <p><strong>Match Score:</strong> <span style="color: red;">{candidate['score']:.1f}%</span></p>
                    <p><strong>Reason:</strong> {candidate['reason']}</p>
                    <p><strong>Individual Scores:</strong></p>
                    <ul>
                        {''.join([f"<li><strong>{k}</strong>: {v}</li>" for k, v in candidate['individual_scores'].items()])}
                    </ul>
                </div>
            """, unsafe_allow_html=True)

            # Resume content (rewritten)
            with st.expander(f"📄 View Resume for {candidate['name']}"):
                for doc in candidate["documents"]:
                    rewritten_content = LLMHandler.init_llm().invoke(
                        f"Rewrite the following content to improve clarity and readability:\n\n{doc.page_content}"
                    ).content
                    st.write(rewritten_content)


                # Add an option to view the candidate's resume
                with st.expander(f"📄 View Resume for {candidate['name']}"):
                    for doc in candidate["documents"]:
                        rewritten_content = LLMHandler.init_llm().invoke(f"Rewrite the following content to improve clarity and readability:\n\n{doc.page_content}").content
                        st.write(rewritten_content)


            # Send Email Button
            if candidate['score'] >= threshold:
                button_key = f"send_email_{candidate['name']}"
                if st.button(f"Send Interview Email to {candidate['name']}", key=button_key):
                    candidate_email = candidate["documents"][0].metadata.get('candidate_email')
                    if candidate_email:
                        if candidate['name'] not in st.session_state.sent_emails:
                            EmailSender.send_email(candidate['name'], candidate_email)
                            st.session_state.sent_emails.add(candidate['name'])
                            st.success(f"✅ Interview email sent to {candidate['name']} ({candidate_email})")
                        else:
                            st.info(f"📨 Email already sent to {candidate['name']}")
                    else:
                        st.warning("⚠️ Email not found in candidate metadata.")


if __name__ == "__main__":
    main()

