import sqlite3
from datetime import datetime
from .config import settings

class Database:
    def __init__(self):
        self.db_path = settings.DB_PATH
        self._init_db()
    
    def _init_db(self):
        """Initialize database with proper schema"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Create documents table with all required columns
        c.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                filename TEXT,
                filepath TEXT,
                file_type TEXT,
                is_image BOOLEAN DEFAULT 0,
                processed BOOLEAN DEFAULT 0,
                created_at TIMESTAMP,
                processed_at TIMESTAMP
            )
        ''')
        
        # Create chunks table
        c.execute('''
            CREATE TABLE IF NOT EXISTS document_chunks (
                id TEXT PRIMARY KEY,
                document_id TEXT,
                chunk_index INTEGER,
                chunk_text TEXT,
                embedding_path TEXT,
                FOREIGN KEY (document_id) REFERENCES documents (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        print("Database initialized successfully")
    
    def add_document(self, doc_id, filename, filepath, file_type):
        """Add a new document record"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            INSERT INTO documents (id, filename, filepath, file_type, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (doc_id, filename, filepath, file_type, datetime.now()))
        conn.commit()
        conn.close()
        return doc_id
    
    def update_document_status(self, doc_id, is_processed=True):
        """Update document processing status"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            UPDATE documents 
            SET processed = ?, processed_at = ?
            WHERE id = ?
        ''', (1 if is_processed else 0, datetime.now(), doc_id))
        conn.commit()
        conn.close()
    
    def get_document(self, doc_id):
        """Get document by ID"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT * FROM documents WHERE id = ?', (doc_id,))
        result = c.fetchone()
        conn.close()
        return result
    
    def list_documents(self):
        """List all documents"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            SELECT id, filename, file_type, processed, created_at
            FROM documents
            ORDER BY created_at DESC
        ''')
        documents = c.fetchall()
        conn.close()
        
        return [
            {
                "id": doc[0],
                "filename": doc[1],
                "type": doc[2],
                "processed": bool(doc[3]),
                "created_at": doc[4]
            }
            for doc in documents
        ]
    
    def document_exists_and_processed(self, doc_id):
        """Check if document exists and is processed"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT processed FROM documents WHERE id = ?', (doc_id,))
        result = c.fetchone()
        conn.close()
        
        if not result:
            return False, "Document not found"
        return bool(result[0]), "Document not processed yet" if not result[0] else ""

# Singleton instance
db = Database()