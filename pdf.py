import fitz  # PyMuPDF
import os
import re
import csv  # Para guardar los datos en CSV

#  Función para extraer el texto de un PDF
def extraer_texto_pdf(ruta_pdf):
    texto = ""
    with fitz.open(ruta_pdf) as doc:
        for pagina in doc:
            texto += pagina.get_text()
    return texto

#  Función para leer PDFs en subdirectorios
def leer_facturas_en_subdirectorios(ruta_base):
    datos_facturas = []
    for carpeta_raiz, _, archivos in os.walk(ruta_base):
        for archivo in archivos:
            if archivo.lower().endswith(".pdf"):
                ruta_pdf = os.path.join(carpeta_raiz, archivo)
                texto = extraer_texto_pdf(ruta_pdf)
                datos_facturas.append({
                    "ruta": ruta_pdf,
                    "texto": texto
                })
    return datos_facturas

#  Función para extraer datos clave del texto de la factura
def extraer_datos_factura(texto):
    texto = texto.replace('\n', ' ')  # Unificamos el texto para evitar cortes

    #  Monto total (después de "total" o "importe")
    monto = None
    monto_regex = re.findall(r"(total|importe)[^\d]{0,10}(\d{1,3}(?:[.,]\d{3})*[.,]\d{2})", texto, re.IGNORECASE)
    if monto_regex:
        monto = monto_regex[-1][1].replace(",", ".").replace(" ", "")

    #  Fecha (formato dd/mm/aaaa o similar)
    fecha = None
    fecha_regex = re.findall(r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b", texto)
    if fecha_regex:
        fecha = fecha_regex[0]

    #  Número de factura (donde aparece "factura" o "nº")
    nro_factura = None
    nro_regex = re.search(r"(factura|número|nº|n°)[^\w]{0,10}([a-zA-Z0-9\-]+)", texto, re.IGNORECASE)
    if nro_regex:
        nro_factura = nro_regex.group(2)

    #  Proveedor (lo extraemos del comienzo del texto)
    proveedor = texto.strip()[:50]  # Solo tomamos los primeros 50 caracteres, puedes ajustarlo

    #  Tipo: Ingreso o Gasto (si tiene "venta" o "ingreso" se clasifica como ingreso)
    texto_lower = texto.lower()
    if "venta" in texto_lower or "emitida" in texto_lower or "ingreso" in texto_lower:
        tipo = "Ingreso"
    else:
        tipo = "Gasto"

    return {
        "fecha": fecha,
        "monto": monto,
        "proveedor": proveedor,
        "nro_factura": nro_factura,
        "tipo": tipo
    }

#  Función para guardar los datos extraídos en un archivo CSV
def guardar_en_csv(datos, nombre_archivo="facturas_extraidas.csv"):
    # Definir los encabezados del CSV
    encabezados = ["Fecha", "Monto", "Proveedor", "Número de Factura", "Tipo"]
    
    # Abrir el archivo CSV en modo escritura
    with open(nombre_archivo, mode="w", newline="", encoding="utf-8") as archivo_csv:
        writer = csv.DictWriter(archivo_csv, fieldnames=encabezados)
        
        # Escribir los encabezados
        writer.writeheader()
        
        # Escribir los datos
        for factura in datos:
            writer.writerow({
                "Fecha": factura["fecha"],
                "Monto": factura["monto"],
                "Proveedor": factura["proveedor"],
                "Número de Factura": factura["nro_factura"],
                "Tipo": factura["tipo"]
            })

#  Ejecutar extracción y guardar en CSV
if __name__ == "__main__":
    ruta_facturas = "facturas"  # Cambiá si tus carpetas están en otro lugar
    datos = leer_facturas_en_subdirectorios(ruta_facturas)
    
    # Crear una lista para almacenar los datos extraídos
    facturas_extraidas = []

    for factura in datos:
        datos_extraidos = extraer_datos_factura(factura["texto"])
        
        # Solo agregamos datos si son relevantes
        facturas_extraidas.append(datos_extraidos)
    
    # Guardar los datos extraídos en un archivo CSV
    guardar_en_csv(facturas_extraidas)
    print(" Datos guardados en 'facturas_extraidas.csv'.")
