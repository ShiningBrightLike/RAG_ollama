import os
import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from langchain.document_loaders import UnstructuredFileLoader
from langchain.text_splitter import CharacterTextSplitter

# ========== 1. 文件加载与处理 ==========
def load_text_from_files(file_paths):
    """加载文件并保留来源信息"""
    all_docs = []
    for file_path in file_paths:
        try:
            loader = UnstructuredFileLoader(file_path)
            documents = loader.load()
            for doc in documents:
                doc.metadata['source_file'] = file_path
            all_docs.extend(documents)
        except Exception as e:
            print(f"无法加载文件 {file_path}，错误: {e}")
    return all_docs


def get_all_files_in_folder(folder_path):
    """递归获取文件夹中的所有文件"""
    file_paths = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_paths.append(os.path.join(root, file))
    return file_paths


def split_documents(documents, chunk_size=300, chunk_overlap=30):
    """文本分割并保留来源信息"""
    splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        is_separator_regex=False
    )

    split_docs = []
    for doc in documents:
        chunks = splitter.split_text(doc.page_content)
        for chunk in chunks:
            new_doc = {
                "text": chunk,
                "metadata": doc.metadata.copy()
            }
            split_docs.append(new_doc)
    return split_docs


# ========== 2. 构建FAISS索引 ==========
def build_faiss_index(docs, index_path="text_search_index.faiss", metadata_path="index_metadata.json"):
    """构建FAISS索引并保存元数据"""
    model = SentenceTransformer("BAAI/bge-m3")

    # 提取纯文本用于嵌入
    texts = [doc["text"] for doc in docs]
    embeddings = model.encode(texts)
    embeddings = np.array(embeddings, dtype='float32')

    # 创建索引映射
    index_to_metadata = {
        i: {
            "text": docs[i]["text"],
            "metadata": docs[i]["metadata"]
        }
        for i in range(len(docs))
    }

    # 构建FAISS索引
    d = embeddings.shape[1]
    index = faiss.IndexFlatL2(d)
    faiss.normalize_L2(embeddings)
    index.add(embeddings)

    # 保存索引和元数据
    faiss.write_index(index, index_path)
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(index_to_metadata, f, ensure_ascii=False, indent=4)

    print(f"索引构建完成，共 {index.ntotal} 条文本")


if not os.path.exists("text_search_index.faiss"):
    print("未找到现有索引，开始构建...")
    folder_path = "本地知识库"
    file_paths = get_all_files_in_folder(folder_path) if os.path.isdir(folder_path) else [folder_path]
    documents = load_text_from_files(file_paths)
    split_docs = split_documents(documents)
    build_faiss_index(split_docs)