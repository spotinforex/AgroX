import os
import faiss
import chardet
import logging
import pickle
from sentence_transformers import SentenceTransformer

logging.basicConfig(level=logging.INFO)

class FAISSGenerator:
    ''' Class for FAISS building '''
    
    def load_document(self, folder_path):
        ''' Function for loading documents for embeddings
        Args:
            folder_path: folder path to the documents
        Returns:
            documents in a list '''
        try:
            logging.info("Document Ingestion In Progress")
            docs = []
            for filename in os.listdir(folder_path):
                if filename.endswith('.txt'):
                    file_path = os.path.join(folder_path, filename)
                    with open(file_path, 'rb') as f:
                        raw_data = f.read()
                        encoding = chardet.detect(raw_data)['encoding'] or 'utf-8'
                    with open(file_path, 'r', encoding=encoding, errors='replace') as f:
                        content = f.read()
                        docs.append(content)
            logging.info("Document Ingestion Completed")
            return docs

        except Exception as e:
            logging.exception(f"An Error Occurred During Data Ingestion: {e}")
            raise e

    def build_faiss_index(self):
        ''' Function to build a FAISS index and save it '''
        try:
            raw_docs = self.load_document(r'C:\Users\SPOT\Documents\AgroX\data')
            logging.info("Building FAISS in Progress")

            # Load local model (must have been downloaded beforehand)
            model = SentenceTransformer(r'C:\Users\SPOT\Documents\AgroX\models\models--sentence-transformers--all-MiniLM-L6-v2')
            embeddings = model.encode(raw_docs, convert_to_numpy=True, show_progress_bar=True)

            dim = embeddings.shape[1]
            index = faiss.IndexFlatL2(dim)
            index.add(embeddings)

            # Save FAISS index
            faiss.write_index(index, r'C:\Users\SPOT\Documents\AgroX\index\faiss_index.index')

            # Save raw_docs for retrieval
            with open(r'C:\Users\SPOT\Documents\AgroX\index\documents.pkl', 'wb') as f:
                pickle.dump(raw_docs, f)

            logging.info("FAISS Saved Successfully")

        except Exception as e:
            logging.exception(f"An Error Occurred During FAISS Building: {e}")
            raise e


if __name__ == "__main__":
    faiss_gen = FAISSGenerator()
    faiss_gen.build_faiss_index()
