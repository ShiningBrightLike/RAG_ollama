# RAG_ollama
基于大语言模型的本地知识库问答系统，多文件模块化实现的RAG系统，支持文档检索与生成式问答，保留文本来源信息。

## 项目结构

```
rag-system/
├── main.py                 # 主程序入口
├── RAGSystem.py            # RAG核心逻辑
├── FaissIndexBuild.py      # 索引构建模块
├── GradioDefine.py         # 交互界面实现
├── 本地知识库/              # 默认文档存储目录
│   ├── *.pdf/.txt/.docx    # 支持多种文档格式
├── requirements.txt        # 依赖列表
└── config.json             # 配置文件(可选)
```

## 快速开始

### 1. 环境配置

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 准备知识库

将您的文档放入`本地知识库`文件夹，支持格式：
- PDF (.pdf)
- Word (.docx)
- 纯文本 (.txt)
- Markdown (.md)

### 3. 运行系统

```bash
# 首次运行会自动构建索引
python main.py

# 指定自定义知识库路径
python main.py --data_path ./my_documents
```

## 模块说明

### 1. FaissIndexBuild.py

- **功能**：文档处理与向量索引构建
- **核心方法**：
  ```python
  build_index(documents, index_path="index.faiss")
  # 构建FAISS索引并保存元数据
  
  load_index(index_path="index.faiss", metadata_path="metadata.json")
  # 加载已有索引
  ```

### 2. RAGSystem.py

- **核心类**：
  ```python
  class RAGSystem:
      def search(query: str, k=3) -> List[Dict]
      # 检索相似文本（返回包含来源的字典）
      
      def generate_response(query: str, stream=False) -> Generator
      # 生成带来源引用的回答
  ```

### 3. GradioDefine.py

- **界面特性**：
  - 实时流式输出
  - 检索结果显示来源文件
  - 支持多模型切换
  - 对话历史管理

![界面截图](assets/ui_screenshot.png)

## 高级配置

通过`config.json`自定义设置：

```json
{
  "embedding_model": "BAAI/bge-m3",
  "llm_options": ["deepseek-r1:7b", "llama3"],
  "chunk_size": 300,
  "chunk_overlap": 30
}
```

## 常见问题

### Q1: 如何更换大模型？
1. 确保已通过Ollama下载模型：
   ```bash
   ollama pull llama3
   ```
2. 在Gradio界面下拉菜单选择

### Q2: 索引未更新怎么办？
删除以下文件后重启程序：
```bash
rm text_search_index.faiss index_metadata.json
```

### Q3: 如何添加新文档？
1. 将文件放入知识库目录
2. 删除现有索引文件
3. 重新启动程序
