from flask import Flask, request, jsonify
from flask_cors import CORS
import yagmail
from datetime import datetime
import os
import tempfile
from reportlab.lib import colors
from reportlab.lib.pagesizes import A5
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm

app = Flask(__name__)
CORS(app)  # Permet à ton menu de communiquer avec le backend

# ============================================
# CONFIGURATION EMAIL
# ============================================
EMAIL_EXPEDITEUR = "Jeremyodimba322@gmail.com"  # Ton email
MOT_DE_PASSE = "afad pinb vlzo bjka"            # Ton mot de passe d'application
EMAIL_DESTINATAIRE = "Jeremyodimba322@gmail.com" # Toi-même (peut être le même)

# ============================================
# FONCTION POUR CRÉER LA FACTURE PDF
# ============================================
def creer_facture_pdf(data):
    """
    Crée un fichier PDF de facture à partir des données de commande
    """
    # Créer un fichier temporaire
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf', mode='wb') as tmp:
        pdf_path = tmp.name
    
    # Créer le document PDF
    doc = SimpleDocTemplate(
        pdf_path, 
        pagesize=A5,
        rightMargin=10*mm,
        leftMargin=10*mm,
        topMargin=10*mm,
        bottomMargin=10*mm
    )
    
    styles = getSampleStyleSheet()
    story = []
    
    # Style pour le titre principal
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#003580'),
        alignment=1,  # Centre
        spaceAfter=10,
        fontName='Helvetica-Bold'
    )
    
    # Style pour le sous-titre
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.grey,
        alignment=1,
        spaceAfter=20
    )
    
    # Style pour le total
    total_style = ParagraphStyle(
        'TotalStyle',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#003580'),
        alignment=2,  # Droite
        spaceBefore=15,
        fontName='Helvetica-Bold'
    )
    
    # Style pour les lignes de commande
    commande_style = ParagraphStyle(
        'CommandeStyle',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=4,
        fontName='Helvetica'
    )
    
    # ========== CONTENU DU PDF ==========
    
    # En-tête
    story.append(Paragraph("RESTAURANT PULLMAN", title_style))
    story.append(Paragraph("LUBUMBASHI", subtitle_style))
    
    # Date et heure
    date_str = datetime.now().strftime('%d/%m/%Y à %H:%M')
    story.append(Paragraph(f"<i>{date_str}</i>", styles['Italic']))
    story.append(Spacer(1, 10))
    
    # Informations client
    story.append(Paragraph(f"<b>Client:</b> {data['nom']}", styles['Normal']))
    story.append(Paragraph(f"<b>Table:</b> {data['table']}", styles['Normal']))
    story.append(Spacer(1, 15))
    
    # Ligne de séparation
    story.append(Paragraph("─" * 45, styles['Normal']))
    story.append(Spacer(1, 10))
    
    # Titre commande
    story.append(Paragraph("<b>COMMANDE</b>", styles['Heading2']))
    story.append(Spacer(1, 5))
    
    # Détails de la commande
    commande_lines = data['commande'].split('\n')
    for line in commande_lines:
        if line.strip():
            story.append(Paragraph(line, commande_style))
    
    story.append(Spacer(1, 10))
    story.append(Paragraph("─" * 45, styles['Normal']))
    
    # Total
    story.append(Paragraph(f"TOTAL: {data['total']}", total_style))
    story.append(Spacer(1, 15))
    
    # Message de remerciement
    story.append(Paragraph("Merci de votre visite !", styles['Italic']))
    story.append(Paragraph("À très bientôt", styles['Normal']))
    
    # Générer le PDF
    doc.build(story)
    
    return pdf_path

