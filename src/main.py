from email_scraper import scrap_rackspace_emails
from excel_writer import save_emails_to_excel
from config import Settings

def main():
    settings = Settings.load()
    settings.safe_print()
    print("🚀 Iniciando scraper Rackspace → Excel …")
    data = scrap_rackspace_emails(settings)
    if data:
        save_emails_to_excel(data, settings.OUTPUT_XLSX)
        print(f"✅ {len(data)} correos procesados.")
    else:
        print("ℹ️ No se extrajo ningún correo.")

if __name__ == "__main__":
    main()
