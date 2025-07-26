from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
from config import Settings

def scrap_rackspace_emails(settings: Settings):
    """Inicia sesión, abre la carpeta ORDERS y extrae el texto de correos abiertos."""
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    if settings.CHROME_HEADLESS:
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=options)

    try:
        # 1) Abrir URL
        driver.get(settings.RACKSPACE_URL)

        # 2) Login
        print("🔐 Esperando campos de login…")
        WebDriverWait(driver, settings.WAIT_LONG).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        WebDriverWait(driver, settings.WAIT_SHORT).until(
            EC.presence_of_element_located((By.NAME, "password"))
        )
        driver.find_element(By.NAME, "username").send_keys(settings.RACKSPACE_USERNAME)
        driver.find_element(By.NAME, "password").send_keys(settings.RACKSPACE_PASSWORD)
        WebDriverWait(driver, settings.WAIT_SHORT).until(
            EC.element_to_be_clickable((By.ID, "login-btn"))
        ).click()
        print("✅ Login enviado.")

        # 3) Panel carpetas
        print("⏳ Esperando panel de carpetas…")
        folders_container = WebDriverWait(driver, settings.WAIT_LONG).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.folders"))
        )

        # 4) Abrir ORDERS
        if not click_folder(driver, folders_container, "ORDERS", settings):
            raise Exception("No se encontró / no se pudo clickear la carpeta ORDERS.")
        print("✅ Carpeta 'ORDERS' abierta.")

        # 5) Esperar carga de correos
        print("⏳ Esperando carga de correos…")
        time.sleep(12)

        # 6) Extraer texto de correos abiertos (iframes)
        extracted = []
        iframes = driver.find_elements(By.CSS_SELECTOR, "iframe#msgBody")
        if not iframes:
            print("ℹ️ No hay iframes con correos abiertos. Próximo paso: automatizar el clic por cada fila.")
        for iframe in iframes:
            driver.switch_to.frame(iframe)
            try:
                body_text = driver.find_element(By.TAG_NAME, "body").get_attribute("innerText")
                extracted.append(parse_email(body_text))
            finally:
                driver.switch_to.default_content()

        return extracted

    finally:
        driver.quit()


def click_folder(driver, container, target_name: str, settings: Settings) -> bool:
    """Busca un div.folder con texto que contenga target_name y hace clic en su <a.link>."""
    target = target_name.upper()

    # Hacer varios scrolls por si el árbol es largo.
    for _ in range(12):
        folders = container.find_elements(By.CSS_SELECTOR, "div.folder")
        for f in folders:
            txt = f.text.strip().upper()
            if target in txt:
                # Preferir el link interno si existe
                try:
                    link = f.find_element(By.CSS_SELECTOR, "a.link")
                except NoSuchElementException:
                    link = f
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", link)
                time.sleep(0.2)
                driver.execute_script("arguments[0].click();", link)
                return True

        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollTop + 300;", container)
        time.sleep(0.3)

    # Fallback con XPath por texto
    xp = (
        "//div[contains(@class,'folders')]"
        "//*[contains(normalize-space(translate(text(),'abcdefghijklmnopqrstuvwxyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ')), 'ORDERS')]"
    )
    try:
        el = driver.find_element(By.XPATH, xp)
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
        time.sleep(0.2)
        driver.execute_script("arguments[0].click();", el)
        return True
    except Exception:
        return False


def parse_email(text: str) -> dict:
    """Parser simple de ejemplo. Ajusta reglas según el formato real."""
    info = {"Producto": "", "Cantidad": "", "Precio": "", "Email": ""}

    for raw in text.splitlines():
        line = raw.strip()

        if "Business Cards" in line and "Lam" in line:
            info["Producto"] = line
        elif ("Qty" in line or "Quantity" in line):
            parts = line.split()
            last = parts[-1] if parts else ""
            if last.isdigit():
                info["Cantidad"] = last
        elif ("Subtotal" in line or "Price" in line) and "$" in line:
            info["Precio"] = line.split("$")[-1].strip()
        elif "customer:" in line.lower():
            info["Email"] = line.split("customer:")[-1].strip()

    return info
