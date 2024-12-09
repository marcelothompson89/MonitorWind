import asyncio
from datetime import datetime
import aiohttp
from bs4 import BeautifulSoup
import json
import re

async def scrape_diputados_proyectos():
    base_url = "https://www.camara.cl/legislacion/ProyectosDeLey/proyectos_ley.aspx"
    items = []
    
    async with aiohttp.ClientSession() as session:
        async with session.get(base_url) as response:
            if response.status != 200:
                print(f"[Diputados Proyectos Scraper] Error al obtener la página: {response.status}")
                return []
            
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')
            
            # Encontrar todos los proyectos
            proyectos = soup.find_all('article', class_='proyecto')
            
            for proyecto in proyectos:
                try:
                    # Extraer número de boletín
                    numero = proyecto.find('span', class_='numero').text.strip()
                    
                    # Extraer tipo de proyecto
                    tipo_proyecto = proyecto.find('ul', class_='etapas-legislativas').find_all('li')[1].text.strip()
                    
                    # Extraer título y URL
                    link = proyecto.find('h3').find('a')
                    title = link.text.strip()
                    url = f"https://www.camara.cl/legislacion/ProyectosDeLey/{link['href']}"
                    
                    # Extraer fecha
                    fecha_str = proyecto.find('span', class_='fecha').text.strip()  # "04 Dic. 2024"
                    # Convertir mes abreviado a número
                    meses = {
                        'Ene.': 1, 'Feb.': 2, 'Mar.': 3, 'Abr.': 4, 'May.': 5, 'Jun.': 6,
                        'Jul.': 7, 'Ago.': 8, 'Sep.': 9, 'Oct.': 10, 'Nov.': 11, 'Dic.': 12
                    }
                    dia, mes, anio = fecha_str.split()
                    mes_num = meses[mes]
                    fecha = datetime(int(anio), mes_num, int(dia))
                    
                    # Extraer estado
                    estado = proyecto.find_all('ul', class_='etapas-legislativas')[1].find_all('li')[1].text.strip()
                    
                    # Crear el objeto del proyecto
                    item = {
                        "title": f"Proyecto de Ley {numero}: {title}",
                        "description": f"Tipo: {tipo_proyecto}. Estado: {estado}. {title}",
                        "source_url": url,
                        "source_type": "proyecto_ley",
                        "country": "Chile",
                        "presentation_date": fecha,
                        "extra_data": json.dumps({
                            "numero_boletin": numero,
                            "tipo_proyecto": tipo_proyecto,
                            "estado": estado
                        })
                    }
                    
                    items.append(item)
                    
                except Exception as e:
                    print(f"[Diputados Proyectos Scraper] Error procesando proyecto: {str(e)}")
                    continue
    
    print(f"[Diputados Proyectos Scraper] Se encontraron {len(items)} proyectos")
    return items

if __name__ == "__main__":
    asyncio.run(scrape_diputados_proyectos())
