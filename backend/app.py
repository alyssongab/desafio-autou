import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask import render_template
from dotenv import load_dotenv
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

load_dotenv()

app = Flask(__name__)
CORS(app)

API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-mnli"
API_TOKEN = os.getenv("HF_API_TOKEN")
headers = {"Authorization": f"Bearer {API_TOKEN}"}

def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()

# funcao para chamar a IA com os parametros
def classifica_texto(text):
    payload = {
        "inputs": text,
        "parameters": {"candidate_labels": ["Produtivo", "Improdutivo"]},
    }
    response = query(payload)
    return response

def valida_texto(text, min_chars=20, min_content_words=2):
    """
    Verifica se um texto tem o mínimo de substância para ser analisado.
    """
    if len(text) < min_chars:
        return False

    words = word_tokenize(text.lower())
    
    # palavras que não são stop words
    stop_words_pt = set(stopwords.words('portuguese'))
    content_words = [word for word in words if word.isalpha() and word not in stop_words_pt]
    
    if len(content_words) < min_content_words:
        return False
        
    return True

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/classificar", methods=['POST'])
def controla_classificacao():
    data = request.get_json()

    if not data or 'text' not in data or not data['text']:
        return jsonify({"error": "O campo 'text' está faltando ou está vazio."}), 400
    
    email_text = data['text']

    if not valida_texto(email_text):
        return jsonify({"error": "O texto fornecido é muito curto ou não contém conteúdo suficiente."}), 400

    try:
        resultado_ia = classifica_texto(email_text)
        categoria = resultado_ia['labels'][0]
        score = resultado_ia['scores'][0]

        resposta = ""

        if categoria == "Produtivo":
            resposta = "Obrigado pelo email. A equipe responsável recebeu sua solicitação e retornaremos em breve."
        else:
            resposta = "Agradecemos seu contato. Sua mensagem foi recebida e arquivada."

        return jsonify({
            "categoria": categoria,
            "score": f"{score:.2%}",
            "resposta": resposta
        })
    
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Erro ao conectar com a API Hugging Face: {e}"}), 503
    
    except Exception as e:
        return jsonify({"error": f"Ocorreu um erro inesperado: {e}"}), 500
    
if __name__ == '__main__':
    app.run(port=5000, debug=True)