# 🇪🇨 Consulta de Fecha de Nacimiento — Ecuador

Script para consultar la **fecha y lugar de nacimiento** de una persona en Ecuador
a partir de su **número de cédula** o de sus **apellidos y nombres**, de forma
**gratuita** y sin pagar los servicios "premium" de terceros.

Usa dos vías:

1. **API de tercero (rápida)** — ataca los endpoints internos de un portal de consultas.
2. **Navegador headless (robusta)** — llena el formulario real con Playwright y lee el resultado.

---

## ✨ Características

- Consulta por **cédula** o por **apellidos y nombres**.
- Devuelve **fecha de nacimiento** y **lugar de nacimiento**.
- Sin credenciales, sin API keys, sin registro.
- Reintentos automáticos sobre varios endpoints (por si uno falla).
- Incluye la lista de endpoints decodificados del JavaScript ofuscado del portal.

---

## 🧠 Cómo funciona

El portal objetivo (`ecuadorlegalonline.com`) es un WordPress que en el cliente
carga un JavaScript **ofuscado** (`cifechaapiyjs.js` / `cinameapi3yjs.js`).
Ese JS llama a backends `.php` internos y a fuentes externas.

Decodificando el JS (base64 con alfabeto invertido) se obtienen estos endpoints:

| Función | Método | Endpoint |
|---|---|---|
| Health-check | GET | `https://www.ecuadorlegalonline.com/js/aliveapi.php` |
| Por cédula | GET | `https://www.ecuadorlegalonline.com/modulo/datos/consultar-cedula.php` |
| Por nombre | GET | `https://apps.ecuadorlegalonline.com/modulo/consultar-cedulanombre.php?nombres=<NOMBRE>` |
| Respaldo (JSON) | GET | `https://srienlinea.sri.gob.ec/movil-servicios/api/v1.0/deudas/porIdentificacion/<CEDULA>?tipoPersona=N` |

> ⚠️ Los endpoints `.php` a veces responden `404` a clientes que no son navegador.
> Por eso existe la vía con Playwright (100 % fiable) y la vía con `requests` (rápida).

---

## 📦 Requisitos

- Python 3.9+
- Para la vía rápida: `requests`, `beautifulsoup4`
- Para la vía robusta: `playwright` (+ Chromium)

```bash
pip install requests beautifulsoup4
# solo si usas la vía con navegador:
pip install playwright
playwright install chromium
```

---

## 🚀 Uso

### Opción A — Vía navegador (recomendada, siempre funciona)

```python
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import re

URL = "https://www.ecuadorlegalonline.com/consultas/registro-civil/consultar-fecha-nacimiento/"

def fecha_nacimiento(valor, por="N"):   # por="N" → cédula ; por="A" → apellidos/nombre
    with sync_playwright() as p:
        nav = p.chromium.launch(headless=True)
        ctx = nav.new_context(
            user_agent=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/124.0.0.0 Safari/537.36"),
            locale="es-EC",
        )
        pg = ctx.new_page()
        pg.goto(URL, wait_until="load", timeout=60000)

        pg.wait_for_selector("#Opcion", state="attached", timeout=60000)
        pg.select_option("#Opcion", por)
        pg.fill("#txtName", valor)
        pg.click("#btnNext")

        # espera a que aparezca una fecha real (no el placeholder XXXX-XX-XX)
        pg.wait_for_function(
            r"""() => {
                const t = (document.querySelector('#resultado')?.innerText || '');
                return /\d{4}\s*[-/]\s*\d{1,2}\s*[-/]\s*\d{1,2}/.test(t);
            }""",
            timeout=60000,
        )
        pg.wait_for_timeout(1500)
        texto = pg.inner_text("#resultado")
        nav.close()

    m = re.search(r"\d{4}\s*[-/]\s*\d{1,2}\s*[-/]\s*\d{1,2}", texto)
    return m.group(0) if m else None

print(fecha_nacimiento("1712345678", "N"))
```

### Opción B — Vía `requests` (rápida)

```python
import requests

H = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Referer": "https://www.ecuadorlegalonline.com/consultas/registro-civil/consultar-fecha-nacimiento/",
}

def por_cedula(cedula):
    r = requests.get(
        "https://www.ecuadorlegalonline.com/modulo/datos/consultar-cedula.php",
        params={"cedula": cedula}, headers=H, timeout=20,
    )
    return r.text

print(por_cedula("1712345678"))
```

---

## 🐛 Solución de problemas

| Síntoma | Causa | Solución |
|---|---|---|
| `Timeout waiting for locator "#Opcion"` | El sitio sirvió otra página al bot | Usa `user_agent` real, `wait_until="load"` y `state="attached"` (ver Opción A) |
| El resultado muestra `XXXX-XX-XX` | Leíste la plantilla antes de que cargara la fecha | Espera el patrón de fecha real (regex `\d{4}-\d{2}-\d{2}`) |
| El endpoint `.php` devuelve `404` | El portal bloquea clientes no-navegador | Usa la Opción A, o captura la petición real con DevTools |

**Capturar el endpoint exacto con DevTools:** abre la página → `F12` → pestaña
**Network** → filtra **Fetch/XHR** → consulta una cédula → copia el **Request URL**.

---

## 🏛️ Fuente oficial (Registro Civil)

Para ir **directo a la fuente** (DIGERCIC) en vez de un tercero:

- Consulta de datos en línea: `https://servicios.registrocivil.gob.ec/cdd/`
- Consulta de cedulados (básica): `https://www.corporacionregistrocivil.gob.ec/pages/CeduladosGratuita.aspx`
- Web Service Demográfico oficial (requiere convenio): contacto `servicios.electronicos@registrocivil.gob.ec`

> El portal oficial suele tener sesión/captcha; el endpoint se captura igual con DevTools.

---

## 📁 Estructura sugerida

```
.
├── README.md
├── requirements.txt
├── fecha_nacimiento.py     # Opción A (Playwright)
└── fecha_requests.py       # Opción B (requests)
```

---

## ⚖️ Aviso legal

- Los datos provienen del **Registro Civil de Ecuador** y de portales que los reexponen.
- Uso libre para fines personales. Verifica siempre con un documento oficial.
- No afiliado al Registro Civil ni a los portales de terceros.

---

## 📝 Notas

- Los endpoints pueden cambiar sin aviso (por eso el script reintenta varios).
- La vía con Playwright es la más estable; úsala para consultas puntuales.
- Para consultas masivas, combina con la Opción B y maneja reintentos.

## 📄 Licencia

MIT — úsalo, modifícalo y compártelo libremente.
