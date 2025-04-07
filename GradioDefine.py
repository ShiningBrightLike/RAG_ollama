import gradio as gr

# ========== Gradio界面 ==========
def format_results(results):
    """格式化检索结果"""
    if not results:
        return "未检索到相关内容"
    return "\n".join(
        f"【结果 {i}】\n📝 内容: {res['text']}\n📂 来源: {res['source_file']}\n📏 相似度: {res['distance']:.4f}\n"
        for i, res in enumerate(results, 1)
    )


class GradioInterface:
    def __init__(self, rag_system):
        self.rag_system = rag_system
        self.chat_history = []

    def respond(self, query, use_rag, stream, k, model_name):
        """处理用户查询并响应"""
        full_response = ""
        for partial_resp, similar_texts in self.rag_system.generate_response(
                query, k, stream, use_rag, model_name
        ):
            full_response = partial_resp
            yield [
                      (q, a) for q, a in self.chat_history
                  ] + [(query, full_response)], format_results(similar_texts)

        self.chat_history.append((query, full_response))

    def clear_chat(self):
        """清空聊天历史"""
        self.chat_history = []
        return [], ""

    def launch(self):
        """启动Gradio界面"""
        with gr.Blocks(theme=gr.themes.Soft(), title="RAG问答系统") as demo:
            gr.Markdown("## 🧠 RAG问答系统(刘磊课题组)")

            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("### ⚙️ 参数设置")
                    model_dropdown = gr.Dropdown(
                        label="选择大模型",
                        choices=["deepseek-r1:7b", "llama3", "mistral", "qwen:7b"],
                        value="deepseek-r1:7b"
                    )
                    k_slider = gr.Slider(1, 5, value=3, step=1, label="检索数量(k)")
                    use_rag = gr.Checkbox(label="使用RAG", value=True)
                    stream = gr.Checkbox(label="流式输出", value=False)
                    clear_btn = gr.Button("🧹 清空对话")

                with gr.Column(scale=3):
                    chatbot = gr.Chatbot(height=400, bubble_full_width=False)
                    query_input = gr.Textbox(placeholder="输入问题...", lines=3)
                    submit_btn = gr.Button("🚀 提交", variant="primary")

                    with gr.Accordion("🔍 检索结果", open=False):
                        retrieval_output = gr.Textbox(label="", lines=5, interactive=False)

            submit_btn.click(
                self.respond,
                [query_input, use_rag, stream, k_slider, model_dropdown],
                [chatbot, retrieval_output]
            ).then(
                lambda: "", None, query_input
            )

            query_input.submit(
                self.respond,
                [query_input, use_rag, stream, k_slider, model_dropdown],
                [chatbot, retrieval_output]
            ).then(
                lambda: "", None, query_input
            )

            clear_btn.click(
                self.clear_chat,
                outputs=[chatbot, retrieval_output]
            )

        demo.launch(share=True)
