import os
import sys
import json
import asyncio
import logging
import platform
import subprocess
import pandas as pd
import streamlit as st
from issue_scraper import scrape_issuu_results

# Set environment variable to disable file watcher
os.environ["STREAMLIT_SERVER_FILE_WATCHER_TYPE"] = "none"

# Configure logging for Streamlit
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def install_playwright():
    """Install Playwright and its dependencies."""
    try:
        # Check if Playwright is already installed
        import playwright
        logger.info("Playwright is already installed")
        return True
    except ImportError:
        logger.info("Playwright not found. Installing...")
        
        # Create a placeholder in the sidebar
        status_placeholder = st.sidebar.empty()
        status_placeholder.info(" Installing Playwright and its dependencies...")
        
        try:
            # Install Playwright package
            logger.info("Installing Playwright package...")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                "playwright==1.48.0",
                "playwright-stealth==1.0.6"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Install browsers
            logger.info("Installing Playwright browsers...")
            subprocess.check_call([
                sys.executable, "-m", "playwright", 
                "install", "chromium"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Install system dependencies (only on Linux)
            if platform.system() == 'Linux':
                logger.info("Installing system dependencies...")
                subprocess.check_call([
                    sys.executable, "-m", "playwright", 
                    "install-deps"
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            logger.info("Playwright installation completed successfully")
            status_placeholder.success(" Playwright installed successfully!")
            return True
            
        except subprocess.CalledProcessError as e:
            error_msg = f"Failed to install Playwright. Error: {e.stderr.decode() if e.stderr else str(e)}"
            logger.error(error_msg)
            status_placeholder.error(f" Error installing Playwright: {error_msg}")
            return False
        except Exception as e:
            error_msg = f"Unexpected error during installation: {str(e)}"
            logger.error(error_msg)
            status_placeholder.error(f" Unexpected error: {error_msg}")
            return False

# Set page config early to avoid rendering issues
st.set_page_config(
    page_title="Issuu Scraper",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Show loading message
with st.spinner("Initializing application..."):
    # Install Playwright when the app starts
    if not install_playwright():
        st.error("❌ Failed to install required dependencies. Please check the logs and try again.")
        st.stop()

# Now that we have all dependencies, import Playwright
import playwright

# Set WindowsProactorEventLoopPolicy for Windows
if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    logger.info("Applied WindowsProactorEventLoopPolicy for asyncio compatibility")

# Streamlit app configuration
st.set_page_config(page_title="Issuu Scraper", page_icon="📄", layout="wide")

# Title and description
st.title("Issuu Publication Scraper")
st.markdown("Enter a company name to scrape publications from Issuu and view or download the results.")

# Input for company name with unique key
company_name = st.text_input("Company Name", placeholder="e.g., Securite Et Signalisation S.A.S.", key="company_name_input")

# Button to trigger scraping
if st.button("Scrape Issuu", key="scrape_button"):
    if not company_name:
        logger.error("No company name provided in UI")
        st.error("Please enter a company name.")
    else:
        logger.info(f"Starting scrape for company: {company_name}")
        with st.spinner("Scraping Issuu... This may take a moment."):
            try:
                # Call the async scraper function
                matching_results, non_matching_results = asyncio.run(scrape_issuu_results(company_name))
                
                if matching_results or non_matching_results:
                    logger.info(f"Found {len(matching_results)} matching and {len(non_matching_results)} non-matching publications")
                    st.success(f"Found {len(matching_results)} matching and {len(non_matching_results)} non-matching publications!")
                    
                    # Display Matching Results
                    if matching_results:
                        st.subheader("Matching Results (Author Link Similar to Company Name)")
                        df_matching = pd.DataFrame(matching_results)
                        df_matching['title'] = df_matching.apply(lambda row: f'<a href="{row["publication_link"]}" target="_blank">{row["title"]}</a>', axis=1)
                        df_matching['author_link'] = df_matching['author_link'].apply(lambda x: f'<a href="{x}" target="_blank">{x}</a>')
                        st.markdown(df_matching[['title', 'author_link', 'price']].to_html(escape=False, index=False), unsafe_allow_html=True)
                    else:
                        st.info("No matching results found.")
                    
                    # Display Non-Matching Results
                    if non_matching_results:
                        st.subheader("Non-Matching Results")
                        df_non_matching = pd.DataFrame(non_matching_results)
                        df_non_matching['title'] = df_non_matching.apply(lambda row: f'<a href="{row["publication_link"]}" target="_blank">{row["title"]}</a>', axis=1)
                        df_non_matching['author_link'] = df_non_matching['author_link'].apply(lambda x: f'<a href="{x}" target="_blank">{x}</a>')
                        st.markdown(df_non_matching[['title', 'author_link', 'price']].to_html(escape=False, index=False), unsafe_allow_html=True)
                    else:
                        st.info("No non-matching results found.")
                    
                    # Prepare JSON for download
                    all_results = matching_results + non_matching_results
                    json_data = json.dumps(all_results, indent=2, ensure_ascii=False)
                    st.download_button(
                        label="Download All Results as JSON",
                        data=json_data,
                        file_name=f"issuu_results_{company_name.replace(' ', '_')}.json",
                        mime="application/json",
                        key="download_button"
                    )
                else:
                    logger.warning("No results found or an error occurred")
                    st.warning("No results found or an error occurred. Check the logs for details.")
            except Exception as e:
                logger.error(f"Error during scraping in Streamlit: {str(e)}")
                st.error(f"Error during scraping: {str(e)}")

# Footer
st.markdown("---")
st.markdown("Built with Streamlit and Playwright. Logs are available in the terminal for debugging.")
