import asyncio
from datetime import datetime
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json

async def scrape_diputados_noticias():
    base_url = "https://www.camara.cl/cms/noticias/"
    items = []
    
    async with aiohttp.ClientSession() as session:
        async with session.get(base_url) as response:
            if response.status != 200:
                print(f"[Diputados Noticias Scraper] Error al obtener la página: {response.status}")
                return []
            
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')
            
            # Encontrar todos los módulos de noticias
            noticias = soup.find_all('div', class_='td_module_4')
            
            for noticia in noticias:
                try:
                    # Extraer el enlace y título
                    link_element = noticia.find('h3', class_='entry-title').find('a')
                    title = link_element['title']
                    url = link_element['href']
                    
                    # Extraer la descripción
                    description = noticia.find('div', class_='td-excerpt').text.strip()
                    
                    # Extraer la fecha
                    date_text = noticia.find('time', class_='entry-date')['datetime']
                    # Convertir el string ISO a objeto datetime
                    date = datetime.fromisoformat(date_text.replace('-03:00', '+00:00'))
                    
                    # Extraer categoría
                    category = noticia.find('a', class_='td-post-category')
                    category_text = category.text.strip() if category else "Sin categoría"
                    
                    # Extraer imagen
                    img = noticia.find('img', class_='entry-thumb')
                    img_url = img['src'] if img else None
                    
                    # Crear el objeto de noticia
                    item = {
                        "title": title,
                        "description": description,
                        "source_url": url,
                        "source_type": "noticia",
                        "country": "Chile",
                        "presentation_date": date,  # Ahora es un objeto datetime
                        "extra_data": json.dumps({
                            "category": category_text,
                            "image_url": img_url
                        })
                    }
                    
                    items.append(item)
                    
                except Exception as e:
                    print(f"[Diputados Noticias Scraper] Error procesando noticia: {str(e)}")
                    continue
    
    print(f"[Diputados Noticias Scraper] Se encontraron {len(items)} noticias")
    return items

if __name__ == "__main__":
    asyncio.run(scrape_diputados_noticias())
