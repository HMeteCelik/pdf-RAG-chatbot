from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions, TesseractOcrOptions, AcceleratorOptions, AcceleratorDevice
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter, MarkdownHeaderTextSplitter
from langchain_core.documents import Document
from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend
from llm import embeddings
import re

CHROMA_DIR = "./.chroma"

TABLE_WITH_CAPTION_RE = re.compile(
    r'((?:^(?!\s*#)(?!\s*\|).+\n)?'
    r'(?:\|.+\|\n)+'
    r'\|[-| :]+\|\n'
    r'(?:\|.+\|\n)*)',
    re.MULTILINE,
)


def extract_tables_and_text(md: str):
    """Extracts tables"""
    tables = []
    for match in TABLE_WITH_CAPTION_RE.finditer(md):
        tables.append(match.group(0).strip())

    remaining_text = TABLE_WITH_CAPTION_RE.sub("\n\n", md)
    remaining_text = re.sub(r"\n{3,}", "\n\n", remaining_text).strip()

    return remaining_text, tables


def compact_table(table_text: str) -> str:
    """ Removes extra spaces to avoid token exceding"""
    lines = table_text.split("\n")
    compacted = []
    for line in lines:
        if line.startswith("|"):
            cells = [cell.strip() for cell in line.split("|")]
            compacted.append("|".join(cells))
        else:
            compacted.append(line)
    return "\n".join(compacted)


def clean_docling_markdown(md: str) -> str:
    """ Removes placeholders """
    md = re.sub(r"<!--\s*image.*?-->", "", md)
    md = re.sub(r"<!--\s*formula.*?-->", "", md)
    md = re.sub(r"\n{3,}", "\n\n", md)
    return md.strip()


def convert_pdfs_docling(pdf_file: str):
    """PDF and Image to markdown"""
    if pdf_file.endswith(".pdf"):
        pipeline_options = PdfPipelineOptions(
            do_table_structure=True,
            do_ocr=True,
            images_scale=2.5,
            generate_picture_images=True,
            accelerator_options=AcceleratorOptions(
                num_threads=4,
                device=AcceleratorDevice.AUTO,
            ),
        )
    else:
        ocr_options = TesseractOcrOptions(
            lang=["tur", "eng"],
        )

        pipeline_options = PdfPipelineOptions(
            do_table_structure=True,
            do_ocr=True,
            images_scale=2.5,
            generate_picture_images=True,
            ocr_options=ocr_options,
            accelerator_options=AcceleratorOptions(
                num_threads=4,
                device=AcceleratorDevice.AUTO,
            ),
        )

    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(
                pipeline_options=pipeline_options,
                backend=PyPdfiumDocumentBackend
            )
        }
    )
    result = converter.convert(str(pdf_file))
    markdown_content = result.document.export_to_markdown()
    md_cleaned = clean_docling_markdown(markdown_content)
    return md_cleaned


def split_document(md_content: str):
    """Processes markdowns and tables seperatly"""
    remaining_text, tables = extract_tables_and_text(md_content)

    text_docs = markdown_splitter.split_text(remaining_text)
    text_docs = text_splitter.split_documents(text_docs)

    table_docs = []
    for i, table_text in enumerate(tables):
        table_docs.append(Document(
            page_content=compact_table(table_text),
            metadata={"type": "table", "table_index": i},
        ))

    return text_docs + table_docs


headers_to_split_on = [
    ("#", "Header 1"),
    ("##", "Header 2"),
]

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=100,
    separators=["\n\n", "\n", " ", ""],
)
markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)

vector_store = Chroma(
    collection_name="vectors",
    embedding_function=embeddings,
    persist_directory=CHROMA_DIR
)

retriever = vector_store.as_retriever(
    search_type="mmr",
    search_kwargs={
        "k": 5,
        "fetch_k": 20,
        "lambda_mult": 0.7
    }
)


def reset_vector_store():
    global vector_store, retriever

    vector_store.delete_collection()

    vector_store = Chroma(
        collection_name="vectors",
        embedding_function=embeddings,
        persist_directory=CHROMA_DIR
    )
    retriever = vector_store.as_retriever(
        search_type="mmr",
        search_kwargs={
            "k": 5,
            "fetch_k": 20,
            "lambda_mult": 0.7
        }
    )