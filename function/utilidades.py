# utilidades.py

import unicodedata
import re

def word_tokenize(text: str) -> list:
    """
    Tokeniza una cadena de texto utilizando expresiones regulares.

    Args:
        text (str): Cadena de texto a tokenizar.

    Returns:
        list: Lista de tokens.
    """
    return re.findall(r'\w+|[¿?!¡"]', text)

def quitar_tildes(texto: str) -> str:
    """
    Elimina las tildes (acentos) de una cadena de texto.

    Args:
        texto (str): La cadena de texto de la cual se eliminarán las tildes.

    Returns:
        str: La cadena de texto sin tildes.
    """
    texto_normalizado = unicodedata.normalize('NFD', texto)
    texto_sin_tildes = ''.join(
        caracter for caracter in texto_normalizado
        if not unicodedata.combining(caracter)
    )
    return texto_sin_tildes

def singularizar(doc: list) -> list:
    """
    Singulariza las palabras para reducir la dimensión de las mismas.

    Args:
        doc (list): Lista de palabras.

    Returns:
        list: Lista de palabras singularizadas.
    """
    return [
        palabra[:-2] if palabra.endswith("es") else
        palabra[:-1] if palabra.endswith("s") else
        palabra
        for palabra in doc
    ]
