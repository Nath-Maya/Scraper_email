from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from config import Settings

def scrap_rackspace_emails(settings: Settings):
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    if settings.CHROME_HEADLESS:
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=options)

    try:
        print("🚀 Iniciando scraper para Rackspace Webmail...")
        driver.get(settings.RACKSPACE_URL)

        # LOGIN
        print("🔐 Esperando campos de login…")
        WebDriverWait(driver, settings.WAIT_LONG).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        driver.find_element(By.NAME, "username").send_keys(settings.RACKSPACE_USERNAME)
        driver.find_element(By.NAME, "password").send_keys(settings.RACKSPACE_PASSWORD)
        WebDriverWait(driver, settings.WAIT_SHORT).until(
            EC.element_to_be_clickable((By.ID, "login-btn"))
        ).click()
        print("✅ Login enviado.")

        # Espera panel de carpetas
        print("⏳ Esperando panel de carpetas…")
        WebDriverWait(driver, settings.WAIT_LONG).until(
            EC.presence_of_element_located((By.CLASS_NAME, "folders"))
        )
        time.sleep(2)
        folders_div = driver.find_element(By.CLASS_NAME, "folders")

        # --- Solo ORDERS ---
        orders_folder = None
        for folder in folders_div.find_elements(By.CSS_SELECTOR, 'div[_ref="folder"]'):
            try:
                label = folder.find_element(By.CSS_SELECTOR, 'span.label')
                if label.text.strip().upper() == "ORDERS":
                    orders_folder = folder
                    break
            except Exception:
                continue

        if not orders_folder:
            raise Exception("No se encontró la carpeta ORDERS en el árbol de carpetas.")

        # Click en ORDERS
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", orders_folder)
        link = orders_folder.find_element(By.CSS_SELECTOR, 'a.link')
        driver.execute_script("arguments[0].click();", link)
        print("✅ Carpeta 'ORDERS' abierta.")

        # Espera la tabla de correos
        WebDriverWait(driver, settings.WAIT_LONG).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'tr.Widgets_Email_Grid_Row'))
        )
        time.sleep(2)

        # Extrae la lista de correos SOLO de ORDERS
        all_emails = []
        rows = driver.find_elements(By.CSS_SELECTOR, 'tr.Widgets_Email_Grid_Row')
        print(f"🔍 Se encontraron {len(rows)} correos en ORDERS.")
        for i, row in enumerate(rows):
            try:
                subj = row.find_element(By.CSS_SELECTOR, 'div[_ref="subject"]').text.strip()
                recv = row.find_element(By.CSS_SELECTOR, 'div[_ref="received"]').text.strip()
                if subj.lower() == "subject" and recv.lower() == "received":
                    continue
                all_emails.append({"Subject": subj, "Received": recv})
            except Exception as e:
                print(f"❌ Error en fila {i}: {e}")

        print(f"✅ Se extrajeron {len(all_emails)} mensajes en total.")
        return all_emails

    finally:
        driver.quit()
