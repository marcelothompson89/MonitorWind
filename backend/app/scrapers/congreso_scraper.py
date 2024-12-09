import httpx
from bs4 import BeautifulSoup
from datetime import datetime
import re

async def scrape_congreso():
    url = "https://comunicaciones.congreso.gob.pe/?s=&date=&post_type%5B%5D=noticias"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    async with httpx.AsyncClient(verify=False) as client:
        try:
            print(f"Iniciando scraping de {url}")
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            noticias = soup.find_all('div', class_='descripcion')
            
            if not noticias:
                print("No se encontraron noticias")
                return []
            
            items = []
            for noticia in noticias:
                try:
                    # Extraer título y URL
                    titulo_elem = noticia.find('p', class_='titulo-20').find('a')
                    titulo = titulo_elem.get_text(strip=True)
                    url = titulo_elem.get('href')
                    
                    # Extraer fecha
                    fecha_str = noticia.find('span', class_='parrafo-clock').get_text(strip=True)
                    # Formato: "05 Dic 2024 | 21:55 h"
                    fecha_match = re.search(r'(\d{2})\s+(\w+)\s+(\d{4})', fecha_str)
                    if fecha_match:
                        dia, mes, anio = fecha_match.groups()
                        meses = {'Ene': 1, 'Feb': 2, 'Mar': 3, 'Abr': 4, 'May': 5, 'Jun': 6, 
                                'Jul': 7, 'Ago': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dic': 12}
                        mes_num = meses.get(mes, 1)
                        fecha = datetime(int(anio), mes_num, int(dia))
                    else:
                        print(f"Error parseando fecha: {fecha_str}")
                        continue
                    
                    # Extraer descripción
                    descripcion = noticia.find('p', class_='parrafo-16')
                    descripcion_texto = descripcion.get_text(strip=True) if descripcion else ""
                    
                    item = {
                        'title': titulo,
                        'description': descripcion_texto,
                        'source_type': 'NOTICIAS',
                        'country': 'Perú',
                        'source_url': url,
                        'presentation_date': fecha,
                        'metadata': {
                            'fecha_completa': fecha_str
                        }
                    }
                    
                    items.append(item)
                    print(f"Item agregado: {titulo}")
                
                except Exception as e:
                    print(f"Error procesando noticia: {str(e)}")
                    continue
            
            return items
            
        except Exception as e:
            print(f"Error en scraping: {str(e)}")
            return []
