import asyncio
import httpx
from bs4 import BeautifulSoup
from datetime import datetime
import json

async def scrape_minsa_normas():
    url = "https://www.gob.pe/institucion/minsa/normas-legales"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    async with httpx.AsyncClient(verify=False) as client:
        try:
            print(f"Iniciando scraping de {url}")
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            
            print(f"Respuesta recibida. Status code: {response.status_code}")
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Encontrar todas las normas legales
            normas = soup.find_all('li', class_='hover:bg-gray-70')
            items = []
            
            for norma in normas:
                try:
                    # Extraer título y número de resolución
                    link = norma.find('a', class_='mb-2')
                    titulo = link.text.strip()
                    url_norma = f"https://www.gob.pe{link['href']}"
                    
                    # Extraer descripción
                    descripcion = norma.find('div', {'id': lambda x: x and x.startswith('p-filter-item-')})
                    descripcion = descripcion.text.strip() if descripcion else ""
                    
                    # Extraer fecha
                    fecha_str = norma.find('time')['datetime'].split()[0]  # "2024-12-06"
                    anio, mes, dia = map(int, fecha_str.split('-'))
                    fecha = datetime(anio, mes, dia)
                    
                    # Extraer URL del PDF
                    pdf_link = norma.find('a', class_='btn')['href'] if norma.find('a', class_='btn') else url_norma
                    
                    item = {
                        'title': titulo,
                        'description': descripcion,
                        'source_url': pdf_link,
                        'source_type': 'norma_legal',
                        'country': 'Perú',
                        'presentation_date': fecha,
                        'extra_data': json.dumps({
                            'url_detalle': url_norma,
                            'tipo': 'norma_legal_minsa'
                        })
                    }
                    items.append(item)
                    
                except Exception as e:
                    print(f"Error procesando norma legal: {e}")
                    continue
            
            print(f"Se encontraron {len(items)} normas legales")
            return items
            
        except Exception as e:
            print(f"Error en scraping de MINSA normas legales: {e}")
            return []

if __name__ == "__main__":
    asyncio.run(scrape_minsa_normas())
