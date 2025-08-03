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

        # LOGIN usando campos por NAME
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

        # ESPERAR PANEL CARPETAS Y ENCONTRAR 'ORDERS'
        print("⏳ Esperando panel de carpetas…")
        WebDriverWait(driver, settings.WAIT_LONG).until(
            EC.presence_of_element_located((By.CLASS_NAME, "folders"))
        )
        time.sleep(2)
        folders_div = driver.find_element(By.CLASS_NAME, "folders")
        carpetas = folders_div.find_elements(By.XPATH, ".//div | .//span")
        orders_elem = None
        for c in carpetas:
            if "orders" in c.text.strip().lower():
                orders_elem = c
                break

        if orders_elem is None:
            raise Exception("No se encontró la carpeta ORDERS. Verifica el texto exacto en el panel de carpetas.")

        driver.execute_script("arguments[0].scrollIntoView(true);", orders_elem)
        orders_elem.click()
        print("✅ Carpeta 'ORDERS' abierta.")

        # ESPERAR TABLA DE CORREOS
        print("⏳ Esperando que cargue la tabla de correos...")
        WebDriverWait(driver, settings.WAIT_LONG).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'tr.Widgets_Email_Grid_Row'))
        )
        time.sleep(2)

        # Iterar sobre las filas de correos
        rows = driver.find_elements(By.CSS_SELECTOR, 'tr.Widgets_Email_Grid_Row')
        print(f"📨 Correos encontrados: {len(rows)}")
        mails = []
        for i, row in enumerate(rows):
            try:
                subj = row.find_element(By.CSS_SELECTOR, 'div[_ref="subject"]').text.strip()
                recv = row.find_element(By.CSS_SELECTOR, 'div[_ref="received"]').text.strip()
                if subj.lower() == "subject" and recv.lower() == "received":
                    continue
                mails.append({"Subject": subj, "Received": recv})
                print(f"{i+1}. Subject: {subj} | Received: {recv}")
            except Exception as e:
                print(f"❌ Error en fila {i}: {e}")

        print(f"✅ Se extrajeron {len(mails)} mensajes.")
        return mails

    finally:
        driver.quit()
