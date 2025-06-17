import json
from datetime import datetime
from RAG_model import rag_chains

def generate_category_summaries(rag_chains, category_queries):
    """
    Generate summaries for each locality and category combination
    Returns structured JSON output for easy consumption
    """
    
    # Define specific queries for each category
    category_queries = {
    "community_social": """
    Community engagement activities social initiatives volunteer programs civic participation 
    resident associations neighborhood groups charitable drives fundraising events community service 
    social gatherings networking events community building efforts local activism environmental cleanup 
    beach cleanup drives tree plantation community outreach programs social welfare initiatives 
    community meetings neighborhood watch programs local committees community development projects 
    social responsibility programs community partnerships collaborative efforts grassroots movements 
    community organizing resident participation civic duties community involvement social causes
    """,

    "infrastructure_news": """
    Infrastructure development road construction bridge projects transportation systems municipal services 
    water supply sewage systems electricity grid metro rail projects highway development urban planning 
    government schemes policy announcements public services municipal updates civic amenities 
    smart city initiatives digital infrastructure telecommunications connectivity internet services 
    public transportation bus routes traffic management parking facilities waste management 
    construction projects building permits development approvals zoning regulations urban development 
    public facilities hospitals schools government buildings parks recreation centers libraries
    """,

    "cultural_events": """
    Cultural festivals music concerts dance performances theater shows art exhibitions cultural programs 
    traditional celebrations religious festivals seasonal festivities community celebrations 
    artistic performances cultural workshops heritage events folk music classical music contemporary arts 
    storytelling sessions literary events book fairs poetry readings cultural diversity programs 
    temple festivals religious ceremonies cultural exchange programs artistic collaborations 
    creative workshops painting exhibitions sculpture displays photography contests film screenings 
    cultural heritage preservation traditional arts handicrafts cultural education programs 
    performing arts venues cultural centers community theaters art galleries museums
    """,

    "health_education": """
    Health camps medical checkups vaccination drives health awareness programs wellness workshops 
    educational seminars training programs skill development workshops health screenings 
    dental camps eye checkups cardiac health programs women's health initiatives child health programs 
    mental health awareness nutrition education fitness programs yoga sessions meditation workshops 
    health insurance information medical assistance programs preventive healthcare initiatives 
    environmental health programs sanitation awareness water quality education air quality monitoring 
    educational institutions schools colleges universities academic programs learning opportunities 
    professional development training certification programs capacity building workshops knowledge sharing
    """,

    "lifestyle_commerce": """
    Shopping centers retail stores boutiques fashion outlets seasonal sales promotional offers 
    commercial establishments business openings restaurant launches food festivals culinary events 
    lifestyle brands product launches consumer goods services marketplace activities 
    local businesses entrepreneurship startups small business initiatives commerce updates 
    retail developments shopping complexes malls market trends consumer preferences 
    service providers professional services beauty salons fitness centers recreational facilities 
    hospitality industry hotels guest houses tourism services entertainment venues 
    lifestyle trends wellness services personal care health and beauty fashion and style
    """,

    "classifieds_marketplace": """
    Real estate property sales rental listings house for sale apartment rentals commercial properties 
    job opportunities employment vacancies career opportunities recruitment drives hiring announcements 
    used goods second hand items buy sell exchange marketplace transactions classified advertisements 
    business opportunities investment opportunities partnership proposals franchise opportunities 
    services offered professional services domestic help tutoring services repair services 
    automotive vehicles for sale car rentals vehicle services transportation services 
    personal announcements relationship matrimonial missing persons found items lost and found 
    wanted listings requirements seeking services looking for accommodation roommate search
    """,

    "obituaries_personal": """
    Death announcements obituary notices memorial services funeral arrangements remembrance ceremonies 
    condolence messages family announcements personal tributes life celebrations memorial events 
    bereavement support grief counseling memorial donations charitable contributions in memory 
    funeral homes crematorium services burial services religious ceremonies last rites 
    family notices personal announcements birth announcements wedding announcements anniversary celebrations 
    graduation ceremonies achievements recognitions awards honors personal milestones 
    community sympathy support for bereaved families memorial funds legacy projects 
    personal remembrances tribute articles life stories community support during difficult times
    """,

    "general_weekly": """
    Weekly news summary local happenings community updates neighborhood events municipal announcements 
    government notifications public notices important deadlines upcoming events calendar updates 
    weather updates seasonal information emergency notifications safety alerts security updates 
    traffic advisories route diversions construction notices public transportation updates 
    utility services power outages water supply interruptions maintenance schedules service updates 
    community announcements public meetings council meetings civic updates policy changes 
    local business news economic developments commercial activities industrial updates 
    social issues community concerns resident feedback public opinion local governance administrative updates
    """
}
    
    all_summaries = []
    
    for locality, locality_chains in rag_chains.items():
        print(f"\nProcessing {locality}...")
        
        for category, query in category_queries.items():
            try:
                # Generate summary using RAG chain
                chain = locality_chains[category]
                summary_content = chain.invoke(query)
                
                # Parse the generated content to extract headline and summary
                lines = summary_content.strip().split('\n')
                headline = ""
                short_summary = ""
                detailed_content = summary_content
                
                # Extract headline (usually first non-empty line)
                for line in lines:
                    if line.strip() and not line.startswith(('1.', '2.', '3.', '-', '*')):
                        headline = line.strip()
                        break
                
                # Extract summary (look for numbered points or paragraphs)
                summary_lines = []
                for line in lines[1:]:
                    if line.strip() and (line.startswith(('2.', '3.')) or 'sentence' in line.lower()):
                        summary_lines.append(line.strip())
                
                short_summary = ' '.join(summary_lines) if summary_lines else summary_content[:200] + "..."
                
                # Structure as JSON object
                summary_obj = {
                    "locality": locality,
                    "category": category,
                    "headline": headline[:80] if headline else f"{category.replace('_', ' ').title()} Updates",
                    "short_summary": short_summary,
                    "detailed_content": detailed_content,
                    "generated_at": datetime.now().isoformat(),
                    "query_used": query
                }
                
                all_summaries.append(summary_obj)
                print(f"  ✓ Generated summary for {category}")
                
            except Exception as e:
                print(f"  ✗ Error generating summary for {category}: {str(e)}")
                
                # Add error entry
                error_obj = {
                    "locality": locality,
                    "category": category,
                    "headline": "Content Not Available",
                    "short_summary": f"Unable to generate summary: {str(e)}",
                    "detailed_content": "",
                    "generated_at": datetime.now().isoformat(),
                    "query_used": query,
                    "error": True
                }
                all_summaries.append(error_obj)
    
    return all_summaries

def save_summaries_to_json(summaries, filename="locality_summaries.json"):
    """Save summaries to JSON file for easy access"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(summaries, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(summaries)} summaries to {filename}")

# Generate all summaries
all_summaries = generate_category_summaries(rag_chains, {})

# Save to JSON file
save_summaries_to_json(all_summaries)