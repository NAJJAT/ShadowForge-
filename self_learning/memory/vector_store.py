"""
Vector Store - تخزين المتجهات للبحث بالتشابه
يستخدم ChromaDB أو FAISS للتخزين الفعال
"""

import json
import hashlib
import logging
from typing import List, Dict, Optional, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# محاولة استيراد ChromaDB (اختياري)
try:
    import chromadb
    from chromadb.utils import embedding_functions
    HAS_CHROMADB = True
except ImportError:
    HAS_CHROMADB = False
    logger.warning("ChromaDB not installed. Using simple in-memory store.")


@dataclass
class VectorDocument:
    """وثيقة مخزنة مع متجهها"""
    id: str
    content: str
    metadata: Dict
    vector: Optional[List[float]] = None


class SimpleVectorStore:
    """تخزين متجهات بسيط (في الذاكرة) - يصلح للمحاكاة"""
    
    def __init__(self):
        self.documents: List[VectorDocument] = []
        logger.info("SimpleVectorStore initialized (in-memory)")
    
    def add(self, content: str, metadata: Dict, vector: List[float]) -> str:
        doc_id = hashlib.md5(f"{content}{metadata}".encode()).hexdigest()[:12]
        doc = VectorDocument(id=doc_id, content=content, metadata=metadata, vector=vector)
        self.documents.append(doc)
        return doc_id
    
    def search(self, query_vector: List[float], k: int = 10) -> List[Dict]:
        """بحث بالتشابه (أقل مسافة إقليدية)"""
        if not self.documents:
            return []
        
        results = []
        for doc in self.documents:
            if doc.vector is None:
                continue
            # حساب المسافة الإقليدية
            distance = sum((a - b) ** 2 for a, b in zip(query_vector, doc.vector)) ** 0.5
            results.append((distance, doc))
        
        results.sort(key=lambda x: x[0])
        return [
            {
                "id": doc.id,
                "content": doc.content,
                "metadata": doc.metadata,
                "distance": dist,
            }
            for dist, doc in results[:k]
        ]
    
    def count(self) -> int:
        return len(self.documents)


class ChromaVectorStore:
    """تخزين متجهات باستخدام ChromaDB (أكثر كفاءة)"""
    
    def __init__(self, collection_name: str = "experiences", persist_directory: str = "./chroma_db"):
        if not HAS_CHROMADB:
            raise ImportError("ChromaDB not installed. Install with: pip install chromadb")
        
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.embedding_fn = embedding_functions.DefaultEmbeddingFunction()
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_fn
        )
        logger.info(f"ChromaVectorStore initialized with collection '{collection_name}'")
    
    def add(self, content: str, metadata: Dict, vector: List[float] = None) -> str:
        doc_id = hashlib.md5(f"{content}{metadata}".encode()).hexdigest()[:12]
        self.collection.add(
            ids=[doc_id],
            documents=[content],
            metadatas=[metadata],
        )
        return doc_id
    
    def search(self, query: str, k: int = 10) -> List[Dict]:
        results = self.collection.query(query_texts=[query], n_results=k)
        return [
            {
                "id": results['ids'][0][i],
                "content": results['documents'][0][i],
                "metadata": results['metadatas'][0][i],
                "distance": results['distances'][0][i] if results['distances'] else 0,
            }
            for i in range(len(results['ids'][0]))
        ]
    
    def count(self) -> int:
        return self.collection.count()


class VectorStore:
    """واجهة موحدة للتخزين المتجهي (تختار تلقائياً الأفضل)"""
    
    def __init__(self, use_chromadb: bool = False, simulation_mode: bool = True):
        self.simulation_mode = simulation_mode
        self.use_chromadb = use_chromadb and HAS_CHROMADB and not simulation_mode
        
        if self.use_chromadb:
            self.store = ChromaVectorStore()
        else:
            self.store = SimpleVectorStore()
        
        logger.info(f"VectorStore initialized (using {type(self.store).__name__})")
    
    def add(self, content: str, metadata: Dict = None) -> str:
        """إضافة وثيقة للتخزين"""
        return self.store.add(content, metadata or {}, None)
    
    def search(self, query: str, k: int = 10) -> List[Dict]:
        """بحث عن وثائق مشابهة"""
        return self.store.search(query, k)
    
    def count(self) -> int:
        return self.store.count()


# مثال
if __name__ == "__main__":
    store = VectorStore(use_chromadb=False, simulation_mode=True)
    
    # إضافة تجارب
    store.add("SQL injection worked on login page with error-based technique", 
              {"type": "success", "technique": "sql_injection"})
    store.add("XSS failed due to CSP, need to try DOM-based XSS",
              {"type": "failure", "technique": "xss"})
    store.add("Used process hollowing to bypass EDR on Windows 10",
              {"type": "success", "technique": "edr_bypass"})
    
    # بحث
    results = store.search("bypass EDR", k=2)
    print("Search results:")
    for r in results:
        print(f"  - {r['content'][:50]}... (distance: {r['distance']:.2f})")