# ============================================
# ROUTE POUR RECEVOIR LES COMMANDES
# ============================================
@app.route('/commande', methods=['POST'])
def recevoir_commande():
    """
    Endpoint principal pour recevoir les commandes du menu
    """
    try:
        # 1. Récupérer les données envoyées par le menu
        data = request.json
        print("\n" + "="*60)
        print("🔔 NOUVELLE COMMANDE REÇUE")
        print("="*60)
        print(f"👤 Client: {data.get('nom', 'Non spécifié')}")
        print(f"🔢 Table: {data.get('table', 'Non spécifiée')}")
        print(f"📋 Commande:\n{data.get('commande', 'Vide')}")
        print(f"💰 Total: {data.get('total', '0€')}")
        print("="*60)
        
        # 2. Créer la facture PDF
        print("📄 Génération de la facture PDF...")
        facture_path = creer_facture_pdf(data)
        print(f"✅ Facture créée: {facture_path}")
        
        # 3. Préparer l'email
        sujet = f"🧾 FACTURE - Table {data['table']} - {data['nom']}"
        
        # Corps de l'email en HTML
        contenu_html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .header {{ background-color: #003580; color: white; padding: 10px; text-align: center; }}
                .content {{ padding: 20px; }}
                .commande {{ background-color: #f5f5f5; padding: 10px; border-radius: 5px; }}
                .total {{ font-size: 18px; color: #003580; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2>🍽️ RESTAURANT PULLMAN</h2>
            </div>
            <div class="content">
                <h3>Nouvelle commande</h3>
                <p><strong>Client:</strong> {data['nom']}<br>
                <strong>Table:</strong> {data['table']}<br>
                <strong>Date:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
                
                <h4>Détails de la commande :</h4>
                <div class="commande">
                    <pre>{data['commande']}</pre>
                </div>
                
                <p class="total">💰 Total : {data['total']}</p>
                
                <p><em>La facture détaillée est jointe à cet email.</em></p>
                
                <hr>
                <p style="color: #666; font-size: 12px;">
                    Cet email a été envoyé automatiquement par le système de commande du restaurant.
                </p>
            </div>
        </body>
        </html>
        """
        
        # Version texte simple (fallback)
        contenu_texte = f"""
        RESTAURANT PULLMAN
        =================
        
        Client: {data['nom']}
        Table: {data['table']}
        Date: {datetime.now().strftime('%d/%m/%Y %H:%M')}
        
        COMMANDE:
        {data['commande']}
        
        TOTAL: {data['total']}
        
        La facture est jointe à cet email.
        """
        
        # 4. Envoyer l'email
        print("📧 Envoi de l'email...")
        yag = yagmail.SMTP(EMAIL_EXPEDITEUR, MOT_DE_PASSE)
        
        yag.send(
            to=EMAIL_DESTINATAIRE,
            subject=sujet,
            contents=[contenu_html, contenu_texte],  # Envoie les deux versions
            attachments=[facture_path]  # La facture PDF en pièce jointe
        )
        
        print(f"✅ Email envoyé avec succès à {EMAIL_DESTINATAIRE}")
        
        # 5. Nettoyer le fichier temporaire
        os.unlink(facture_path)
        print("🧹 Fichier temporaire supprimé")
        
        # 6. Répondre au menu que tout est OK
        return jsonify({
            "status": "ok",
            "message": "Commande envoyée avec facture par email",
            "details": {
                "destinataire": EMAIL_DESTINATAIRE,
                "date": datetime.now().strftime('%d/%m/%Y %H:%M')
            }
        })
        
    except Exception as e:
        # En cas d'erreur, on la log et on renvoie une réponse d'erreur
        print(f"❌ ERREUR: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            "status": "error",
            "message": f"Erreur lors du traitement: {str(e)}"
        }), 500

# ============================================
# ROUTE DE TEST
# ============================================
@app.route('/', methods=['GET'])
def home():
    """
    Page d'accueil de l'API
    """
    return jsonify({
        "status": "ok",
        "nom": "API Restaurant Pullman",
        "version": "1.0",
        "endpoints": {
            "/": "Cette page",
            "/test": "Test de connexion",
            "/commande": "POST - Envoyer une commande (POST)"
        },
        "email_destinataire": EMAIL_DESTINATAIRE
    })

@app.route('/test', methods=['GET'])
def test():
    """
    Route de test pour vérifier que l'API fonctionne
    """
    return jsonify({
        "status": "ok",
        "message": "Backend opérationnel",
        "email_config": {
            "expediteur": EMAIL_EXPEDITEUR,
            "destinataire": EMAIL_DESTINATAIRE
        },
        "timestamp": datetime.now().isoformat()
    })

# ============================================
# ROUTE POUR TESTER L'ENVOI D'EMAIL
# ============================================
@app.route('/test-email', methods=['GET'])
def test_email():
    """
    Route pour tester l'envoi d'email (utile pour le debug)
    """
    try:
        # Créer une commande factice
        test_data = {
            "nom": "Test",
            "table": "99",
            "commande": "1x Menu Test - 25€\n1x Boisson - 5€",
            "total": "30€"
        }
        
        # Créer la facture
        facture_path = creer_facture_pdf(test_data)
        
        # Envoyer l'email
        yag = yagmail.SMTP(EMAIL_EXPEDITEUR, MOT_DE_PASSE)
        yag.send(
            to=EMAIL_DESTINATAIRE,
            subject="🧪 TEST - Envoi d'email",
            contents="Ceci est un email de test depuis le backend.",
            attachments=[facture_path]
        )
        
        os.unlink(facture_path)
        
        return jsonify({
            "status": "ok",
            "message": "Email de test envoyé avec succès"
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

# ============================================
# POINT D'ENTRÉE PRINCIPAL
# ============================================
if __name__ == '__main__':
    # Afficher la configuration au démarrage
    print("\n" + "="*60)
    print("🚀 BACKEND RESTAURANT PULLMAN")
    print("="*60)
    print(f"📧 Email expéditeur: {EMAIL_EXPEDITEUR}")
    print(f"📨 Email destinataire: {EMAIL_DESTINATAIRE}")
    print(f"🔌 Serveur démarré sur http://127.0.0.1:5000")
    print("="*60)
    print("\n📡 En attente des commandes...\n")
    
    # Démarrer le serveur
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)        
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
