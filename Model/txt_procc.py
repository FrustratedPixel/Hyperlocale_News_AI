from langchain_community.document_loaders import DirectoryLoader, TextLoader

def process_documents_from_directory(directory_path, glob_pattern="**/*.txt"):
    loader = DirectoryLoader(
        path=directory_path,
        glob=glob_pattern,
        loader_cls=TextLoader,
        loader_kwargs={"autodetect_encoding": True}  # Handle encoding issues
    )
    
    documents = loader.load()
    return documents

def process_multiple_directories(directory_paths):
    all_docs = {}
    
    for directory_name, directory_path in directory_paths.items():
        documents = process_documents_from_directory(directory_path)
        all_docs[directory_name] = documents
        print(f"Loaded {len(documents)} documents from {directory_name}")
    
    return all_docs

# Chunking

from langchain.text_splitter import RecursiveCharacterTextSplitter

def chunk_documents(documents, chunk_size=1000, chunk_overlap=100):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len
    )
    chunks = text_splitter.split_documents(documents)
    return chunks

# Define your directory paths
directory_paths = {
    "Adayar": "scraped_content/adyartimes_in",
    "Mylapore": "scraped_content/mylaporetimes_com"
}

# Process documents from both directories separately
all_documents = process_multiple_directories(directory_paths)

# Chunk documents separately for each location
chunked_documents = {}
for location, documents in all_documents.items():
    chunks = chunk_documents(documents, chunk_size=1000, chunk_overlap=100)
    chunked_documents[location] = chunks
    print(f"Created {len(chunks)} chunks for {location}")

'''
example run
'''
'''



# Chunk details for sanity check

def analyze_chunks(chunked_documents, location_name):
    """
    Analyze chunks to understand their characteristics
    """
    chunks = chunked_documents[location_name]
    
    print(f"\n=== ANALYSIS FOR {location_name.upper()} ===")
    print(f"Total chunks: {len(chunks)}")
    
    # Chunk size statistics
    chunk_sizes = [len(chunk.page_content) for chunk in chunks]
    avg_size = sum(chunk_sizes) / len(chunk_sizes)
    min_size = min(chunk_sizes)
    max_size = max(chunk_sizes)
    
    print(f"Average chunk size: {avg_size:.2f} characters")
    print(f"Min chunk size: {min_size} characters")
    print(f"Max chunk size: {max_size} characters")
    
    # Source file distribution
    source_files = {}
    for chunk in chunks:
        source = chunk.metadata.get('source', 'Unknown')
        filename = source.split('/')[-1] if '/' in source else source
        source_files[filename] = source_files.get(filename, 0) + 1
    
    print(f"\nChunks per file:")
    for filename, count in source_files.items():
        print(f"  {filename}: {count} chunks")
    
    # Show sample chunks
    print(f"\n--- SAMPLE CHUNKS ---")
    for i in range(min(3, len(chunks))):
        print(f"\nChunk {i+1}:")
        print(f"Source: {chunks[i].metadata.get('source', 'Unknown')}")
        print(f"Length: {len(chunks[i].page_content)} characters")
        print(f"Preview: {chunks[i].page_content[:200]}...")
        print(f"Metadata: {chunks[i].metadata}")

def detailed_chunk_distribution(chunked_documents):
    """
    Show distribution of chunk sizes across all locations
    """
    print("\n=== CHUNK SIZE DISTRIBUTION ===")
    
    for location, chunks in chunked_documents.items():
        chunk_sizes = [len(chunk.page_content) for chunk in chunks]
        
        # Create size ranges
        size_ranges = {
            "0-250": 0,
            "251-500": 0, 
            "501-750": 0,
            "751-1000": 0,
            "1000+": 0
        }
        
        for size in chunk_sizes:
            if size <= 250:
                size_ranges["0-250"] += 1
            elif size <= 500:
                size_ranges["251-500"] += 1
            elif size <= 750:
                size_ranges["501-750"] += 1
            elif size <= 1000:
                size_ranges["751-1000"] += 1
            else:
                size_ranges["1000+"] += 1
        
        print(f"\n{location}:")
        for range_name, count in size_ranges.items():
            percentage = (count / len(chunks)) * 100
            print(f"  {range_name} chars: {count} chunks ({percentage:.1f}%)")

# Usage - add this after your chunking code
for location in chunked_documents.keys():
    analyze_chunks(chunked_documents, location)

detailed_chunk_distribution(chunked_documents)

'''
# sanity check code is AI generated
# Everything seems good