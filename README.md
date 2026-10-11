# file-ujm.py

Script que consulta la **fecha de nacimiento** de una persona en Ecuador
por **número de cédula** o por **apellidos y nombres**, gratis.

Usa Playwright para abrir el formulario, consultar y extraer la fecha.

---

## Requisitos

- Python 3.9+
- Playwright

```bash
pip install playwright
playwright install chromium
```

---

## Uso

1. Abre `file-ujm.py` y edita la última línea con el dato a consultar:

```python
# por cédula
fecha_nacimiento("1712345678", "N")

# o por apellidos y nombre
fecha_nacimiento("Pinto Haro Jorge", "A")
```

2. Ejecuta:

```bash
python file-ujm.py
```

---

## Parámetros

| Parámetro | Valores | Descripción |
|---|---|---|
| `valor` | texto | La cédula o los apellidos y nombres |
| `por` | `"N"` / `"A"` | `"N"` = cédula · `"A"` = apellidos y nombre |

---

## Salida

```
FECHA DETECTADA: 1990-05-14
```

---

## Notas

- `headless=True` → corre sin abrir ventana. Ponlo en `False` para ver el navegador.
- Si sale `XXXX-XX-XX`, es el placeholder: el script ya espera a que cargue la fecha real.
- Los datos vienen del Registro Civil de Ecuador.
