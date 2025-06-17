# Hyperlocale_News_AI

An end-to-end Retrieval-Augmented Generation (RAG) pipeline that automatically ingests, processes, and summarizes content from local newspapers, generating publication-quality summaries for multiple localities and content categories.

## Table of Contents

- [Overview](#overview)  
- [Features](#features)  
- [Technology Stack](#technology-stack)  
- [Installation](#installation)  
- [Configuration](#configuration)  
  - [API Rate Limiting](#api-rate-limiting)  
  - [Content Categories](#content-categories)  
- [Usage](#usage)  
  1. [Data Collection](#1-data-collection)  
  2. [Document Processing](#2-document-processing)  
  3. [Generate Summaries](#3-generate-summaries)  
- [Project Structure](#project-structure)  
- [Sample Output](#sample-output)  
- [Performance Optimizations](#performance-optimizations)  
- [Future Enhancements](#future-enhancements)  
- [Contributing](#contributing)  
- [License](#license)  
- [Contact](#contact)  

## Overview

This project transforms hyperlocal newspaper content into structured, actionable summaries by combining web scraping, advanced text processing, and AI-powered summarization. The system maintains strict locality separation while providing category-specific insights across community initiatives, infrastructure updates, cultural events, and more.

## Features

- **Automated Web Scraping**  
  BFS-based scraper using BeautifulSoup to extract content from local newspaper websites  
- **Intelligent Preprocessing**  
  Removes boilerplate content (ads, navigation) with ~30% noise reduction  
- **Multi-Locality Support**  
  Separate processing pipelines for different geographic areas  
- **Category-Specific Summarization**  
  Tailored summaries for 7 distinct content categories  
- **RAG Architecture**  
  LangChain-based pipeline with Google Gemini 1.5 Flash integration  
- **Cost-Effective Operation**  
  Built-in API rate limiting for free-tier compliance  
- **Structured Output**  
  Clean JSON format ready for downstream applications  

## Technology Stack

- **Python 3.8+**  
- **LangChain** – RAG pipeline and document processing  
- **Google Gemini 1.5 Flash** – Language model and embeddings  
- **ChromaDB** – Vector database for embeddings storage
- **BeautifulSoup4** – Web scraping and HTML parsing  
- **Requests** – HTTP client for web scraping  

## Installation

1. **Clone the repository**  
   ```bash
   git clone https://github.com/FrustratedPixel/Hyperlocale_News_AI.git
   cd Hyperlocale_News_AI
   ```

3. **Set up environment variables**  
   ```bash
   export GOOGLE_API_KEY="your_gemini_api_key"
   ```

## Configuration

### API Rate Limiting

The system is configured for Google Gemini free tier limits:  
- 15 requests per minute  
- 1,500 requests per day  

### Content Categories

- Community & Social Initiatives  
- Infrastructure & General News  
- Cultural & Arts Events  
- Health, Environment & Education  
- Classified Marketplace  
- Obituaries & Personal Notices  
- General Weekly Summary  

## Sample Output

```json
{
  "locality": "adyar",
  "category": "community_social",
  "headline": "Community Clean-Up Drive Engages 200+ Volunteers",
  "short_summary": "Adyar residents organized a successful beach cleanup...",
  "detailed_content": "Full detailed summary with participants, dates, and impact...",
  "generated_at": "2025-06-17T12:01:00",
  "query_used": "What community activities are mentioned?"
}
```

## Performance Optimizations

- **Chunking Strategy**  
  Optimized chunk size (1000 tokens) with 100-token overlap  
- **Retrieval Configuration**  
  k=6 documents per query for balanced context  
- **Prompt Engineering**  
  Eliminates meta-commentary for publication-ready output  
- **Batch Processing**  
  Efficient handling of large document collections  

## Future Enhancements

- Multi-language support for regional newspapers  
- Real-time processing with webhook integration  
- Advanced entity extraction and relationship mapping  
- Custom embedding fine-tuning for newspaper content  
- Automated fact-checking and source verification  

## Contributing

1. Fork the repository  
2. Create a feature branch  
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. Commit your changes  
   ```bash
   git commit -m "Add some amazing feature"
   ```
4. Push to the branch  
   ```bash
   git push origin feature/amazing-feature
   ```
5. Open a Pull Request

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
