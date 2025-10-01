import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# API_URL = "https://router.huggingface.co/hf-inference/models/facebook/bart-large-mnli"
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

@app.route("/classificar", methods=['POST'])
def controla_classificacao():
    data = request.get_json()

    if not data or 'text' not in data or not data['text']:
        return jsonify({"error": "O campo 'text' está faltando ou está vazio."}), 400
    
    email_text = data['text']

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
        return jsonify({"erro": f"Erro ao conectar com a API Hugging Face: {e}"}), 503
    
    except Exception as e:
        return jsonify({"erro": f"Ocorreu um erro inesperado: {e}"}), 500
    
if __name__ == '__main__':
    app.run(port=5000, debug=True)