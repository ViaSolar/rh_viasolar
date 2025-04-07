from flask import Flask, request, render_template_string, send_from_directory
import PyPDF2
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Função para dividir o PDF
def dividir_pdf(input_pdf, output_directory):
    with open(input_pdf, "rb") as file:
        pdf_reader = PyPDF2.PdfReader(file)
        num_pages = len(pdf_reader.pages)

        for i in range(num_pages):
            pdf_writer = PyPDF2.PdfWriter()
            pdf_writer.add_page(pdf_reader.pages[i])

            output_file = os.path.join(output_directory, f"contra_cheque_pagina_{i + 1}.pdf")
            with open(output_file, "wb") as output_pdf:
                pdf_writer.write(output_pdf)

# Rota principal com formulário de upload
@app.route('/')
def index():
    html_content = '''
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <title>Dividir PDF</title>
    </head>
    <body>
        <h2>Upload de PDF para Divisão</h2>
        <form id="uploadForm" enctype="multipart/form-data" method="POST" action="/upload">
            <input type="file" name="pdf" accept=".pdf" required>
            <button type="submit">Enviar</button>
        </form>

        <div id="result"></div>

        <script>
            const form = document.getElementById("uploadForm");
            const resultDiv = document.getElementById("result");

            form.addEventListener("submit", async (e) => {
                e.preventDefault();

                const formData = new FormData(form);

                try {
                    const response = await fetch("/upload", {
                        method: "POST",
                        body: formData
                    });
                    const result = await response.text();
                    resultDiv.innerHTML = `<p>${result}</p>`;
                } catch (error) {
                    resultDiv.innerHTML = `<p>Erro: ${error.message}</p>`;
                }
            });
        </script>
    </body>
    </html>
    '''
    return render_template_string(html_content)

# Rota para upload do PDF
@app.route('/upload', methods=['POST'])
def upload_pdf():
    if 'pdf' not in request.files:
        return "Arquivo não encontrado no formulário."
    
    file = request.files['pdf']
    if file and file.filename.endswith('.pdf'):
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)

        output_directory = os.path.join(UPLOAD_FOLDER, 'output')
        os.makedirs(output_directory, exist_ok=True)

        dividir_pdf(file_path, output_directory)

        return f"PDF dividido com sucesso! Arquivos salvos na pasta: {output_directory}"
    return "Erro ao fazer o upload ou arquivo inválido."

# Servir arquivos divididos
@app.route('/uploads/<path:filename>')
def download_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8000)))
    # Para rodar localmente, use: app.run(debug=True)

