import os
from bs4 import BeautifulSoup as bs
import pandas as pd
from urllib.parse import urljoin
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import time
import random
from function.manejo_datos import save_data

# Modulos de function
from function.manejo_datos import save_data
from function.utilidades import quitar_tildes
from function.constantes import TEXTO_BASURA

def scrape_data(df_path): 
    try:
        df_historico = pd.read_csv(df_path)
    except FileNotFoundError:
        print(f"No se encontró el archivo {df_path}. Iniciando con un DataFrame vacío.")
        df_historico = pd.DataFrame(columns=[
            'id_atributo', 'titulo_articulo', 'resumen_art', 'fecha_publicacion',
            'autor_redacta', 'imagen_url', 'notice_url', 'notice_completa'
        ])
    except Exception as e:
        print(f"Error al leer el archivo CSV: {e}")
        return

    try:
        df_historico["fecha_publicacion_CD"] = pd.to_datetime(df_historico["fecha_publicacion_CD"])
        last_date = df_historico["fecha_publicacion_CD"].max()
        last_id = df_historico["id_atributo"].max()
    except (KeyError, IndexError):
        print("No hay datos previos. Iniciando desde el principio.")
        last_date, last_id = None, 0

    # Configuración del driver Selenium
    options = Options()
    options.add_argument("--headless")  # Ejecución en segundo plano -que no aparezca la ventana-

    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    except Exception as e:
        print(f"Error al inicializar Selenium: {e}")
        return

    base_url = "https://www.ucr.ac.cr"
    x = 3  # Número de páginas a recorrer -para evitar sobrecarga-
    add = len(df_historico) + 1

    # Listas para almacenar los datos recolectados
    id_proyecto, titulo_articulo, resumen_art = [], [], []
    fecha_publicacion, autor_redacta, imagen_url, notice_url, notice_completa = [], [], [], [], []

    detener = False  # detener toda la carga de datos

    try:
        for i in range(1, x + 1):
            if detener:
                print("Detención activada. Saliendo del bucle de páginas.")
                break  # Salir del bucle de páginas

            driver.get(f"{base_url}/noticias/?pagina={i}")
            WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "noticia")))

            soup = bs(driver.page_source, 'html.parser')
            noticias = soup.find_all("div", class_="noticia item tarjeta")

            for notice in noticias:
                if detener:
                    print("Detención activada. Saliendo del bucle de noticias.")
                    break  # Salir del bucle de noticias

                enlace = notice.find("a", class_='marco')
                if not enlace:
                    continue

                fecha_ = notice.find("span", class_='dia')
                fecha_text = fecha_.text.strip() if fecha_ else ""

                # Detener el scraping si se encuentra la fecha límite
                if last_date and fecha_text == last_date:
                    print("Fecha límite encontrada. Deteniendo scraping.")
                    detener = True
                    break  # Salir del bucle de noticias

                titulo_articulo.append(enlace.text.strip())
                fecha_publicacion.append(fecha_text)
                resumen_ = notice.find("p", class_='resumen')
                resumen_art.append(resumen_.text.strip() if resumen_ else "Sin resumen")

                imagen = notice.find("img")
                imagen_url.append(imagen['src'] if imagen else None)

                autor = notice.find("div", class_='autores')
                autor_redacta.append(autor.text.strip() if autor else "Desconocido")

                noticia_url = urljoin(base_url, enlace.get("href"))
                notice_url.append(noticia_url)

                # Cargar contenido completo de la noticia
                try:
                    driver.get(noticia_url)
                    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.TAG_NAME, "p")))
                    contenido_completo = ' '.join([p.text for p in bs(driver.page_source, "html.parser").find_all("p")])
                    notice_completa.append(contenido_completo.replace("TEXTO_BASURA", "").strip())
                except Exception as e:
                    print(f"Error al cargar el contenido completo de la noticia: {e}")
                    notice_completa.append("Contenido no disponible")

                id_proyecto.append(f'{add:06}')
                add += 1

                time.sleep(random.uniform(1, 3))  # Pausa para evitar bloqueos

    except Exception as e:
        print(f"Error en la página {i}: {e}")

    finally:
        driver.quit()

    # Guardar los datos recolectados
    try:
        id_proyecto = [int(last_id) + int(n) for n in id_proyecto]

        df_nuevo = save_data(
            id_proyecto = id_proyecto,
            titulo_articulo = titulo_articulo,
            resumen_art = resumen_art,
            fecha_publicacion = fecha_publicacion,
            autor_redacta = autor_redacta,
            imagen_url = imagen_url,
            notice_url = notice_url,
            notice_completa = notice_completa,
            change_date = fecha_publicacion
        )

        df_nuevo.to_csv(df_path, mode='a', header=not os.path.exists(df_path), index=False)
        
        print("Scraping completado y datos guardados.")
    except Exception as e:
        print(f"Error al guardar los datos: {e}")

    print("Scraping completado exitosamente.")