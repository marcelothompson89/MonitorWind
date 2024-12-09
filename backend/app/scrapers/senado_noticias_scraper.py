import asyncio
import httpx
from bs4 import BeautifulSoup
from datetime import datetime
import json
import re

async def scrape_senado_noticias():
    url = "https://www.senado.cl/comunicaciones/noticias"
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
            noticias = soup.find_all('a', class_='card')
            items = []
            urls_procesadas = set()  # Set para trackear URLs ya procesadas
            
            for noticia in noticias:
                try:
                    # Extraer URL
                    url_noticia = f"https://www.senado.cl{noticia['href']}"
                    
                    # Saltar si ya procesamos esta URL
                    if url_noticia in urls_procesadas:
                        continue
                    
                    urls_procesadas.add(url_noticia)
                    
                    # Extraer título
                    titulo = noticia.find('h3', class_='subtitle').text.strip()
                    
                    # Extraer categoría
                    categorias_div = noticia.find('div', class_='categorias')
                    categorias = [cat.text.strip() for cat in categorias_div.find_all('p')] if categorias_div else []
                    categoria = categorias[0] if categorias else "General"
                    
                    # Extraer fecha del contenido
                    fecha = None
                    
                    try:
                        # Hacer una petición a la página de la noticia
                        response_noticia = await client.get(url_noticia, headers=headers)
                        response_noticia.raise_for_status()
                        soup_noticia = BeautifulSoup(response_noticia.text, 'html.parser')
                        
                        # Buscar la fecha en el contenido
                        fecha_element = soup_noticia.find('p', class_='color-blue-75')
                        if fecha_element:
                            fecha_str = fecha_element.text.strip()
                            # Convertir mes a número
                            meses = {
                                'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4, 'mayo': 5, 'junio': 6,
                                'julio': 7, 'agosto': 8, 'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
                            }
                            patron = r'(\d+) de (\w+) de (\d+)'
                            match = re.search(patron, fecha_str)
                            if match:
                                dia, mes, anio = match.groups()
                                mes_num = meses[mes.lower()]
                                fecha = datetime(int(anio), mes_num, int(dia))
                        
                        # Si no se encuentra en el primer intento, buscar en otros elementos
                        if not fecha:
                            fecha_element = soup_noticia.find('time')
                            if fecha_element:
                                fecha_str = fecha_element.text.strip()
                                match = re.search(patron, fecha_str)
                                if match:
                                    dia, mes, anio = match.groups()
                                    mes_num = meses[mes.lower()]
                                    fecha = datetime(int(anio), mes_num, int(dia))
                    except Exception as e:
                        print(f"Error obteniendo fecha de la noticia {url_noticia}: {e}")
                    
                    if not fecha:
                        print(f"No se pudo extraer la fecha para la noticia: {titulo}")
                        continue
                    
                    # Extraer imagen
                    img = noticia.find('img')
                    img_src = None
                    if img:
                        srcset = img.get('srcset', '')
                        # Extraer la URL de mayor resolución del srcset
                        urls = re.findall(r'(https://[^\s]+)', srcset)
                        img_src = urls[-1] if urls else img.get('src', '')
                        if img_src.startswith('/_next'):
                            img_src = None
                    
                    item = {
                        'title': titulo,
                        'description': f"[{categoria}] {titulo}",
                        'source_url': url_noticia,
                        'source_type': 'noticia',
                        'country': 'Chile',
                        'presentation_date': fecha,
                        'extra_data': json.dumps({
                            'categoria': categoria,
                            'imagen_url': img_src,
                            'tipo': 'noticia_senado'
                        })
                    }
                    items.append(item)
                    
                except Exception as e:
                    print(f"Error procesando noticia: {e}")
                    continue
            
            print(f"Se encontraron {len(items)} noticias")
            return items
            
        except Exception as e:
            print(f"Error en scraping de Senado noticias: {e}")
            return []

if __name__ == "__main__":
    asyncio.run(scrape_senado_noticias())
