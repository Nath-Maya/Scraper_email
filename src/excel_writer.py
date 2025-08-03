import pandas as pd
import os

def save_emails_to_excel(emails, file_path="data/emails.xlsx"):
    # Ruta absoluta relativa al directorio raíz del proyecto
    ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    abs_path = os.path.join(ROOT_DIR, file_path)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    if not emails:
        df = pd.DataFrame(columns=["Subject", "Received"])
    else:
        df = pd.DataFrame(emails)
    df.to_excel(abs_path, index=False)
    print(f"📄 Datos guardados en {abs_path}")
