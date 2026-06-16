# pdf-RAG

![graph](graph.png)

**pdf-RAG**, PDF ve görsel dosyalarınızı yerel olarak sorgulayabileceğiniz, tamamen çevrimdışı çalışan bir **chatbot** uygulaması. 

**Self-Corrective RAG** mimarisi çalışır. Her yanıt, oluşturulmadan önce kaynaklar kontrol edilir ve gerektiğinde yeniden sorgulanır. Bu sayede halüsinasyon riski en aza indirilir.

Arayüz **Gradio** ile sunulur; tarayıcı üzerinden çalışan bir sohbet ekranı açılır. Sol panelde PDF veya görsel yüklenirken sağ panelde belgeye yönelik sorular sorulabilir. Konuşma geçmişi de bağlam olarak modele iletilir, böylece art arda soru sorulabilir.

## Özellikler

- PDF ve görsel dosyalardan (`.pdf`, `.png`, `.jpg`, `.jpeg`) metin çıkarımı
- Gradio tabanlı chatbot arayüzü — tarayıcıda çalışır, kurulum gerektirmez
- Self-Corrective RAG ile halüsinasyona karşı otomatik doğrulama
- Vektör tabanlı anlamsal arama ve yerel embedding
- Tamamen yerel çalışır — hiçbir veri dışarı gitmez
- `llm.py` üzerinden farklı Ollama modelleri kolayca değiştirilebilir

## Sistem Mimarisi

- `main.py` — Gradio arayüzünü başlatır; dosya yükleme ve sohbet akışını yönetir
- `vector_db.py` — Belge dönüştürme, bölme ve vektör depolama işlemlerini üstlenir
- `graph/` — Self-Corrective RAG zincirinin düğüm ve akış mantığını barındırır
- `uploads/` — Yüklenen dosyaların geçici olarak tutulduğu klasördür

## LLM Seçimi ve Ayarlar

`llm.py` içindeki `model` parametresini değiştirerek istediğiniz yerel Ollama modelini kullanabilirsiniz. Varsayılan model `qwen3:4b-instruct-2507-q4_K_M`'dir. Embedding için `bge-m3:567m` kullanılmaktadır.

## Debug ve Hata Takibi

`config.py` içinde `DEBUG = True` iken `dprint()` fonksiyonu ayrıntılı debug mesajları terminale yazar.

## Kurulum

### 1. Repoyu Klonlayın

```bash
https://github.com/HMeteCelik/pdf-RAG-chatbot
cd pdf-RAG-chatbot
```

### 2. Python Ortamı Oluşturun

```bash
python -m venv venv
```

Sanal ortamı etkinleştirin:

```bash
# Windows
.\venv\Scripts\activate

# Linux / macOS
source venv/bin/activate
```

### 3. Bağımlılıkları Yükleyin

```bash
pip install -r requirements.txt
```

---

## Ollama Kurulumu

### İndirme

Ollama'yı resmi sitesinden indirin:
[https://ollama.com/download](https://ollama.com/download)

### Modelleri İndirin

```bash
ollama run qwen3:4b-instruct-2507-q4_K_M
ollama pull bge-m3:567m
```

---

## Çalıştırma

```bash
python main.py
```

---

## 🛠 Gereksinimler

- Python 3.11
- [Ollama](https://ollama.com)
- `qwen3:4b-instruct-2507-q4_K_M` modeli
- `bge-m3` embedding modeli
