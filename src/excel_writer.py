import pandas as pd
import os

def save_emails_to_excel(emails, file_path="emails.xlsx"):
    if not emails:
        return
    df_new = pd.DataFrame(emails)
    if os.path.exists(file_path):
        df_old = pd.read_excel(file_path)
        df = pd.concat([df_old, df_new], ignore_index=True)
    else:
        df = df_new
    df.to_excel(file_path, index=False)
    print(f"📄 Datos guardados en {file_path}")
