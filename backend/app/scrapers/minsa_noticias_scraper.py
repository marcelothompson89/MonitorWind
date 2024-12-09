import asyncio
import httpx
from bs4 import BeautifulSoup
from datetime import datetime
import json

async def scrape_minsa_noticias():
    url = "https://www.gob.pe/institucion/minsa/noticias"
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
            noticias = soup.find_all('li', class_='scrollable__item')
            items = []
            
            for noticia in noticias:
                try:
                    # Extraer título y URL
                    link = noticia.find('a', class_='text-primary')
                    titulo = link.text.strip()
                    url_noticia = f"https://www.gob.pe{link['href']}"
                    
                    # Extraer imagen
                    img = noticia.find('img')
                    img_url = img['src'] if img else None
                    img_alt = img['alt'] if img else None
                    
                    # Extraer fecha
                    fecha_str = noticia.find('time')['datetime']  # "2024-12-07 08:29:00.000"
                    fecha = datetime.strptime(fecha_str, "%Y-%m-%d %H:%M:%S.%f")
                    
                    # Extraer descripción (si existe)
                    descripcion_div = noticia.find('div', class_='flex-1')
                    descripcion = descripcion_div.text.strip() if descripcion_div else img_alt or titulo
                    
                    item = {
                        'title': titulo,
                        'description': descripcion,
                        'source_url': url_noticia,
                        'source_type': 'noticia',
                        'country': 'Perú',
                        'presentation_date': fecha,
                        'extra_data': json.dumps({
                            'imagen_url': img_url,
                            'imagen_alt': img_alt,
                            'tipo': 'noticia_minsa'
                        })
                    }
                    items.append(item)
                    
                except Exception as e:
                    print(f"Error procesando noticia: {e}")
                    continue
            
            print(f"Se encontraron {len(items)} noticias")
            return items
            
        except Exception as e:
            print(f"Error en scraping de MINSA noticias: {e}")
            return []

if __name__ == "__main__":
    asyncio.run(scrape_minsa_noticias())
