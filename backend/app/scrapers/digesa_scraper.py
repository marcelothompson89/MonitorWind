import asyncio
from datetime import datetime
import re
from bs4 import BeautifulSoup
import aiohttp
from urllib.parse import urljoin
import json

async def scrape_digesa():
    print("[DIGESA Scraper] Iniciando scraping...")
    
    # URL base de DIGESA
    base_url = "http://www.digesa.minsa.gob.pe/noticias/comunicados.asp"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(base_url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Buscar el encabezado de 2024
                    header_2024 = soup.find('h4', string='Comunicados 2024')
                    if not header_2024:
                        print("[DIGESA Scraper] No se encontró la sección de comunicados 2024")
                        return []
                    
                    items = []
                    # Obtener todos los enlaces después del encabezado hasta el siguiente h4
                    current = header_2024.find_next()
                    while current and current.name != 'h4':
                        if current.name == 'a':
                            href = current.get('href')
                            if href and ('.pdf' in href.lower() or 'comunicado' in href.lower()):
                                texto = current.text.strip()
                                fecha_match = re.search(r'(\d{2})[./](\d{2})[./](\d{4})', texto)
                                
                                try:
                                    if fecha_match:
                                        dia, mes, anio = fecha_match.groups()
                                        fecha = datetime.strptime(f"{anio}-{mes}-{dia}", "%Y-%m-%d")
                                    else:
                                        fecha = datetime.utcnow()
                                    
                                    # Construir URL completa del PDF
                                    pdf_url = urljoin(base_url, href)
                                    
                                    metadata = {
                                        'tipo': 'comunicado',
                                        'institucion': 'DIGESA',
                                        'año': '2024',
                                        'pais': 'Perú'
                                    }
                                    
                                    item = {
                                        'title': texto,
                                        'description': texto,
                                        'country': 'Perú',
                                        'source_url': pdf_url,
                                        'source_type': 'DIGESA',
                                        'presentation_date': fecha,
                                        'extra_data': json.dumps(metadata)
                                    }
                                    items.append(item)
                                except Exception as e:
                                    print(f"[DIGESA Scraper] Error procesando item: {str(e)}")
                                    continue
                        current = current.find_next()
                    
                    print(f"[DIGESA Scraper] Se encontraron {len(items)} comunicados de 2024")
                    return items
                else:
                    print(f"[DIGESA Scraper] Error al acceder a la página: {response.status}")
                    return []
                    
    except Exception as e:
        print(f"[DIGESA Scraper] Error durante el scraping: {str(e)}")
        return []

if __name__ == "__main__":
    asyncio.run(scrape_digesa())
