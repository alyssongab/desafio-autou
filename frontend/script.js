const form = document.getElementById('email-form');
const emailTextInput = document.getElementById('email-text');
const loadingDiv = document.getElementById('loading');
const resultDiv = document.getElementById('result-container');
const categoriaSpan = document.getElementById('category');
const sugestaoDiv = document.getElementById('suggestion');

const BACKEND_URL = 'http://127.0.0.1:5000/classificar'; 

form.addEventListener('submit', async (event) => {

    event.preventDefault();
    
    loadingDiv.classList.remove('hidden');
    resultDiv.classList.add('hidden');

    const emailText = emailTextInput.value;

    try {

        const response = await fetch(BACKEND_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text: emailText }),
        });

        const data = await response.json();

        if (response.ok) {
            categoriaSpan.textContent = `${data.categoria} (Confiança: ${data.score})`;
            sugestaoDiv.textContent = data.resposta;
            resultDiv.classList.remove('hidden');
        } else {
            alert(`Erro do servidor: ${data.error}`);
        }

    } catch (error) {
        console.error('Falha na comunicação com o backend:', error);
        alert('Não foi possível conectar ao servidor. Verifique se o backend está rodando e tente novamente.');
    } finally {

        loadingDiv.classList.add('hidden');
    }
});