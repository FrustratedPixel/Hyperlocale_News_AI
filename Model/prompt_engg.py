from langchain.prompts import ChatPromptTemplate

def create_category_prompts():
    """
    Design specialized prompts for different content categories
    Each prompt is optimized for reader-ready newspaper content
    """
    
    # Common instructions for all prompts
    common_instructions = """
    
    IMPORTANT WRITING GUIDELINES:
    - Write directly for newspaper readers, not as an analysis of the text
    - Use confident, declarative statements only
    - Do NOT mention limitations like "text is limited", "details not provided", "may have occurred"
    - Do NOT use hedging language like "potentially", "suggests", "implies"
    - If you need more details, simply end with: "For additional details, refer to the local newspaper." at the end of the summary.
    - Write in active voice and present factual information as facts
    - Do not mention the source text or analysis process
    - Write everything as detailed as possible.
    """
    
    prompts = {
        "community_social": ChatPromptTemplate.from_template(f"""
        Based on the following local newspaper content, generate a headline and detailed summary focusing on community and social initiatives:

        Context: {{context}}

        Please provide:
        1. A compelling headline (max 80 characters)
        2. A detailed overview of the key community activities, volunteer efforts, or social programs (no limit on max characters).
        3. Key participants, dates, and impact mentioned

        Focus on: Clean-ups, charitable drives, resident association activities, civic engagement, community programs and similar stuff.
        {common_instructions}
        """),

        "infrastructure_news": ChatPromptTemplate.from_template(f"""
        Based on the following local newspaper content, summarize infrastructure and general news:

        Context: {{context}}

        Please provide:
        1. A clear headline (max 80 characters)
        2. A summary of infrastructure updates, government schemes, or municipal services (no limit on max characters).
        3. Timeline and impact on residents

        Focus on: Road projects, municipal services, government schemes, neighborhood developments and similar stuff.
        {common_instructions}
        """),

        "cultural_events": ChatPromptTemplate.from_template(f"""
        Based on the following local newspaper content, summarize cultural and arts events:

        Context: {{context}}

        Please provide:
        1. An engaging headline (max 80 characters)
        2. A summary highlighting cultural activities and events (no limit on max characters).
        3. Dates, venues, and participation details

        Focus on: Festivals, music/dance events, theater, storytelling sessions, temple festivals and similar stuff.
        {common_instructions}
        """),

        "health_education": ChatPromptTemplate.from_template(f"""
        Based on the following local newspaper content, summarize health, environment, and education initiatives:

        Context: {{context}}

        Please provide:
        1. An informative headline (max 80 characters)
        2. A summary of health camps, workshops, or educational programs (no limit on max characters).
        3. Key benefits and participation details

        Focus on: Health camps, awareness sessions, workshops, educational programs and similar stuff.
        {common_instructions}
        """),

        "classified_marketplace": ChatPromptTemplate.from_template(f"""
        Based on the following local newspaper content, summarize classified advertisements and marketplace notices:

        Context: {{context}}

        Please provide:
        1. A clear headline (max 80 characters)
        2. A summary of classified advertisements, marketplace listings, and commercial notices (no limit on max characters).
        3. Key categories of listings and notable trends

        Focus on: Real estate listings, job postings (situation vacant), used goods for sale, rental properties, services offered, business opportunities and similar marketplace content.
        
        Note: Provide general trends and categories rather than specific personal details or contact information.
        {common_instructions}
        """),

        "obituaries_personal": ChatPromptTemplate.from_template(f"""
        Based on the following local newspaper content, summarize obituaries and personal notices with appropriate sensitivity:

        Context: {{context}}

        Please provide:
        1. A respectful headline (max 80 characters)
        2. A sensitive summary of personal notices and community remembrances (no limit on max characters).
        3. General information about community impact or notable contributions

        Focus on: Obituary announcements, memorial notices, family remembrances, community tributes and similar personal notices.
        
        Note: Maintain dignity and respect in all summaries. Focus on community aspects rather than specific personal details.
        {common_instructions}
        """),

        "general_weekly": ChatPromptTemplate.from_template(f"""
        Based on the following local newspaper content, create a comprehensive weekly summary:

        Context: {{context}}

        Please provide:
        1. A comprehensive headline (max 80 characters)
        2. A summary covering the key happenings across all categories. Be as detailed as possible. (no limit on max characters).
        3. Most important developments affecting residents

        Include: All significant news, events, and announcements from the week.
        {common_instructions}
        """)
    }
    
    return prompts

# Create prompt templates
category_prompts = create_category_prompts()
