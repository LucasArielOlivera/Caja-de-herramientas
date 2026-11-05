"""
imprimir_facturas.py
====================
Toma la página 1 de cada PDF que haya en una carpeta y genera un único PDF
combinado listo para imprimir. Opcionalmente lo envía directo a la impresora.

Uso:
    python imprimir_facturas.py                      # usa la carpeta actual
    python imprimir_facturas.py C:\\Facturas\\Junio   # carpeta específica
    python imprimir_facturas.py --imprimir           # abre el diálogo de impresión
    python imprimir_facturas.py C:\\Facturas --imprimir

Requisitos:
    pip install pypdf
"""

import sys
import os
import glob
import subprocess
import platform
from pathlib import Path

try:
    from pypdf import PdfReader, PdfWriter
except ImportError:
    print("ERROR: Falta la librería pypdf.")
    print("Instalala con:  pip install pypdf")
    sys.exit(1)


# ── Configuración ──────────────────────────────────────────────────────────────

NOMBRE_SALIDA = "FACTURAS_pagina1.pdf"   # nombre del PDF combinado que se genera


# ── Funciones principales ──────────────────────────────────────────────────────

def obtener_pdfs(carpeta: Path) -> list[Path]:
    """Devuelve todos los PDFs de la carpeta, ordenados por nombre."""
    archivos = sorted(carpeta.glob("*.pdf"))
    # Excluir el archivo de salida si ya existe en la misma carpeta
    archivos = [f for f in archivos if f.name != NOMBRE_SALIDA]
    return archivos


def combinar_primera_pagina(pdfs: list[Path], salida: Path) -> int:
    """
    Extrae la página 1 de cada PDF y las une en un solo archivo.
    Devuelve la cantidad de páginas incluidas.
    """
    writer = PdfWriter()
    incluidos = 0
    omitidos = []

    for pdf_path in pdfs:
        try:
            reader = PdfReader(str(pdf_path))
            if len(reader.pages) == 0:
                omitidos.append((pdf_path.name, "PDF vacío"))
                continue
            writer.add_page(reader.pages[0])
            incluidos += 1
            print(f"  ✓  {pdf_path.name}")
        except Exception as e:
            omitidos.append((pdf_path.name, str(e)))
            print(f"  ✗  {pdf_path.name}  →  {e}")

    if incluidos == 0:
        return 0

    with open(salida, "wb") as f:
        writer.write(f)

    if omitidos:
        print(f"\n⚠  Se omitieron {len(omitidos)} archivo(s) con errores:")
        for nombre, motivo in omitidos:
            print(f"   - {nombre}: {motivo}")

    return incluidos


def abrir_para_imprimir(ruta: Path, imprimir_directo: bool) -> None:
    """
    Abre el PDF combinado.
    - imprimir_directo=True  → envía a la impresora predeterminada sin abrir visor
    - imprimir_directo=False → abre el visor PDF para que el usuario imprima manualmente
    """
    sistema = platform.system()

    if sistema == "Windows":
        if imprimir_directo:
            # Envía a la impresora predeterminada usando el verbo "print"
            os.startfile(str(ruta), "print")
            print("\n🖨  Enviado a la impresora predeterminada.")
        else:
            # Abre el visor PDF (Adobe, Edge, etc.)
            os.startfile(str(ruta))
            print("\n📄  PDF abierto en el visor. Usá Ctrl+P para imprimir.")

    elif sistema == "Darwin":  # macOS
        if imprimir_directo:
            subprocess.run(["lp", str(ruta)], check=False)
            print("\n🖨  Enviado a la impresora predeterminada (lp).")
        else:
            subprocess.run(["open", str(ruta)], check=False)
            print("\n📄  PDF abierto. Usá Cmd+P para imprimir.")

    else:  # Linux
        if imprimir_directo:
            subprocess.run(["lp", str(ruta)], check=False)
            print("\n🖨  Enviado a la impresora predeterminada (lp).")
        else:
            for visor in ["evince", "okular", "xdg-open"]:
                if subprocess.run(["which", visor], capture_output=True).returncode == 0:
                    subprocess.Popen([visor, str(ruta)])
                    break
            print("\n📄  PDF abierto. Imprimí desde el visor.")


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    # Parsear argumentos simples (sin argparse para no añadir dependencias)
    args = sys.argv[1:]
    imprimir_directo = "--imprimir" in args
    args = [a for a in args if not a.startswith("--")]

    # Determinar carpeta
    if args:
        carpeta = Path(args[0])
    else:
        carpeta = Path.cwd()

    if not carpeta.is_dir():
        print(f"ERROR: La carpeta no existe: {carpeta}")
        sys.exit(1)

    carpeta = carpeta.resolve()
    salida = carpeta / NOMBRE_SALIDA

    print(f"\n{'='*55}")
    print(f"  Carpeta:  {carpeta}")
    print(f"  Salida:   {salida.name}")
    print(f"{'='*55}\n")

    # Buscar PDFs
    pdfs = obtener_pdfs(carpeta)
    if not pdfs:
        print("No se encontraron archivos PDF en la carpeta.")
        sys.exit(0)

    print(f"Se encontraron {len(pdfs)} PDF(s). Procesando...\n")

    # Combinar
    total = combinar_primera_pagina(pdfs, salida)

    if total == 0:
        print("\nNo se pudo procesar ningún PDF.")
        sys.exit(1)

    print(f"\n✅  PDF combinado generado: {salida}")
    print(f"   {total} página(s) incluida(s).\n")

    # Abrir / imprimir
    abrir_para_imprimir(salida, imprimir_directo)
    print()


if __name__ == "__main__":
    main()
