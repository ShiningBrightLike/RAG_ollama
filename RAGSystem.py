import json
import faiss
import ollama
from sentence_transformers import SentenceTransformer

# ========== 3. 查询与RAG功能 ==========
class RAGSystem:
    def __init__(self):
        self.model = SentenceTransformer("BAAI/bge-m3")
        self.index = None
        self.index_metadata = None

    def load_index(self, index_path="text_search_index.faiss", metadata_path="index_metadata.json"):
        """加载预构建的索引"""
        self.index = faiss.read_index(index_path)
        with open(metadata_path, "r", encoding="utf-8") as f:
            self.index_metadata = json.load(f)
        print("索引加载完成")

    def search_similar_text(self, query_text, k=3):
        """查询相似文本（带来源信息）"""
        query_embedding = self.model.encode([query_text]).astype('float32')
        faiss.normalize_L2(query_embedding)

        distances, indices = self.index.search(query_embedding, k)

        results = []
        for idx, distance in zip(indices[0], distances[0]):
            metadata = self.index_metadata.get(str(idx))
            if metadata:
                results.append({
                    "text": metadata["text"],
                    "source_file": metadata["metadata"]["source_file"],
                    "distance": float(distance)
                })
        return results

    def generate_response(self, query, k=3, stream=False, use_rag=True, model_name="deepseek-r1:7b"):
        """生成RAG回复"""
        if use_rag:
            similar_texts = self.search_similar_text(query, k)
            retrieved_text = "\n".join(
                [f"内容: {res['text']}\n来源: {res['source_file']}"
                 for res in similar_texts]
            )
            messages = [
                {"role": "system", "content": f"基于以下信息回答问题：\n{retrieved_text}"},
                {"role": "user", "content": query}
            ]
        else:
            similar_texts = []
            messages = [{"role": "user", "content": query}]

        response = ollama.chat(
            model=model_name,
            messages=messages,
            stream=stream,
            options={"max_tokens": 500}
        )

        if stream:
            full_response = ""
            for chunk in response:
                if "message" in chunk and "content" in chunk["message"]:
                    full_response += chunk["message"]["content"]
                    yield full_response, similar_texts
        else:
            yield response["message"]["content"], similar_texts