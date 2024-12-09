import asyncio
import httpx
from bs4 import BeautifulSoup
from datetime import datetime
import json

async def scrape_ispch_noticias():
    url = "https://www.ispch.gob.cl/noticia/"
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
            
            # Encontrar todas las noticias
            noticias = soup.find_all('div', class_='')
            items = []
            
            for noticia in noticias:
                try:
                    link = noticia.find('a', class_='link-search')
                    if not link:
                        continue
                        
                    # Extraer título
                    title = link.find('h4').text.strip()
                    
                    # Extraer URL
                    url = link['href']
                    
                    # Extraer fecha
                    fecha_str = link.find('time').text.strip()  # "2 diciembre, 2024"
                    # Convertir mes a número
                    meses = {
                        'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4, 'mayo': 5, 'junio': 6,
                        'julio': 7, 'agosto': 8, 'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
                    }
                    dia, mes, anio = fecha_str.replace(',', '').split()
                    mes_num = meses[mes.lower()]
                    fecha = datetime(int(anio), mes_num, int(dia))
                    
                    # Extraer descripción
                    description = link.find('p').text.strip()
                    
                    # Crear el objeto de la noticia
                    item = {
                        "title": title,
                        "description": description,
                        "source_url": url,
                        "source_type": "noticia",
                        "country": "Chile",
                        "presentation_date": fecha,
                        "extra_data": json.dumps({
                            "tipo": "Noticia ISPCH"
                        })
                    }
                    
                    items.append(item)
                    print(f"Guardando nuevo item: {title} - País: Chile")
                    print(f"Fecha: {fecha.isoformat()}")
                    print(f"URL: {url}")
                    
                except Exception as e:
                    print(f"[ISPCH Noticias Scraper] Error procesando noticia: {str(e)}")
                    continue
            
            print(f"[ISPCH Noticias Scraper] Se encontraron {len(items)} noticias")
            return items
            
        except Exception as e:
            print(f"Error scraping ISPCH Noticias: {str(e)}")
            if 'response' in locals():
                print(f"Status code: {response.status_code}")
                print(f"Response text: {response.text[:500]}")
            return []

if __name__ == "__main__":
    asyncio.run(scrape_ispch_noticias())
