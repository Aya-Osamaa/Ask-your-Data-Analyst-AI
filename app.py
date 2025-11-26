import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io
import time
import re # Added for better explanation formatting

st.set_page_config(page_title="Mistral Data Analyst", layout="wide")

st.title("📊 Chat with your CSV/Excel 🤖")
st.markdown("**Your Personal Data Analyst, Powered by Mistral-7B**")

# File loading function
@st.cache_data
def load_data(file):
    file.seek(0)
    file_extension = file.name.split('.')[-1].lower()
    file_stream = io.BytesIO(file.read())

    df = None
    if file_extension in ['csv']:
        for enc in ["utf-8", "latin-1", "iso-8859-1"]:
            try:
                file_stream.seek(0)
                df = pd.read_csv(file_stream, encoding=enc)
                break
            except Exception:
                continue
    elif file_extension in ['xlsx', 'xls']:
        try:
            df = pd.read_excel(file_stream, engine='openpyxl' if file_extension == 'xlsx' else None)
        except Exception:
            return None
    
    if df is not None:
         # Clean column names to match backend processing
        df.columns = df.columns.str.replace('[^A-Za-z0-9_]+', '', regex=True).str.replace(' ', '_')
    return df

def execute_chart_safely(code_string, dataframe):
    """Safely execute chart code"""
    try:
        # Create a copy of the dataframe with cleaned columns
        df_clean = dataframe.copy() 
        df_clean.columns = df_clean.columns.str.replace('[^A-Za-z0-9_]+', '', regex=True).str.replace(' ', '_')
        
        local_vars = {
            'df': df_clean, # Pass the cleaned DataFrame
            'pd': pd,
            'px': px,
            'go': go
        }
        
        exec(code_string, globals(), local_vars)
        fig = local_vars.get('fig')
        return fig, None
        
    except Exception as e:
        return None, str(e)

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    # NOTE: User MUST update this URL after the Kaggle notebook prints the new one
    api_url = st.text_input(
        "Mistral Backend URL:", 
        value="https://unpitying-gala-unirritating.ngrok-free.dev/analyze", 
        help="Paste the Ngrok URL printed in your Kaggle notebook here."
    )
    
    st.markdown("---")
    st.subheader("🚀 Quick Questions")
    
    quick_questions = {
        "Top Sales": "What are the top 5 products by sales revenue?",
        "Regional Distribution": "Show the percentage sales distribution by region.",
        "Monthly Trend": "What is the monthly sales trend over the entire period?",
        "Comparison": "Compare total sales between the last two full years in the data.",
        "Data Overview": "Give me a comprehensive data overview including columns, types, and value ranges."
    }
    
    # Store query in session state when a quick button is clicked
    for label, question in quick_questions.items():
        if st.button(f"📊 {label}", use_container_width=True):
            st.session_state.current_query = question

# File upload
uploaded_file = st.file_uploader("Upload CSV or Excel file", type=["csv", "xlsx", "xls"])

if uploaded_file is not None:
    df_preview = load_data(uploaded_file)
    
    if df_preview is not None and not df_preview.empty:
        st.success(f"✅ Data loaded: {len(df_preview)} rows × {len(df_preview.columns)} columns")
        
        with st.expander("📋 Data Preview"):
            st.dataframe(df_preview.head())
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Rows", len(df_preview))
                if 'Quantity' in df_preview.columns:
                    st.metric("Total Units", f"{int(df_preview['Quantity'].sum()):,}")
            with col2:
                st.metric("Total Columns", len(df_preview.columns))
                if 'Category' in df_preview.columns:
                    st.metric("Unique Categories", len(df_preview['Category'].unique()))
        
        st.write("---")
        
        # Query input (uses session state for pre-filling)
        query = st.text_area(
            "Ask Mistral-7B about your data:",
            value=st.session_state.get('current_query', 'What is the monthly sales trend over the entire period?'),
            height=100,
            placeholder="E.g., What are the best-selling products? Compare sales between 2023 and 2024...",
            key="query_input" # Use a key for the text_area
        )
        
        # Update session state after user types
        st.session_state.current_query = query
        
        if st.button("🔍 Analyze with Mistral-7B", type="primary"):
            if not query:
                st.warning("Please enter a question")
            else:
                with st.spinner("🤖 Mistral-7B is analyzing your data... (10-30 seconds)"):
                    try:
                        start_time = time.time()
                        
                        # Need to re-read the file to ensure the file pointer is at the start for the request
                        uploaded_file.seek(0) 
                        files = {"file": (uploaded_file.name, uploaded_file, "application/octet-stream")}
                        data = {"query": query}
                        
                        # Use a longer timeout for LLM
                        response = requests.post(api_url, files=files, data=data, timeout=120) 
                        processing_time = time.time() - start_time
                        
                        if response.status_code == 200:
                            result = response.json()
                            
                            if "error" in result:
                                st.error(f"❌ Error: {result['error']}")
                            else:
                                st.success(f"✅ Mistral-7B Analysis Complete ({processing_time:.1f}s)")
                                
                                # Display explanation
                                explanation = result.get('explanation', 'No analysis provided.')
                                st.subheader("📝 Final Analysis and Conclusion")
                                
                                # Enhance markdown rendering for better appearance (optional: add emojis)
                                final_explanation = explanation.replace("1.", "⭐ **Insight 1:**").replace("2.", "⭐ **Insight 2:**").replace("3.", "⭐ **Conclusion:**").replace("\n", "\n\n")
                                
                                st.markdown(final_explanation)
                                
                                # Display chart
                                chart_code = result.get('chart_code', '')
                                if chart_code and chart_code.strip():
                                    st.subheader("📈 Visualization")
                                    
                                    fig, error = execute_chart_safely(chart_code, df_preview)
                                    
                                    if fig is not None:
                                        st.plotly_chart(fig, use_container_width=True)
                                        
                                        with st.expander("🔧 View Generated Code"):
                                            st.code(chart_code, language='python')
                                    else:
                                        st.warning("Could not generate chart. Please check the data columns.")
                                        if error:
                                            st.error(f"Chart Generation Error: {error}")
                                else:
                                    st.info("No visualization was generated for this question.")
                                
                        else:
                            st.error(f"Connection failed (Status: {response.status_code}). Please check the backend URL and Ngrok tunnel.")
                            
                    except requests.exceptions.Timeout:
                        st.error("⏰ Analysis timed out. The LLM took too long to respond. Try simplifying the question or checking the backend server.")
                    except requests.exceptions.ConnectionError:
                        st.error("🔌 Connection failed. Check your Ngrok URL and ensure the Kaggle backend is still running.")
                    except Exception as e:
                        st.error(f"Unexpected error in Streamlit app: {e}")

    elif uploaded_file is not None and (df_preview is None or df_preview.empty):
        st.error("❌ Failed to load data. Please ensure the file is a valid CSV or Excel file.")

# Initialize session state for query
if 'current_query' not in st.session_state:
    st.session_state.current_query = "What is the monthly sales trend over the entire period?"