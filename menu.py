from flask import Flask, request, jsonify
from flask_cors import CORS
import yagmail
from datetime import datetime
import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import A5
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import tempfile

app = Flask(__name__)
CORS(app)

# CONFIGURATION EMAIL - TOUT POUR TOI !
EMAIL = "Jeremyodimba322@gmail.com"
MOT_DE_PASSE = "afad pinb vlzo bjka"

def creer_facture(data):
    """Crée un PDF de facture"""
    
    # Créer un fichier temporaire
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
        pdf_path = tmp.name
    
    # Créer le PDF
    doc = SimpleDocTemplate(pdf_path, pagesize=A5)
    styles = getSampleStyleSheet()
    story = []
    
    # En-tête
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#003580'),
        alignment=1
    )
    story.append(Paragraph("RESTAURANT PULLMAN", title_style))
    story.append(Spacer(1, 10))
    
    # Date
    story.append(Paragraph(f"Date: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
    story.append(Spacer(1, 10))
    
    # Client
    story.append(Paragraph(f"Client: {data['nom']}", styles['Normal']))
    story.append(Paragraph(f"Table: {data['table']}", styles['Normal']))
    story.append(Spacer(1, 15))
    
    # Commande
    story.append(Paragraph("COMMANDE:", styles['Heading2']))
    story.append(Spacer(1, 5))
    
    commande_lines = data['commande'].split('\n')
    for line in commande_lines:
        if line.strip():
            story.append(Paragraph(line, styles['Normal']))
    
    story.append(Spacer(1, 15))
    
    # Total
    total_style = ParagraphStyle(
        'TotalStyle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#003580'),
        alignment=2
    )
    story.append(Paragraph(f"TOTAL: {data['total']}", total_style))
    
    # Générer le PDF
    doc.build(story)
    
    return pdf_path

@app.route('/commande', methods=['POST'])
def recevoir_commande():
    try:
        # 1. Recevoir la commande du menu
        data = request.json
        print(f"\n📥 Commande reçue de {data['nom']} (Table {data['table']})")
        
        # 2. Créer la facture PDF
        print("📄 Génération de la facture...")
        facture_path = creer_facture(data)
        
        # 3. Préparer l'email
        sujet = f"🧾 FACTURE - Table {data['table']} - {data['nom']}"
        
        contenu = f"""
        <h2>🍽️ NOUVELLE COMMANDE</h2>
        
        <p><strong>Client:</strong> {data['nom']}<br>
        <strong>Table:</strong> {data['table']}<br>
        <strong>Date:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
        
        <h3>Détails de la commande :</h3>
        <pre>{data['commande']}</pre>
        
        <h3>💰 Total : {data['total']}</h3>
        
        <p><em>La facture est en pièce jointe.</em></p>
        """
        
        # 4. ENVOYER L'EMAIL À TON ADRESSE
        yag = yagmail.SMTP(EMAIL, MOT_DE_PASSE)
        yag.send(
            to=EMAIL,  # À TOI-MÊME !
            subject=sujet,
            contents=contenu,
            attachments=[facture_path]
        )
        
        print(f"✅ Facture envoyée à {EMAIL}")
        
        # 5. Nettoyer le fichier temporaire
        os.unlink(facture_path)
        
        # 6. Répondre au menu
        return jsonify({
            "status": "ok", 
            "message": "Commande envoyée avec facture"
        })
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return jsonify({
            "status": "error", 
            "message": str(e)
        }), 500

@app.route('/test', methods=['GET'])
def test():
    return jsonify({
        "status": "ok", 
        "message": "Backend opérationnel",
        "email": EMAIL
    })

if __name__ == '__main__':
    print("="*60)
    print("🚀 BACKEND RESTAURANT - PULLMAN")
    print("="*60)
    print(f"📧 Les factures seront envoyées à : {EMAIL}")
    print("🔌 Serveur démarré sur http://127.0.0.1:5000")
    print("="*60)
    app.run(host='0.0.0.0', port=5000, debug=True)