import pandas as pd
import numpy as np
from langchain.document_loaders import DataFrameLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
import os
from typing import List, Dict, Any
from langchain.schema import Document

class JobListingProcessor:
    def __init__(self, csv_path="data/job_listing_data.csv"):
        """
        Initialize the job listing processor with the path to the CSV file
        """
        self.csv_path = csv_path
        self.raw_df = None
        self.processed_df = None
        self.documents = []
        self.vectorstore = None
        
    def load_data(self) -> pd.DataFrame:
        """
        Load the job listing data from CSV
        """
        print(f"Loading job data from {self.csv_path}...")
        try:
            self.raw_df = pd.read_csv(self.csv_path)
            print(f"Loaded {len(self.raw_df)} job listings")
            return self.raw_df
        except Exception as e:
            print(f"Error loading CSV: {str(e)}")
            # Create a sample dataframe for testing if file doesn't exist
            self.raw_df = self._create_sample_data()
            print(f"Created sample data with {len(self.raw_df)} job listings")
            return self.raw_df
    
    def _create_sample_data(self) -> pd.DataFrame:
        """
        Create sample job listing data for testing
        """
        sample_data = {
            'job_id': list(range(1, 11)),
            'job_title': [
                'Senior Software Engineer', 
                'Data Scientist',
                'Product Manager',
                'UI/UX Designer',
                'Marketing Manager',
                'HR Manager',
                'Finance Analyst',
                'Business Development Executive',
                'Content Writer',
                'Operations Manager'
            ],
            'company_name': [
                'TechCorp', 'DataWorks', 'ProductInc', 'DesignHub',
                'MarketingPro', 'PeopleFirst', 'FinanceWorld', 'GrowthPartners',
                'ContentKing', 'OperateWell'
            ],
            'location': [
                'Bangalore', 'Mumbai', 'Delhi', 'Hyderabad',
                'Chennai', 'Pune', 'Kolkata', 'Bangalore',
                'Mumbai', 'Delhi'
            ],
            'job_description': [
                'Looking for a senior software engineer with 5+ years of experience in Java, Spring Boot, and microservices architecture.',
                'Data scientist position requiring expertise in Python, machine learning, and statistics. Experience with NLP is a plus.',
                'Product manager role for a SaaS platform. Should have experience in agile methodologies and product lifecycle management.',
                'UI/UX designer for mobile applications. Experience with Figma and Adobe XD required.',
                'Marketing manager for digital campaigns. Experience in social media marketing and analytics required.',
                'HR manager role focusing on talent acquisition and employee engagement.',
                'Finance analyst position requiring expertise in financial modeling and data analysis.',
                'Business development executive for expanding market reach. Experience in sales and negotiation required.',
                'Content writer for technical blog posts and documentation. Knowledge of SEO best practices required.',
                'Operations manager for streamlining internal processes. Experience in process optimization required.'
            ],
            'experience_required': [
                '5+ years', '3-5 years', '4-6 years', '2-4 years',
                '5-7 years', '6-8 years', '2-3 years', '3-5 years',
                '1-3 years', '5-8 years'
            ],
            'skills_required': [
                'Java, Spring Boot, Microservices, AWS',
                'Python, Machine Learning, Statistics, NLP',
                'Agile, Product Management, JIRA, User Stories',
                'UI/UX, Figma, Adobe XD, Wireframing',
                'Digital Marketing, Social Media, Analytics, Content Strategy',
                'Talent Acquisition, Employee Engagement, HR Policies',
                'Financial Modeling, Excel, Data Analysis, Forecasting',
                'Sales, Negotiation, Market Research, Client Relationship',
                'Content Writing, SEO, Technical Documentation, Blogging',
                'Process Optimization, Team Management, Resource Planning'
            ],
            'job_type': [
                'Full-time', 'Full-time', 'Full-time', 'Full-time',
                'Full-time', 'Full-time', 'Full-time', 'Full-time',
                'Contract', 'Full-time'
            ],
            'remote_option': [
                'Yes', 'Yes', 'No', 'Yes',
                'No', 'No', 'Yes', 'No',
                'Yes', 'No'
            ],
            'salary_range': [
                '20-30 LPA', '15-25 LPA', '18-28 LPA', '12-18 LPA',
                '15-22 LPA', '18-25 LPA', '10-15 LPA', '12-18 LPA',
                '8-12 LPA', '15-25 LPA'
            ],
            'posted_date': [
                '2023-08-01', '2023-08-02', '2023-08-03', '2023-08-04',
                '2023-08-05', '2023-08-06', '2023-08-07', '2023-08-08',
                '2023-08-09', '2023-08-10'
            ]
        }
        
        return pd.DataFrame(sample_data)
    
    def preprocess_data(self) -> pd.DataFrame:
        """
        Preprocess the job listing data
        """
        if self.raw_df is None:
            self.load_data()
        
        # Create a copy for processing
        self.processed_df = self.raw_df.copy()
        
        # Handle missing values
        self.processed_df = self.processed_df.fillna({
            'job_description': 'No description provided',
            'skills_required': 'Not specified',
            'experience_required': 'Not specified',
            'location': 'Not specified',
            'salary_range': 'Not disclosed',
            'remote_option': 'Not specified'
        })
        
        # Create a combined text field for better search
        self.processed_df['combined_text'] = (
            'Job Title: ' + self.processed_df['job_title'] + '\n' +
            'Company: ' + self.processed_df['company_name'] + '\n' +
            'Location: ' + self.processed_df['location'] + '\n' +
            'Experience Required: ' + self.processed_df['experience_required'] + '\n' +
            'Skills Required: ' + self.processed_df['skills_required'] + '\n' +
            'Job Type: ' + self.processed_df['job_type'] + '\n' +
            'Remote Option: ' + self.processed_df['remote_option'] + '\n' +
            'Salary Range: ' + self.processed_df['salary_range'] + '\n' +
            'Description: ' + self.processed_df['job_description']
        )
        
        print("Data preprocessing complete")
        return self.processed_df
    
    def create_documents(self) -> List[Document]:
        """
        Convert the preprocessed dataframe to Langchain documents
        """
        if self.processed_df is None:
            self.preprocess_data()
        
        # Use DataFrameLoader to create documents
        loader = DataFrameLoader(
            self.processed_df, 
            page_content_column="combined_text"
        )
        
        self.documents = loader.load()
        
        # Add metadata
        for i, doc in enumerate(self.documents):
            row = self.processed_df.iloc[i]
            doc.metadata.update({
                'job_id': str(row['job_id']),
                'job_title': row['job_title'],
                'company_name': row['company_name'],
                'location': row['location'],
                'job_type': row['job_type'],
                'remote_option': row['remote_option'],
                'document_type': 'job_listing'
            })
        
        print(f"Created {len(self.documents)} documents from job listings")
        return self.documents
    
    def create_vector_store(self, embedding_model=None) -> Chroma:
        """
        Create a vector store from the documents
        """
        if not self.documents:
            self.create_documents()
        
        # Set up text splitter for chunking
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        
        # Split documents into chunks
        split_docs = splitter.split_documents(self.documents)
        
        # Set up embedding model (default to OpenAI if none provided)
        if embedding_model is None:
            api_key = os.environ.get("OPENAI_API_KEY", "your-openai-api-key")
            embedding_model = OpenAIEmbeddings(api_key=api_key)
        
        # Create vector store
        self.vectorstore = Chroma.from_documents(
            documents=split_docs,
            embedding=embedding_model,
            persist_directory="./chroma_db"
        )
        
        print(f"Vector store created with {len(split_docs)} chunks")
        return self.vectorstore
    
    def search_jobs(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for jobs based on the query
        """
        if self.vectorstore is None:
            self.create_vector_store()
        
        # Search the vector store
        results = self.vectorstore.similarity_search_with_relevance_scores(query, k=top_k)
        
        # Format the results
        formatted_results = []
        for doc, score in results:
            formatted_results.append({
                'job_title': doc.metadata.get('job_title', 'Unknown'),
                'company_name': doc.metadata.get('company_name', 'Unknown'),
                'location': doc.metadata.get('location', 'Unknown'),
                'job_type': doc.metadata.get('job_type', 'Unknown'),
                'remote_option': doc.metadata.get('remote_option', 'Unknown'),
                'relevance_score': score,
                'content': doc.page_content
            })
        
        return formatted_results