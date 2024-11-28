import os
from flask import Flask, render_template, request, send_file
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfgen import canvas

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'static', 'uploads')


# Função para criar o PDF
def generate_pdf(form_data, before_path, after_path, pdf_path):
    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4

    # Adicionar logótipo
    logo_path = os.path.join(app.config['UPLOAD_FOLDER'], "logo.png")
    if os.path.exists(logo_path):
        c.drawImage(logo_path, width - 540, height - 100, width=150, height=50)

    # Título do relatório
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(width / 2, height - 150, "Field Service Report")

    # Campos à esquerda
    x_right = 50
    y = height - 200
    c.setFont("Helvetica-Bold", 12)
    for key in ["Company", "Address", "Country", "Contact Person"]:
        c.setFont("Helvetica-Bold", 12) # Labels a negrito
        c.drawString(x_right, y, f"{key}:")
        c.setFont("Helvetica", 12) # Info colocada pelo user sem negrito
        c.drawString(x_right + 100, y, f"{form_data.get(key, '')}")
        y -= 20

    # Campos à direita dentro de uma box
    x_left = width - 250
    y = height - 200
    c.setStrokeColor(colors.grey)
    c.setLineWidth(0.5)
    c.rect(x_left, y - 100, 200, 120)  # Caixa ao redor dos campos
    c.setFont("Helvetica-Bold", 12)
    for key in ["K-Nr", "Creation Date", "Technician", "Assembly Start", "Assembly End"]:
        c.setFont("Helvetica-Bold", 12) # Labels a negrito
        c.drawString(x_left + 10, y, f"{key}:")
        c.setFont("Helvetica", 12) # Info colocada pelo user sem negrito
        c.drawString(x_left + 110, y, f"{form_data.get(key, '')}")
        y -= 20

    # Campo Machine Type and Number
    y -= 20
    c.setFont("Helvetica-Bold", 12) # Label a negrito
    c.drawString(50, y, "Machine Type and Number:")
    c.setFont("Helvetica", 12) # Info colocada pelo user sem negrito
    y -= 15 # Ajustar para exibir a info colocada pelo user abaixo da label
    c.drawString(50, y, f"{form_data.get('Machine Type and Number', '')}")

    # Linha divisória
    y -= 20
    c.setLineWidth(1)
    c.line(50, y, width - 50, y)

    # Campos como checklist
    def add_checklist(field_name, y_offset):
        text = form_data.get(field_name, "").strip()
        if text:
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y_offset, f"{field_name}:")
            y_offset -= 20
            c.setFont("Helvetica", 12)
            for line in text.split("\n"):
                c.drawString(70, y_offset, f"• {line.strip()}")
                y_offset -= 15
        return y_offset

    y -= 30
    for field in ["Service", "Further Actions", "Parts to be quoted"]:
        y = add_checklist(field, y)

    # Imagens
    y -= 50
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Photo Before:")
    c.drawImage(before_path, 50, y - 170, width=200, height=150)
    c.drawString(300, y, "Photo After:")
    c.drawImage(after_path, 300, y - 170, width=200, height=150)

    # Salva o PDF
    c.save()


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        form_data = request.form.to_dict()
        before_image = request.files.get("before_image")
        after_image = request.files.get("after_image")

        # Validação para garantir que os arquivos foram enviados
        if not before_image or not before_image.filename:
            return "Error: Please upload the 'Before' image.", 400
        if not after_image or not after_image.filename:
            return "Error: Please upload the 'After' image.", 400

        before_path = os.path.join(app.config['UPLOAD_FOLDER'], before_image.filename)
        after_path = os.path.join(app.config['UPLOAD_FOLDER'], after_image.filename)

        before_image.save(before_path)
        after_image.save(after_path)

        company_name = form_data.get("Company", "Unknown")
        k_nr = form_data.get("K-Nr", "Unknown")
        pdf_filename = f"Field Service Report {company_name} {k_nr}.pdf"
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf_filename)

        generate_pdf(form_data, before_path, after_path, pdf_path)
        return send_file(pdf_path)

    return render_template("form.html")

if __name__ == "__main__":
    # app.run(debug=True)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
