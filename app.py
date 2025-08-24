import streamlit as st
import pandas as pd
import json

# Page configuration
st.set_page_config(
    page_title="Hyperlocal News AI Dashboard",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    
    .news-card {
        border: 2px solid #e0e0e0;
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
        background-color: #fafafa;
        cursor: pointer;
        transition: all 0.3s ease;
        height: 280px;
        overflow: hidden;
    }
    
    .news-card:hover {
        border-color: #1976d2;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }
    
    .card-headline {
        font-size: 1.3rem;
        font-weight: bold;
        margin-bottom: 12px;
        line-height: 1.4;
        color: #333;
    }
    
    .card-summary {
        font-size: 1rem;
        line-height: 1.5;
        color: #666;
        margin-bottom: 15px;
    }
    
    .category-badge {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 15px;
        font-size: 0.85rem;
        font-weight: bold;
        margin-right: 10px;
        margin-bottom: 10px;
    }
    
    .community-social { background-color: #e3f2fd; color: #1976d2; }
    .cultural-events { background-color: #f3e5f5; color: #7b1fa2; }
    .health-education { background-color: #e8f5e8; color: #388e3c; }
    .infrastructure-news { background-color: #fff3e0; color: #f57c00; }
    .obituaries-personal { background-color: #fce4ec; color: #c2185b; }
    
    .locality-tag {
        display: inline-block;
        padding: 4px 10px;
        background-color: #37474f;
        color: white;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: bold;
        margin-bottom: 10px;
    }
    
    .pagination-info {
        text-align: center;
        color: #666;
        margin: 20px 0;
        font-size: 1.1rem;
    }
    
    .selected-article {
        background-color: #f5f5f5;
        border: 2px solid #1976d2;
        border-radius: 12px;
        padding: 25px;
        margin: 20px 0;
    }
    
    .selected-article h2 {
        color: #1976d2;
        font-size: 1.8rem;
        margin-bottom: 15px;
    }
    
    .selected-article p {
        font-size: 1.1rem;
        line-height: 1.6;
    }
    
    .click-hint {
        color: #1976d2;
        font-size: 0.9rem;
        font-style: italic;
        margin-top: auto;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_and_process_data(file_path: str) -> pd.DataFrame:
    """Load JSON data and process it into a clean DataFrame"""
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    df = pd.DataFrame(data)
    
    # Filter out entries with errors
    if 'error' in df.columns:
        df = df[(df['error'] != True) & (df['error'] != 'true')].copy()
    
    # Check for required columns
    required_cols = ['headline', 'detailed_content']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        return pd.DataFrame()
    
    # Clean up the data
    df = df.dropna(subset=required_cols)
    df = df[df['detailed_content'].astype(str).str.len() > 0]
    
    if len(df) == 0:
        return df
    
    # Convert to categorical for memory efficiency
    if 'locality' in df.columns:
        df['locality'] = df['locality'].astype('category')
    if 'category' in df.columns:
        df['category'] = df['category'].astype('category')
        df['category_display'] = df['category'].str.replace('_', ' ').str.title()
    
    return df

def get_category_class(category: str) -> str:
    """Return CSS class for category badge"""
    return category.replace('_', '-')

def truncate_text(text: str, max_length: int = 200) -> str:
    """Truncate text to specified length"""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."

def reset_pagination():
    """Reset pagination to first page"""
    st.session_state.page = 0

def main():
    # Initialize session state
    if 'page' not in st.session_state:
        st.session_state.page = 0
    if 'selected_article' not in st.session_state:
        st.session_state.selected_article = None

    # App header
    st.markdown('<h1 class="main-header">📰 Hyperlocale News AI</h1>', unsafe_allow_html=True)
    st.markdown('<p style="font-size: 1.2rem; color: #666;">Stay updated with community news from Adayar and Mylapore</p>', unsafe_allow_html=True)

    # Load and process data
    try:
        articles_df = load_and_process_data("locality_summaries.json")
    except FileNotFoundError:
        st.error("Could not find locality_summaries.json file. Please ensure it's in the same directory as this app.")
        return
    except json.JSONDecodeError as e:
        st.error(f"Invalid JSON format in locality_summaries.json file: {e}")
        return
    except Exception as e:
        st.error(f"Error processing data: {e}")
        return
    
    if articles_df.empty:
        st.warning("No valid articles found in the data.")
        return

    # Sidebar filters
    st.sidebar.header("🔍 Filters")
    
    # Search functionality
    search_query = st.sidebar.text_input("Search Headlines", placeholder="Enter keywords...")
    
    # Filter controls
    localities = []
    categories = []
    
    if 'locality' in articles_df.columns:
        localities = st.sidebar.multiselect(
            "Filter by Locality", 
            options=sorted(articles_df['locality'].unique()),
            default=[],
            key="locality_filter"
        )
    
    if 'category_display' in articles_df.columns:
        categories = st.sidebar.multiselect(
            "Filter by Category",
            options=sorted(articles_df['category_display'].unique()),
            default=[],
            key="category_filter"
        )
    
    # Reset pagination when filters change
    current_filters = (search_query, tuple(localities), tuple(categories))
    if 'last_filters' not in st.session_state:
        st.session_state.last_filters = current_filters
    elif st.session_state.last_filters != current_filters:
        reset_pagination()
        st.session_state.selected_article = None  # Clear selection on filter change
        st.session_state.last_filters = current_filters

    # Apply filters
    filtered_df = articles_df.copy()
    
    if search_query:
        search_mask = False
        if 'headline' in filtered_df.columns:
            search_mask |= filtered_df['headline'].astype(str).str.contains(search_query, case=False, na=False)
        if 'short_summary' in filtered_df.columns:
            search_mask |= filtered_df['short_summary'].astype(str).str.contains(search_query, case=False, na=False)
        filtered_df = filtered_df[search_mask]
    
    if localities and 'locality' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['locality'].isin(localities)]
    
    if categories and 'category_display' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['category_display'].isin(categories)]

    # Pagination setup
    ITEMS_PER_PAGE = 6  # Reduced for grid layout
    total_articles = len(filtered_df)
    total_pages = max(1, -(-total_articles // ITEMS_PER_PAGE))
    
    if st.session_state.page >= total_pages:
        st.session_state.page = max(0, total_pages - 1)
    
    start_idx = st.session_state.page * ITEMS_PER_PAGE
    end_idx = min(start_idx + ITEMS_PER_PAGE, total_articles)
    page_df = filtered_df.iloc[start_idx:end_idx]

    if total_articles == 0:
        st.info("No articles match your current filters.")
        return
    
    st.markdown(f'<p style="font-size: 1.1rem;"><strong>Showing {start_idx + 1}-{end_idx} of {total_articles} articles</strong></p>', unsafe_allow_html=True)
    
    # Display articles in grid layout (2 columns)
    cols = st.columns(2)
    
    for idx, (_, article) in enumerate(page_df.iterrows()):
        col = cols[idx % 2]
        
        with col:
            # Clean headline
            headline = str(article.get('headline', 'No headline'))
            clean_headline = headline.replace('##', '').replace('#', '').strip()
            
            # Create summary for card
            summary = str(article.get('short_summary', ''))
            if not summary or summary == clean_headline:
                summary = str(article.get('detailed_content', ''))
            
            # Clean and truncate summary
            clean_summary = summary.replace('##', '').replace('#', '').strip()
            truncated_summary = truncate_text(clean_summary, 150)
            
            # Create card HTML
            card_html = f"""
            <div class="news-card">
                <div class="locality-tag">{article.get('locality', 'Unknown')}</div>
                <div class="category-badge {get_category_class(str(article.get('category', '')))}">{article.get('category_display', 'General')}</div>
                <div class="card-headline">{clean_headline}</div>
                <div class="card-summary">{truncated_summary}</div>
                <div class="click-hint">Click to read full article →</div>
            </div>
            """
            
            # Create clickable card
            if st.button(f"Read Article {idx + 1}", key=f"article_{start_idx + idx}", help=clean_headline):
                st.session_state.selected_article = article.to_dict()
                st.rerun()
            
            # Display card
            st.markdown(card_html, unsafe_allow_html=True)

    # Display selected article
    if st.session_state.selected_article:
        st.markdown("---")
        article = st.session_state.selected_article
        
        col1, col2 = st.columns([5, 1])
        with col1:
            st.markdown('<div class="selected-article">', unsafe_allow_html=True)
            
            # Article header
            clean_headline = str(article.get('headline', '')).replace('##', '').replace('#', '').strip()
            st.markdown(f"## {clean_headline}")
            
            # Tags
            tag_col1, tag_col2 = st.columns([1, 4])
            with tag_col1:
                st.markdown(f'<span class="locality-tag">{article.get("locality", "Unknown")}</span>', unsafe_allow_html=True)
                if 'category' in article:
                    category_class = get_category_class(str(article['category']))
                    st.markdown(f'<span class="category-badge {category_class}">{article.get("category_display", "General")}</span>', unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Content
            content = str(article.get('detailed_content', 'No content available'))
            content_clean = content.replace('##', '**').replace('#', '**')
            st.markdown(content_clean)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            if st.button("✕ Close", key="close_article"):
                st.session_state.selected_article = None
                st.rerun()

    # Pagination controls
    if total_pages > 1:
        st.markdown("---")
        col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
        
        if st.session_state.page > 0:
            if col1.button("⬅️ Previous", key="prev_page"):
                st.session_state.page -= 1
                st.session_state.selected_article = None  # Clear selection on page change
                st.rerun()
        
        if st.session_state.page < total_pages - 1:
            if col5.button("Next ➡️", key="next_page"):
                st.session_state.page += 1
                st.session_state.selected_article = None  # Clear selection on page change
                st.rerun()
        
        col3.markdown(f'<div class="pagination-info">Page {st.session_state.page + 1} of {total_pages}</div>', unsafe_allow_html=True)

    # Sidebar info
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**📊 Statistics**")
    st.sidebar.markdown(f"Total Articles: {len(articles_df)}")
    st.sidebar.markdown(f"Filtered Results: {total_articles}")
    
    if not filtered_df.empty and 'category_display' in filtered_df.columns:
        st.sidebar.markdown("**Categories in Results:**")
        category_counts = filtered_df['category_display'].value_counts()
        for category, count in category_counts.items():
            st.sidebar.markdown(f"• {category}: {count}")

if __name__ == "__main__":
    main()
