import os
import io
import re
import logging
import requests
from bs4 import BeautifulSoup
import pymupdf  # PyMuPDF
from urllib.parse import urljoin, urlparse
from pathlib import Path
from typing import Set, List, Optional
import concurrent.futures
from tqdm import tqdm
from collections import deque
import time
import random

class PDFNewsScraper:
    """Professional PDF news scraper with text extraction and normalization."""
    
    def __init__(self, max_depth: int = 5, num_pdfs: int = 5, workers: int = 4, timeout: int = 10):
        self.max_depth = max_depth
        self.num_pdfs = num_pdfs
        self.workers = workers
        self.timeout = timeout
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        }
        self._setup_logging()
    
    def _setup_logging(self) -> None:
        """Configure logging for the scraper."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def _get_website_folder_name(self, url: str) -> str:
        """Extract clean folder name from website URL."""
        parsed = urlparse(url)
        domain = parsed.netloc.replace('www.', '')
        return re.sub(r'[^\w\-_]', '_', domain)
    
    def _create_output_directory(self, base_url: str) -> Path:
        """Create output directory based on website name."""
        folder_name = self._get_website_folder_name(base_url)
        output_dir = Path.cwd() / "scraped_content" / folder_name
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir
    
    def _normalize_text(self, text: str) -> str:
        """Normalize newspaper text with irregular line breaks."""
        if not text:
            return ""
        
        # Join hyphenated words split across lines
        text = re.sub(r'(\w+)-\n(\w+)', r'\1\2', text)
        
        lines = text.split('\n')
        normalized_lines = []
        buffer = ""
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                if buffer:
                    normalized_lines.append(buffer)
                    buffer = ""
                normalized_lines.append("")
                continue
            
            # Handle headers and titles
            if len(line) < 20 and (line.isupper() or (line[0:1].isupper() and i > 0 and not lines[i-1].strip())):
                if buffer:
                    normalized_lines.append(buffer)
                    buffer = ""
                normalized_lines.append(line)
                continue
            
            ends_with_punct = bool(re.search(r'[.!?:;"\']$', line))
            
            buffer = f"{buffer} {line}" if buffer else line
            
            if ends_with_punct:
                normalized_lines.append(buffer)
                buffer = ""
        
        if buffer:
            normalized_lines.append(buffer)
        
        # Create paragraphs
        paragraph_chunks = []
        current_paragraph = []
        
        for line in normalized_lines:
            if not line:
                if current_paragraph:
                    paragraph_chunks.append(" ".join(current_paragraph))
                    current_paragraph = []
            else:
                current_paragraph.append(line)
        
        if current_paragraph:
            paragraph_chunks.append(" ".join(current_paragraph))
        
        result = "\n\n".join(paragraph_chunks)
        result = re.sub(r' +', ' ', result)
        result = re.sub(r'\n{3,}', '\n\n', result)
        
        return result
    
    def _filter_content(self, text: str) -> str:
        """Filter out non-content elements from newspaper text."""
        patterns_to_filter = [
            r'Page \d+ of \d+',
            r'Copyright ©.*?reserved',
            r'www\.[a-zA-Z0-9-]+\.[a-z]{2,}',
            r'[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}',
            r'(?:(?:\+|00)[1-9]\d{1,2}[\s-]?)?(?:\d{2,4}[\s-]?){2,5}',
            r'ADVERTISEMENT',
            r'CLASSIFIEDS'
        ]
        
        for pattern in patterns_to_filter:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        lines = text.split('\n')
        filtered_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                filtered_lines.append('')
                continue
            
            if len(line.split()) <= 2 and len(line) < 15:
                continue
                
            filtered_lines.append(line)
        
        return '\n'.join(filtered_lines)
    
    def _extract_pdf_links(self, url: str, session: requests.Session) -> Set[str]:
        """Extract PDF links from webpage."""
        try:
            response = session.get(url, timeout=self.timeout)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            return {
                urljoin(url, a["href"]) 
                for a in soup.find_all("a", href=True) 
                if a["href"].lower().endswith(".pdf")
            }
        except Exception as e:
            self.logger.error(f"Error extracting PDF links from {url}: {e}")
            return set()
    
    def _download_pdf(self, url: str, session: requests.Session) -> bytes:
        """Download PDF content with error handling."""
        try:
            # Add random delay to avoid rate limiting
            time.sleep(random.uniform(0.5, 2.0))
            response = session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.content
        except Exception as e:
            self.logger.error(f"Failed to download {url}: {e}")
            return b""
    
    def _extract_text_from_pdf(self, pdf_content: bytes) -> str:
        """Extract and normalize text from PDF bytes."""
        if not pdf_content:
            return ""
        
        try:
            with pymupdf.open(stream=io.BytesIO(pdf_content), filetype="pdf") as doc:
              raw_text = "\n".join(page.get_text() for page in doc if page.get_text())

            
            if raw_text:
                filtered_text = self._filter_content(raw_text)
                return self._normalize_text(filtered_text)
            return ""
        except Exception as e:
            self.logger.error(f"PDF extraction error: {e}")
            return ""
    
    def _discover_pdf_links(self, base_url: str) -> List[str]:
        """BFS website scraper to discover PDF links."""
        visited = set()
        pdf_links = []
        seen_pdfs = set()
        queue = deque([(base_url, 0)])
        session = requests.Session()
        session.headers.update(self.headers)

        with tqdm(desc="Discovering PDFs", unit="pages") as pbar:
            while queue:
                url, depth = queue.popleft()
                if url in visited or depth > self.max_depth:
                    continue

                visited.add(url)
                pbar.set_postfix_str(f"Depth: {depth}")
                
                # Extract PDF links
                for link in self._extract_pdf_links(url, session):
                    if link not in seen_pdfs:
                        seen_pdfs.add(link)
                        pdf_links.append(link)
                
                # Find internal links for next depth level
                if depth < self.max_depth:
                    try:
                        time.sleep(random.uniform(0.5, 1.5))  # Rate limiting
                        response = session.get(url, timeout=self.timeout)
                        soup = BeautifulSoup(response.text, "html.parser")
                        for a in soup.find_all("a", href=True):
                            link = urljoin(url, a["href"])
                            if base_url in link and link not in visited:
                                queue.append((link, depth + 1))
                    except Exception as e:
                        self.logger.error(f"Error processing {url}: {e}")
                
                pbar.update(1)
        
        return pdf_links[:self.num_pdfs]
    
    def scrape_website(self, website_url: str) -> Optional[Path]:
        """
        Scrape PDFs from a website and extract text content.
        
        Args:
            website_url: URL of the website to scrape
            
        Returns:
            Path to the output directory containing extracted texts
        """
        self.logger.info(f"Starting scrape of {website_url}")
        
        # Create output directory
        output_dir = self._create_output_directory(website_url)
        
        # Discover PDF links
        pdf_urls = self._discover_pdf_links(website_url)
        if not pdf_urls:
            self.logger.warning("No PDF links found")
            return None
        
        self.logger.info(f"Found {len(pdf_urls)} PDFs to process")
        
        # Process PDFs concurrently
        session = requests.Session()
        session.headers.update(self.headers)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.workers) as executor:
            future_to_url = {
                executor.submit(self._download_pdf, url, session): url 
                for url in pdf_urls
            }
            
            successful_extractions = 0
            for idx, future in enumerate(tqdm(concurrent.futures.as_completed(future_to_url), 
                                            total=len(future_to_url), 
                                            desc="Processing PDFs")):
                url = future_to_url[future]
                pdf_content = future.result()
                
                if not pdf_content:
                    continue
                
                text = self._extract_text_from_pdf(pdf_content)
                if not text:
                    continue
                
                # Save extracted text
                output_path = output_dir / f"extracted_text_{idx + 1}.txt"
                output_path.write_text(text, encoding="utf-8")
                
                # Log extraction statistics
                word_count = len(text.split())
                paragraph_count = text.count('\n\n') + 1
                self.logger.info(f"Extracted {word_count} words in {paragraph_count} paragraphs from PDF {idx+1}")
                successful_extractions += 1
        
        self.logger.info(f"Completed! {successful_extractions} texts saved to {output_dir}")
        return output_dir

def scrape_newspaper_website(website_url: str, max_depth: int = 5, num_pdfs: int = 5, workers: int = 4) -> Optional[Path]:
    """
    Convenience function to scrape a single newspaper website.
    
    Args:
        website_url: URL of the website to scrape
        max_depth: Maximum depth for link discovery
        num_pdfs: Number of PDFs to process
        workers: Number of concurrent workers
        
    Returns:
        Path to output directory or None if failed
    """
    scraper = PDFNewsScraper(max_depth=max_depth, num_pdfs=num_pdfs, workers=workers)
    return scraper.scrape_website(website_url)

def scrape_multiple_websites(websites: List[str], **kwargs) -> List[Path]:
    """
    Scrape multiple newspaper websites.
    
    Args:
        websites: List of website URLs to scrape
        **kwargs: Additional arguments for PDFNewsScraper
        
    Returns:
        List of output directory paths
    """
    scraper = PDFNewsScraper(**kwargs)
    results = []
    
    for website in websites:
        result = scraper.scrape_website(website)
        if result:
            results.append(result)
    
    return results

if __name__ == "__main__":
    # Example usage for multiple websites
    websites = [
        "https://adyartimes.in/epaper/",
        "https://www.mylaporetimes.com/mt-epaper/"
    ]
    results = scrape_multiple_websites(websites, max_depth=3, num_pdfs=5)
