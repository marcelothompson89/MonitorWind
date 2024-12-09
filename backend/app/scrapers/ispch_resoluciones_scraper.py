import asyncio
import httpx
from bs4 import BeautifulSoup
from datetime import datetime
import json

async def scrape_ispch_resoluciones():
    url = "https://www.ispch.gob.cl/resoluciones/"
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
            
            # Encontrar todas las resoluciones en la tabla
            resoluciones = soup.find_all('tr')
            items = []
            
            for resolucion in resoluciones[1:]:  # Skip header row
                try:
                    cols = resolucion.find_all('td')
                    if len(cols) < 4:
                        continue
                        
                    numero = cols[0].text.strip()
                    link_element = cols[1].find('a')
                    titulo = link_element.text.strip()
                    url = link_element['href']
                    
                    # Extraer fecha
                    fecha_str = cols[2].text.strip()  # "08-11-2024"
                    dia, mes, anio = map(int, fecha_str.split('-'))
                    fecha = datetime(anio, mes, dia)
                    
                    # Extraer categoría
                    categoria = cols[3].text.strip()
                    
                    item = {
                        'title': f"Resolución N° {numero}: {titulo}",
                        'description': titulo,
                        'source_url': url,
                        'source_type': 'resolucion',
                        'country': 'Chile',
                        'presentation_date': fecha,
                        'extra_data': json.dumps({
                            'numero_resolucion': numero,
                            'categoria': categoria,
                            'tipo': 'resolucion_ispch'
                        })
                    }
                    items.append(item)
                    
                except Exception as e:
                    print(f"Error procesando resolución: {e}")
                    continue
            
            print(f"Se encontraron {len(items)} resoluciones")
            return items
            
        except Exception as e:
            print(f"Error en scraping de ISPCH resoluciones: {e}")
            return []

if __name__ == "__main__":
    asyncio.run(scrape_ispch_resoluciones())
