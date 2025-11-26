# Ask-your-Data-Analyst-AI
Ask your Data Analyst AI: Chat With Your Data demonstrates how AI can transform traditional analytics workflows by removing technical barriers and enabling data-driven decisions through simple conversation. It's designed for students, analysts, and anyone who wants quick insights without deep technical knowledge.

# Chat With Your CSV — Your Personal Data Analyst

## 🔍 Demo

![demo](assets/demo_screenshot.png)

Try the Kaggle notebook: [https://www.kaggle.com/](https://www.kaggle.com/code/aiastar/my-data-analysis-project)<aiastar>/<kernel-slug>
Live demo (temporary): [https://unpitying-gala-unirritating.ngrok-free.dev/analyze] — 
---

## 🚀 Quick start

1. Clone the repo:

```bash
git clone https://github.com/your-username/chat-with-your-csv.git
cd chat-with-your-csv
```

2. Install dependencies:

```bash
pip install -r requirements.txt
# or
conda env create -f environment.yml
conda activate chat-with-csv
```

3. Run Streamlit app:

```bash
streamlit run src/app.py
```

4. If you need the original dataset, run:

```bash
bash scripts/download_data.sh
```

---

## 🧾 Files

* `notebooks/chat_with_your_csv.ipynb` — main notebook
* `src/app.py` — Streamlit app (exported)
* `assets/` — screenshots and sample CSV
* `requirements.txt` — Python dependencies

---

## ⚠️ Notes & security

* **Do not** commit API keys, ngrok URLs, or other secrets. Use `.env` and GitHub Secrets.
* Sample CSV included for demo only. For full dataset, follow download instructions.

---

## 🔧 Tech stack

* Kaggle Notebooks, Python, Pandas, Streamlit
* Hugging Face (LLM)
* Ngrok for local tunneling

---

## 📄 License

This project is released under the MIT License. See LICENSE for details.

---

## ✉️ Contact

If you want to try the project or collaborate, feel free to open an issue or contact me at [your-email].

