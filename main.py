import os
from  RAGSystem import RAGSystem
from  GradioDefine import  GradioInterface
# 初始化RAG系统

# 检查是否已有索引，没有则构建
if not os.path.exists("text_search_index.faiss"):
    print("未找到现有索引")
    print("请运行FaissIndexBuild.py构建索引")


rag_system = RAGSystem()

# 加载索引
rag_system.load_index()

# 启动界面
GradioInterface(rag_system).launch()