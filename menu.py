from flask import Flask, request, jsonify
from flask_cors import CORS
import yagmail
from datetime import datetime
import os
import tempfile
import logging

from reportlab.lib import colors
from reportlab.lib.pagesizes import A5
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)

EMAIL = "Jeremyodimba322@gmail.com"
MOT_DE_PASSE = "afad pinb vlzo bjka"


# -----------------------------------
# VALIDATION DONNÉES
# -----------------------------------
def valider_commande(data):
    champs_obligatoires = ["nom", "table", "commande", "total"]

    for champ in champs_obligatoires:
        if champ not in data or not data[champ]:
            return False, f"Champ manquant : {champ}"

    return True, None


# -----------------------------------
# CREATION FACTURE PDF
# -----------------------------------
def creer_facture(data):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        pdf_path = tmp.name

    doc = SimpleDocTemplate(pdf_path, pagesize=A5)
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Heading1"],
        fontSize=16,
        textColor=colors.HexColor("#003580"),
        alignment=1
    )

    total_style = ParagraphStyle(
        "TotalStyle",
        parent=styles["Heading2"],
        fontSize=14,
        textColor=colors.HexColor("#003580"),
        alignment=2
    )

    story.append(Paragraph("RESTAURANT PULLMAN", title_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph(
        f"Date : {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        styles["Normal"]
    ))
    story.append(Spacer(1, 10))

    story.append(Paragraph(f"Client : {data['nom']}", styles["Normal"]))
    story.append(Paragraph(f"Table : {data['table']}", styles["Normal"]))
    story.append(Spacer(1, 15))

    story.append(Paragraph("COMMANDE :", styles["Heading2"]))
    story.append(Spacer(1, 5))

    for line in data["commande"].split("\n"):
        if line.strip():
            story.append(Paragraph(line, styles["Normal"]))

    story.append(Spacer(1, 15))
    story.append(Paragraph(f"TOTAL : {data['total']}", total_style))

    doc.build(story)
    return pdf_path


# -----------------------------------
# ROUTE COMMANDE
# -----------------------------------
@app.route("/commande", methods=["POST"])
def recevoir_commande():

    if not request.is_json:
        return jsonify({
            "success": False,
            "message": "Content-Type doit être application/json"
        }), 400

    data = request.get_json()

    valide, erreur = valider_commande(data)
    if not valide:
        return jsonify({
            "success": False,
            "message": erreur
        }), 400

    try:
        logging.info(f"Nouvelle commande reçue : {data}")

        facture_path = creer_facture(data)

        sujet = f"FACTURE - Table {data['table']} - {data['nom']}"

        contenu = f"""
        <h2>Nouvelle commande</h2>
        <p>
        <strong>Client :</strong> {data['nom']}<br>
        <strong>Table :</strong> {data['table']}<br>
        <strong>Date :</strong> {datetime.now().strftime('%d/%m/%Y %H:%M')}
        </p>

        <h3>Détails :</h3>
        <pre>{data['commande']}</pre>

        <h3>Total : {data['total']}</h3>
        """

        yag = yagmail.SMTP(EMAIL, MOT_DE_PASSE)
        yag.send(
            to=EMAIL,
            subject=sujet,
            contents=contenu,
            attachments=[facture_path]
        )

        os.unlink(facture_path)

        return jsonify({
            "success": True,
            "message": "Commande reçue avec succès",
            "timestamp": datetime.now().isoformat()
        }), 200

    except Exception as e:
        logging.error(str(e))

        return jsonify({
            "success": False,
            "message": "Erreur serveur",
            "error": str(e)
        }), 500


# -----------------------------------
# ROUTE TEST
# -----------------------------------
@app.route("/test", methods=["GET"])
def test():
    return jsonify({
        "success": True,
        "message": "API opérationnelle"
    })


# -----------------------------------
# ROUTE HOME
# -----------------------------------
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "success": True,
        "message": "API RESTAURANT PULLMAN en ligne",
        "version": "1.0.0"
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
