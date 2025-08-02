import pandas as pd
import os

def save_emails_to_excel(emails, file_path="data/emails.xlsx"):
    print("DEBUG antes de crear directorio y guardar excel")
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    if not emails:
        print("DEBUG: emails vacío, solo headers.")
        df = pd.DataFrame(columns=["Subject", "Received"])
    else:
        print(f"DEBUG: emails a guardar: {emails}")
        df = pd.DataFrame(emails)
    print("DEBUG: Guardando el archivo Excel…")
    df.to_excel(file_path, index=False)
    print(f"📄 Datos guardados en {file_path}")
