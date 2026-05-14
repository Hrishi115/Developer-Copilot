# Developer Copilot (Codebase-Aware AI Assistant)

Developer Copilot is an AI-powered assistant that understands **your own codebase** and helps you navigate, explain, and generate code efficiently.

Unlike generic AI tools, this copilot is **context-aware**, meaning it can answer questions like:

- “Explain this function”
- “Where is authentication handled?”
- “Generate a snippet based on this module”

  ---

## Features

-  **Semantic Code Search (RAG-based)**\
  Query your codebase using natural language.

-  **Context-Aware Responses**\
  Answers are generated using your actual project files.

-  **Code Snippet Generation**\
  Automatically generates relevant code snippets for queries.

-  **Multi-file Codebase Support**\
  Works across `.py`, `.js`, `.md`, and more.

-  **GitHub Integration (optional)**\
  Load and analyze repositories directly.

---

## Tech Stack

- **Python**
- **LangChain**
- **Vector DB**: Chroma / FAISS
- **LLM APIs** (OpenAI / Ollama)
- **Embeddings**: OpenAI / HuggingFace / Ollama

---

## 📦 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Hrishi115/developer-copilot.git
cd developer-copilot
```

---

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate   # On Windows: venv\\Scripts\\activate
```

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Get your Github Fine-grained personal access token
Go to: 
Github Profile -> Settings -> Developer Settings -> Personal-Access Tokens -> Fine-grained token -> Generate new

---

### 5. Setup Environment Variables
Create a `.env` file in the root directory:

```env
ACCESS_TOKEN=you_fine_grained_access_token_here
```

---

## ⚙️ Usage

### Run the CLI Tool

After installation, start the Developer Copilot using:

```bash
python orchestrator.py
```

---

### Step 1: Enter Repository

The CLI will prompt you to enter a GitHub repository:

```bash
Enter GitHub repo (username/repo):
```

Example:

```bash
username/project-name
```

The tool will automatically:

- Fetch the repository
- Load and process files
- Create embeddings
- Initialize the vector database

---

### Step 2: Ask Questions

Once setup is complete, you can start querying:

```bash
Ask a question: Where is authentication handled?
```

Other examples:

- Explain this function
- How does the API routing work?
- Generate a function for user login

---

### Step 3: Continuous Interaction

- Keep asking questions in the CLI
- The copilot maintains context of your repository
- Type `exit` or `quit` to stop the program

---

## How It Works

1. **Document Loading**\
   Your codebase is parsed into chunks.

2. **Embedding Creation**\
   Each chunk is converted into vector embeddings.

3. **Semantic Retrieval (RAG)**\
   Relevant chunks are fetched based on your query.

4. **LLM Generation**\
   The model generates answers using retrieved context.

---

## Configuration

You can customize:

- Embedding model
- Chunk size & overlap
- Vector DB (FAISS / Chroma)
- LLM provider

---

## Future Improvements

- Web UI / Dashboard
- VS Code Extension
- Authentication for multi-user access
- Usage tracking & limits (for SaaS)

---

## Contributing

Contributions are welcome!

1. Fork the repo
2. Create a feature branch
3. Commit your changes
4. Open a PR

---

## 📄 License

This project is licensed under the MIT License.

---

## 💡 Inspiration

Built to solve a real problem:\
Understanding large codebases quickly and efficiently without wasting hours.

---

## 🧑‍💻 Author

**Hrishikesh Shendage**\
GitHub: [[https://github.com/Hrishi115](https://github.com/Hrishi115)]

---

## ⭐ Support

If you find this project useful, consider giving it a ⭐ on GitHub!

---



