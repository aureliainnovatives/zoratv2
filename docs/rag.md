# Retrieval-Augmented Generation (RAG) System

## **Objective**
To build a scalable, enterprise-grade Retrieval-Augmented Generation (RAG) system capable of handling large document datasets, integrating with external systems like SAP and databases, and performing semantic queries across multiple data sources. This system will prioritize compliance, modularity, and extensibility.

---

## **Tech Stack**

### **Core Components**
1. **Haystack**: Backend for document processing, indexing, and hybrid search.
2. **LangChain**: Orchestrates workflows, builds agents, and integrates with external systems.
3. **Docling**: Preprocesses and parses diverse document formats (PDF, DOCX, etc.) with OCR support.
4. **Embedding Model**: 
   - Default: `sentence-transformers/all-MiniLM-L6-v2`
   - Open to integrating domain-specific or custom embeddings for enhanced performance.
5. **Vector Database Options** (Configurable):
   - **ElasticSearch**: For hybrid search (dense + sparse retrieval).
   - **Milvus**: For large-scale, optimized vector similarity search.
6. **FastAPI**: Exposes REST APIs for integration with other systems.
7. **Python 3.10+**: Primary development language.

### **Optional Components**
1. **Redis**: For caching frequently accessed queries.
2. **Neo4j**: For graph-based retrieval (future enhancement).

---

## **Approach**

### **1. Document Workflow**
1. **Upload**:
   - Documents are uploaded and parsed using **Docling**.
   - Supported formats: PDF, DOCX, XLSX, images, etc.
2. **Parsing & Preprocessing**:
   - Documents are split into manageable chunks.
   - Text and metadata are extracted and prepared for embedding.
3. **Embedding & Indexing**:
   - Embeddings are generated using a pre-trained model.
   - Both embeddings and metadata are stored in the selected vector database (ElasticSearch or Milvus).
4. **Retrieval**:
   - Queries are matched to embeddings for semantic search.
   - Relevant results are fetched and returned, optionally including decrypted content if needed.

### **2. Configurable Search Engine**
The system supports two configurable search engines:
1. **ElasticSearch**: Combines full-text search and vector-based semantic search. Best for hybrid queries and metadata-rich retrieval.
2. **Milvus**: Optimized for pure vector search at scale, ideal for embedding-centric AI-powered queries.

### **3. Query Handling**
- User queries are processed using **LangChain** agents.
- The system supports multi-source querying (documents, databases, APIs).
- Results are contextualized with metadata and/or raw text when required.

### **4. Compliance**
- Parsed text is deleted post-embedding unless encryption is enabled.
- Metadata stored is minimal, ensuring compliance with confidentiality policies.
- Embeddings are non-decodable, providing an additional layer of security.

---

## **Installation**

### **1. Prerequisites**
- Python 3.10+
- Docker and Docker Compose (optional, for deploying dependencies).
- Git

### **2. Clone the Repository**
```bash
git clone <repository-url>
cd <repository-folder>
```

### **3. Create a Virtual Environment**
#### macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```
#### Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

### **4. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **5. Set Up Vector Database**
#### Option 1: ElasticSearch
- Install ElasticSearch via Docker:
```bash
docker pull docker.elastic.co/elasticsearch/elasticsearch:7.17.8
docker run -d -p 9200:9200 -e "discovery.type=single-node" elasticsearch:7.17.8
```
- Configure ElasticSearch endpoint in the project settings.

#### Option 2: Milvus
- Install Milvus via Docker:
```bash
docker pull milvusdb/milvus:latest
docker run -d -p 19530:19530 milvusdb/milvus:latest
```
- Configure Milvus endpoint in the project settings.

### **6. Set Up the Project**
- Update environment variables in `.env` file (e.g., vector DB endpoints, embedding model paths).
- Initialize the vector database:
```bash
python scripts/init_vector_db.py
```

### **7. Run the Application**
```bash
uvicorn app.main:app --reload
```
- The API will be available at `http://127.0.0.1:8000`.

---

## **API Endpoints**

### **1. Document Upload**
**POST** `/documents/upload`
- Accepts: File upload (PDF, DOCX, etc.).
- Response: Document ID(s).

### **2. Query Documents**
**POST** `/query`
- Accepts: Query text.
- Response: Relevant document excerpts with metadata.

### **3. Metadata Search**
**GET** `/documents/search`
- Accepts: Metadata filters (e.g., document type, author).
- Response: List of matching documents.

---

## **Future Enhancements**
1. **Neo4j Integration**: To enable graph-based querying for relationship-heavy data.
2. **Advanced Analytics**: Adding user behavior insights and query performance metrics.
3. **Multi-modal Search**: Support for image and audio embeddings alongside text.
4. **RBAC (Role-Based Access Control)**: For secure enterprise deployments.

---

## **Development Notes**
1. Follow modular development practices to keep document processing, retrieval, and agent workflows loosely coupled.
2. Ensure unit tests are written for all major components.
3. Use Docker Compose to simplify multi-component deployment.
4. Regularly update embedding models to maintain retrieval accuracy.

---

## **References**
- [Haystack Documentation](https://haystack.deepset.ai/)
- [LangChain Documentation](https://langchain.readthedocs.io/)
- [ElasticSearch Setup Guide](https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html)
- [Milvus Documentation](https://milvus.io/docs/)
