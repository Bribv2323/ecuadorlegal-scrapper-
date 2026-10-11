# pip install playwright && playwright install chromium
from playwright.sync_api import sync_playwright

URL = "https://www.ecuadorlegalonline.com/consultas/registro-civil/consultar-fecha-nacimiento/"

def consultar(valor, tipo="N"):          # tipo: "N" = cédula, "A" = apellidos/nombre
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True)
        pg = b.new_page()
        pg.goto(URL, wait_until="networkidle")

        pg.select_option("#Opcion", tipo)     # elige el modo de búsqueda
        pg.fill("#txtName", valor)
        pg.click("#btnNext")                  # botón CONSULTAR

        pg.wait_for_selector("#resultado table, #resultado", timeout=30000)
        pg.wait_for_timeout(2500)             # deja cargar el ajax
        html = pg.inner_html("#resultado")
        b.close()
        return html

# Ejemplos
print(consultar("1712345678", "N"))   # por cédula
print(consultar("Pinto Haro", "A"))   # por apellidos