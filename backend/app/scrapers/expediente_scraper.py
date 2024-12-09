import asyncio
from datetime import datetime
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

async def scrape_expediente():
    print("[Expediente Scraper] Iniciando scraping con Selenium...")
    
    # Configurar opciones de Chrome
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--disable-notifications')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-infobars')
    
    # Configurar el servicio de Chrome
    service = Service(r'C:\SeleniumDrivers\chromedriver.exe')
    
    try:
        print("[Expediente Scraper] Iniciando navegador...")
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.set_page_load_timeout(30)  # 30 segundos timeout para cargar la página
        
        # URL del portal de expedientes
        url = "https://wb2server.congreso.gob.pe/spley-portal/#/expediente/search"
        print(f"[Expediente Scraper] Accediendo a URL: {url}")
        
        # Acceder a la página
        driver.get(url)
        
        # Esperar a que se cargue la página
        print("[Expediente Scraper] Esperando que se cargue la página...")
        wait = WebDriverWait(driver, 30)  # Aumentado a 30 segundos
        
        # Intentar diferentes selectores para detectar cuando la página esté cargada
        try:
            print("[Expediente Scraper] Buscando tabla...")
            table = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table.mat-table")))
        except TimeoutException:
            print("[Expediente Scraper] No se encontró tabla.mat-table, intentando otro selector...")
            try:
                table = wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
            except TimeoutException:
                print("[Expediente Scraper] No se encontró ninguna tabla, intentando buscar contenedor...")
                try:
                    container = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "mat-table-container")))
                    print("[Expediente Scraper] Contenedor encontrado, esperando datos...")
                except TimeoutException:
                    raise TimeoutException("No se pudo encontrar ningún elemento de la tabla")
        
        # Esperar un momento adicional para que se carguen los datos
        print("[Expediente Scraper] Esperando que se carguen los datos...")
        time.sleep(10)
        
        # Imprimir el HTML para debug
        print("[Expediente Scraper] HTML de la página:")
        print(driver.page_source[:1000])  # Primeros 1000 caracteres
        
        # Intentar diferentes selectores para las filas
        print("[Expediente Scraper] Buscando filas de la tabla...")
        rows = []
        selectors = [
            "table.mat-table tbody tr",
            "table tbody tr",
            ".mat-row",
            "tr.mat-row"
        ]
        
        for selector in selectors:
            print(f"[Expediente Scraper] Intentando selector: {selector}")
            rows = driver.find_elements(By.CSS_SELECTOR, selector)
            if rows:
                print(f"[Expediente Scraper] Encontradas {len(rows)} filas con selector {selector}")
                break
        
        if not rows:
            print("[Expediente Scraper] No se encontraron filas en la tabla")
            return []
        
        items = []
        for row in rows:
            try:
                # Extraer el href y construir la URL
                link_element = row.find_element(By.CSS_SELECTOR, "a.link-proyecto-acumulado")
                href = link_element.get_attribute("href")
                print(f"\n[DEBUG] HTML del link: {link_element.get_attribute('outerHTML')}")
                print(f"[DEBUG] href extraído: {href}")
                
                # Construir la URL base
                base_url = "https://wb2server.congreso.gob.pe/spley-portal/#"
                
                # Si el href empieza con #, quitarlo
                if href and href.startswith('#'):
                    path = href[1:]
                else:
                    path = href if href else '/'
                
                # Construir URL final
                source_url = f"{base_url}{path}"
                print(f"[DEBUG] URL final: {source_url}")
                
                # Extraer información básica
                numero = link_element.text.strip()
                fecha_str = row.find_element(By.CSS_SELECTOR, "td:nth-child(2)").text.strip()
                titulo = row.find_element(By.CSS_SELECTOR, "td:nth-child(3) span.ellipsis").text.strip()
                estado = row.find_element(By.CSS_SELECTOR, "td:nth-child(4)").text.strip()
                proponente = row.find_element(By.CSS_SELECTOR, "td:nth-child(5)").text.strip()
                
                print(f"[Expediente Scraper] Datos extraídos:")
                print(f"  - Número: {numero}")
                print(f"  - Fecha: {fecha_str}")
                print(f"  - Título: {titulo[:100]}...")
                print(f"  - Estado: {estado}")
                print(f"  - Proponente: {proponente}")
                print(f"  - Link original: {source_url}")
                
                # Convertir fecha
                try:
                    fecha = datetime.strptime(fecha_str, '%d/%m/%Y')
                except ValueError:
                    print(f"[Expediente Scraper] Error al parsear fecha: {fecha_str}")
                    continue
                
                # Crear descripción
                descripcion = f"Número: {numero}\n"
                descripcion += f"Estado: {estado}\n"
                descripcion += f"Proponente: {proponente}"
                
                item = {
                    'title': titulo,
                    'description': descripcion,
                    'source_type': 'PROYECTO_LEY',
                    'country': 'Perú',
                    'source_url': source_url,
                    'presentation_date': fecha,
                    'metadata': {
                        'numero_expediente': numero,
                        'estado': estado,
                        'proponente': proponente,
                        'periodo': '2021-2026'
                    }
                }
                
                items.append(item)
                print(f"[Expediente Scraper] Item agregado: {item['title'][:100]}...")
            
            except Exception as e:
                print(f"[Expediente Scraper] Error procesando fila: {str(e)}")
                continue
        
        print(f"[Expediente Scraper] Total de items procesados: {len(items)}")
        return items
        
    except TimeoutException as e:
        print(f"[Expediente Scraper] Timeout: {str(e)}")
        return []
        
    except Exception as e:
        print(f"[Expediente Scraper] Error en scraping: {str(e)}")
        return []
        
    finally:
        try:
            driver.quit()
            print("[Expediente Scraper] Navegador cerrado")
        except:
            pass
