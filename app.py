import streamlit as st
from groq import Groq
from PyPDF2 import PdfReader
from docx import Document
import os

# Initialize Groq client with your API key directly
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Set up the Streamlit app
st.set_page_config(
    page_title="Legal AI Assistant",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better appearance
st.markdown("""
<style>
    .stApp {
        max-width: 1000px;
        padding: 2rem;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 4px;
        border: none;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .risk-item {
        padding: 1rem;
        margin: 0.5rem 0;
        background-color: #fff8f0;
        border-left: 4px solid #ff9800;
        border-radius: 0 4px 4px 0;
    }
    .analysis-section {
        padding: 1rem;
        margin: 1rem 0;
        background-color: #f5f5f5;
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)

def extract_text(uploaded_file):
    """Extract text from PDF, DOCX or TXT files"""
    if uploaded_file.type == "application/pdf":
        reader = PdfReader(uploaded_file)
        return "\n".join([page.extract_text() for page in reader.pages])
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = Document(uploaded_file)
        return "\n".join([para.text for para in doc.paragraphs])
    else:
        return uploaded_file.getvalue().decode("utf-8")

def analyze_document(text, prompt):
    """Send to Groq API and get response"""
    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a legal expert analyzing contracts."},
                {"role": "user", "content": f"{prompt}\n\nDOCUMENT:\n{text}"}
            ],
            model="llama-3.1-8b-instant",
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    st.title("📄 Legal Document AI Assistant")
    st.write("Upload contracts or legal documents for instant analysis using Groq AI")
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Choose a legal document", 
        type=["pdf", "docx", "txt"],
        help="Supports PDF, Word (DOCX), and text files"
    )
    
    if uploaded_file:
        st.success("File uploaded successfully!")
        
        # Extract text with spinner
        with st.spinner("Reading document..."):
            text = extract_text(uploaded_file)
        
        # Show extracted text toggle
        if st.checkbox("Show extracted text"):
            st.text_area("Document Text", text, height=200)
        
        # Analysis options
        st.subheader("Select Analysis Type")
        analysis_type = st.radio(
            "What would you like to analyze?",
            options=[
                "Quick Summary",
                "Identify Parties",
                "Key Dates & Deadlines", 
                "Risk Analysis",
                "Full Analysis"
            ],
            horizontal=True
        )
        
        # Analyze button
        if st.button("Analyze Document"):
            with st.spinner(f"Performing {analysis_type}..."):
                if analysis_type == "Quick Summary":
                    prompt = "Provide a concise 3-5 sentence summary of this legal document."
                    result = analyze_document(text, prompt)
                    st.subheader("Document Summary")
                    st.write(result)
                
                elif analysis_type == "Identify Parties":
                    prompt = """List all parties in this contract with their roles. 
                    Format as: 1. [Party Name] - [Role]"""
                    result = analyze_document(text, prompt)
                    st.subheader("Parties Identified")
                    st.write(result)
                
                elif analysis_type == "Key Dates & Deadlines":
                    prompt = """Extract all important dates with their significance.
                    Format as a table with: Date | Description | Relevant Clause"""
                    result = analyze_document(text, prompt)
                    st.subheader("Key Dates")
                    st.write(result)
                
                elif analysis_type == "Risk Analysis":
                    prompt = """Identify 3-5 potential risks or problematic clauses.
                    For each, include: 1) The relevant text 2) Why it's risky 3) Suggested changes"""
                    result = analyze_document(text, prompt)
                    st.subheader("Risk Analysis")
                    st.markdown(result)
                
                elif analysis_type == "Full Analysis":
                    cols = st.columns(2)
                    with cols[0]:
                        st.subheader("Summary")
                        summary = analyze_document(text, "Provide a 3 paragraph summary")
                        st.write(summary)
                        
                        st.subheader("Parties")
                        parties = analyze_document(text, "List all parties with roles")
                        st.write(parties)
                    
                    with cols[1]:
                        st.subheader("Key Dates")
                        dates = analyze_document(text, "List important dates with significance")
                        st.write(dates)
                        
                        st.subheader("Risks")
                        risks = analyze_document(text, "Identify top 3 risks with recommendations")
                        st.markdown(risks)

if __name__ == "__main__":
    main()
