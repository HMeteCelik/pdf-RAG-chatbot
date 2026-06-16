import gradio as gr
from config import dprint
from vector_db import convert_pdfs_docling, split_document, reset_vector_store
import vector_db
from graph.graph import app as rag_app
import shutil, uuid
from pathlib import Path

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


def upload_and_index(file):
    if file is None:
        return (
            "Lütfen önce bir belge yükleyin.\n"
            "Please upload a document first."
        )

    suffix = Path(file.name).suffix.lower()
    file_id = str(uuid.uuid4())
    dest = UPLOAD_DIR / f"{file_id}{suffix}"
    shutil.copy(file.name, dest)

    if suffix in [".pdf", ".png", ".jpg", ".jpeg"]:
        reset_vector_store()
        md_content = convert_pdfs_docling(str(dest))
        dprint(md_content)
        docs = split_document(md_content)
        vector_db.vector_store.add_documents(docs)
        dest.unlink(missing_ok=True)
        return (
            "Belge başarıyla işlendi ve sorguya hazır.\n"
            "Document processed and ready for queries."
        )
    else:
        return (
            "Desteklenmeyen dosya formatı. Lütfen şu formatlardan birini kullanın: .pdf, .png, .jpg, .jpeg\n"
            "Unsupported file format. Please use one of the following: .pdf, .png, .jpg, .jpeg"
        )


def ask_question(message, history):
    if not message.strip():
        return "", history

    chat_history = []
    user_msg = None
    for h in history:
        if h["role"] == "user":
            user_msg = h["content"]
        elif h["role"] == "assistant" and user_msg is not None:
            chat_history.append((user_msg, h["content"]))
            user_msg = None

    dprint(f"Question: {message}")
    dprint(f"Chat history length: {len(chat_history)}")

    result = rag_app.invoke(input={
        "question": message,
        "chat_history": chat_history,
    })

    answer = result.get(
        "generation",
        "Yüklenen belgede bu soruya ilişkin bir bilgi bulunamadı.\n"
        "No relevant information found in the uploaded document."
    )

    history.append({"role": "user", "content": message})
    history.append({"role": "assistant", "content": answer})

    return "", history


with gr.Blocks(title="Belge Soru-Cevap Sistemi") as demo:
    gr.Markdown("# Belge Soru-Cevap Sistemi / Document Q&A")

    with gr.Row():
        with gr.Column(scale=1):
            file_input = gr.File(
                label="Belge Yükle — PDF veya Görsel / Upload Document — PDF or Image",
                file_types=[".pdf", ".png", ".jpg", ".jpeg"],
            )
            upload_btn = gr.Button("Yükle / Upload", variant="primary")
            upload_status = gr.Textbox(label="Durum / Status", interactive=False)

        with gr.Column(scale=2):
            chatbot = gr.Chatbot(
                label="Konuşma / Chat",
                height=450,
            )
            with gr.Row():
                question_input = gr.Textbox(
                    label="Soru / Question",
                    placeholder="Belge hakkında bir soru sorun... / Ask a question about the document...",
                    scale=4,
                )
                ask_btn = gr.Button("Gönder / Send", variant="primary", scale=1)

    upload_btn.click(fn=upload_and_index, inputs=file_input, outputs=upload_status)

    ask_btn.click(
        fn=ask_question,
        inputs=[question_input, chatbot],
        outputs=[question_input, chatbot],
    )
    question_input.submit(
        fn=ask_question,
        inputs=[question_input, chatbot],
        outputs=[question_input, chatbot],
    )


if __name__ == "__main__":
    demo.launch()