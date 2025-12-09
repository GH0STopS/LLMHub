import os
import json
from langchain_community.llms.ollama import Ollama
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from operator import itemgetter
# from langchain. import 


class CodeAssistantBot:
    def __init__(self, persist_dir : str = "./code_vectordb"):
        self.persist_dir = persist_dir
        self._setup()

    def _setup(self):
        self.model = Ollama(
            model = "mistral:latest",
            temperature = 0.2,
        )

        self.embeddings = OllamaEmbeddings(
            model="all-minilm:latest"
        )

        self.vectordb = Chroma(
            persist_directory=self.persist_dir,
            embedding_function=self.embeddings
        )

        self.retriever = self.vectordb.as_retriever(search_kwargs={'k':6})

        metadata_file = os.path.join(self.persist_dir, 'code_metadata.json')
        if os.path.exists(metadata_file):
            with open(metadata_file, 'r') as f:
                self.code_metadata = json.load(f)
        else:
            self.code_metadata = []
        
        self.prompt = ChatPromptTemplate.from_template("""
You are a code analysis expert. Analyze the provided code context carefully.

Code Context:
{context}

User Query: {question}

Instructions:
- Be precise and factual
- Reference specific line numbers when possible
- If information is not in the context, say so
- For lists, provide complete items from the code
- Explain relationships between components

Analysis:
""")
        
        def format_docs(docs):
            return "\n\n".join([f"=== Chunk {i+1} ===\n{doc.page_content}" 
                              for i, doc in enumerate(docs)])
        
        self.chain = (
            {
                'context': self.retriever | format_docs,
                'question': itemgetter('question')
            }
            | self.prompt
            | self.model
            | StrOutputParser()
        )

    def analyze(self, query : str) -> str:
        return self.chain.invoke({'question':query})
    
    def get_file_metadata(self):
        return self.code_metadata
    
    def list_functions(self):
        all_func = []
        for data in self.code_metadata:
            for func in data['functions']:
                all_func.append({
                    'file':data['file_name'],
                    'function': func['name'],
                    'args': func['args'],
                    'line':func['line']
                })
        return all_func

    def list_classes(self):
        all_classes = []
        for data in self.code_metadata:
            for c in data['classes']:
                all_classes.append({
                    'file':data['file_name'],
                    'class':c['name'],
                    'functions':c['methods'],
                    'line':c['line']
                })
        return all_classes
    
    def list_imports(self):
        all_imports = []
        for data in self.code_metadata:
            # for c in data['imports']:
            #     all_imports.append({
            #         'file':data['file_name'],
            #         'imports':c
            #     })
            all_imports.append(data['imports'])
        return all_imports
    
    def auth_flow(self):
        query = """
Analyze the authentication flow in this codebase:
1. List all authentication-related functions and classes
2. Describe the login process step by step
3. Identify token/session management
4. Note any security patterns used
"""
        return self.analyze(query)

    def code_smells(self):
        query = """
Analyze the code for potential issues:
1. Long functions (>50 lines)
2. Classes with too many methods
3. Duplicate code patterns
4. Missing error handling
5. Hard-coded values
6. Complex conditional logic
"""
        return self.analyze(query)
        