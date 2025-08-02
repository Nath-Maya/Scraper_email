from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from config import Settings

def scrap_rackspace_emails(settings: Settings):
    """Inicia sesión, abre ORDERS y extrae Subject/Received de todos los correos en la lista."""
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    if settings.CHROME_HEADLESS:
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=options)

    try:
        # 1) Abrir URL y Login
        driver.get(settings.RACKSPACE_URL)
        WebDriverWait(driver, settings.WAIT_LONG).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        driver.find_element(By.NAME, "username").send_keys(settings.RACKSPACE_USERNAME)
        driver.find_element(By.NAME, "password").send_keys(settings.RACKSPACE_PASSWORD)
        WebDriverWait(driver, settings.WAIT_SHORT).until(
            EC.element_to_be_clickable((By.ID, "login-btn"))
        ).click()
        print("✅ Login enviado.")

        # 2) Panel carpetas
        print("⏳ Esperando panel de carpetas…")
        folders_container = WebDriverWait(driver, settings.WAIT_LONG).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.folders"))
        )

        # 3) Abrir ORDERS
        if not click_folder(driver, folders_container, "ORDERS", settings):
            raise Exception("No se encontró / no se pudo clickear la carpeta ORDERS.")
        print("✅ Carpeta 'ORDERS' abierta.")

        # 4) Esperar carga de correos
        print("⏳ Esperando carga de correos…")
        time.sleep(7)

        # 5) EXTRAER TODOS SUBJECT Y RECEIVED
        print("🔍 Extrayendo Subject y Received de TODOS los mensajes en la lista…")
        subjects = driver.find_elements(By.CSS_SELECTOR, 'div[_ref="subject"]')
        receiveds = driver.find_elements(By.CSS_SELECTOR, 'div[_ref="received"]')

        # Solo tomamos los pares completos (en el mismo orden visual)
        count = min(len(subjects), len(receiveds))
        mails = []
        for i in range(count):
            subj = subjects[i].text.strip()
            recv = receiveds[i].text.strip()
            mails.append({"Subject": subj, "Received": recv})

        print(f"✅ Se extrajeron {len(mails)} mensajes.")
        return mails

    finally:
        driver.quit()

def click_folder(driver, container, target_name: str, settings: Settings) -> bool:
    target = target_name.upper()
    for _ in range(12):
        folders = container.find_elements(By.CSS_SELECTOR, "div.folder")
        for f in folders:
            txt = f.text.strip().upper()
            if target in txt:
                try:
                    link = f.find_element(By.CSS_SELECTOR, "a.link")
                except:
                    link = f
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", link)
                time.sleep(0.2)
                driver.execute_script("arguments[0].click();", link)
                return True
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollTop + 300;", container)
        time.sleep(0.3)
    return False
