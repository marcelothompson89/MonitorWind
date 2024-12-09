import httpx
from bs4 import BeautifulSoup
from datetime import datetime
import re

async def scrape_anamed():
    url = "https://www.ispch.gob.cl/categorias-alertas/anamed/"
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
            
            # Encontrar la tabla de alertas
            table = soup.find('table')
            if not table:
                print("No se encontró ninguna tabla en la página")
                print("HTML recibido:", response.text[:500])  # Primeros 500 caracteres
                return []
            
            rows = table.find_all('tr')[1:]  # Ignorar la fila de encabezado
            print(f"Se encontraron {len(rows)} filas en la tabla")
            items = []
            
            for row in rows:
                cols = row.find_all('td')
                if len(cols) < 5:
                    print(f"Fila ignorada por tener menos de 5 columnas: {len(cols)}")
                    continue
                
                # Extraer enlaces
                links_col = cols[4]
                alerta_link = links_col.find('a', text=re.compile('Alerta', re.I))
                nota_link = links_col.find('a', text=re.compile('Nota', re.I))
                publicacion_link = links_col.find('a', text=re.compile('Publicación', re.I))
                
                # Convertir fecha al formato correcto
                fecha_str = cols[0].get_text(strip=True)
                try:
                    fecha = datetime.strptime(fecha_str, '%d-%m-%Y')
                except ValueError as e:
                    print(f"Error al parsear fecha '{fecha_str}': {str(e)}")
                    continue
                
                item = {
                    'title': cols[3].get_text(strip=True),
                    'description': cols[3].get_text(strip=True),
                    'source_type': cols[1].get_text(strip=True),
                    'category': cols[2].get_text(strip=True),
                    'country': 'Chile',
                    'source_url': alerta_link.get('href') if alerta_link else None,
                    'presentation_date': fecha,
                    'metadata': {
                        'nota_url': nota_link.get('href') if nota_link else None,
                        'publicacion_url': publicacion_link.get('href') if publicacion_link else None
                    }
                }
                
                items.append(item)
                print(f"Item agregado: {item['title']}")
            
            print(f"Total de items encontrados: {len(items)}")
            return items
            
        except Exception as e:
            print(f"Error scraping ISPCH: {str(e)}")
            if 'response' in locals():
                print(f"Status code: {response.status_code}")
                print(f"Response text: {response.text[:500]}")
            return []
