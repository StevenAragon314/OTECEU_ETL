# manejo_datos.py

import pandas as pd
from nltk.corpus import stopwords
from function.constantes import MESES, KEY_WORDS
from function.procesamiento_texto import text_reduce

def replace_date(date: str) -> str:
    """
    Cambia fechas con el formato 'día (número) mes (palabras) año (número)' a 'día-mes-número-año'.

    Args:
        date (str): Fecha en formato 'día mes año', por ejemplo, '01 ene 2023'.

    Returns:
        str: Fecha en formato 'dd-mm-yyyy' a '01-1-2023'.
    """
    day, month, year = date.split(" ")
    return f'{day}-{MESES[month]}-{year}'

def save_data(
    id_proyecto: list,
    titulo_articulo: list,
    resumen_art: list,
    fecha_publicacion: list,
    autor_redacta: list,
    imagen_url: list,
    notice_url: list,
    notice_completa: list,
    change_date: pd.to_datetime) -> pd.DataFrame:
    """
    Crea un DataFrame a partir de las listas proporcionadas, procesa las fechas y reduce el texto.

    Args:
        id_proyecto (List): Lista de IDs de proyectos.
        titulo_articulo (List): Lista de títulos de artículos.
        resumen_art (List): Lista de resúmenes de artículos.
        fecha_publicacion (List): Lista de fechas de publicación.
        autor_redacta (List): Lista de autores.
        imagen_url (List): Lista de URLs de imágenes.
        notice_url (List): Lista de URLs de noticias.
        notice_completa (List): Lista de noticias completas.
        list_date (List): Lista de fechas a procesar.

    Returns:
        pd.DataFrame: DataFrame procesado con las columnas especificadas.
    """
    
    # Palabras clave y stopwords
    stopwords_set = list(set(stopwords.words("spanish")).union({
        'rodríguez', '”', '©', "universidad", "ucr", "costa", "rica",
        "educación", "2024", "espacio", "años", "universidades",
        "foto"
    }))

    # Procesar las fechas
    date_change = [replace_date(date) for date in change_date]

    # Crear el diccionario de datos
    data_dict = {
        'id_atributo': id_proyecto,
        'titulo_articulo': titulo_articulo,
        'resumen_art': resumen_art,
        'fecha_publicacion': fecha_publicacion,
        'autor_redacta': autor_redacta,
        'imagen_url': imagen_url,
        'notice_url': notice_url,
        'noticia_completa': notice_completa,
        'fecha_publicacion_CD': date_change
    }

    df = pd.DataFrame(data_dict)

    # Procesar y añadir la columna 'n_by_tex'
    df['n_by_tex'] = text_reduce(
        df=df,
        col="noticia_completa",
        stopwords_list= stopwords_set,
        key_words= KEY_WORDS
    )

    df["fecha_publicacion_CD"] =  pd.to_datetime(df["fecha_publicacion_CD"], format="%d-%m-%Y")

    df.sort_values(by = "fecha_publicacion_CD", ascending= False, inplace= True)
    df.reset_index(drop= True, inplace= True)

    return df