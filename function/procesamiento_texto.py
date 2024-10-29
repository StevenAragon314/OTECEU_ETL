# procesamiento_texto.py

import pandas as pd
import spacy
from nltk.corpus import stopwords
from typing import List, Optional
import nltk
from function.utilidades import word_tokenize, quitar_tildes, singularizar
from function.constantes import KEY_WORDS

def text_reduce(df: pd.DataFrame, col: str,
               stopwords_list: list = None,
                 key_words: list = None) -> pd.Series:
    """
    Procesa una columna de texto en el DataFrame para contar
    cuántas palabras están en la lista de key_words después de limpiar el texto.

    Args:
        df (pd.DataFrame): DataFrame que contiene los datos.
        col (str): Nombre de la columna a procesar.
        new_col_suffix (str): Sufijo para la nueva columna de conteo.
        stopwords_list (list, optional): Lista de palabras a eliminar. 
                                         Si es None, se usan las stopwords de NLTK en español.
        key_words (list): Lista de palabras clave para contar.

    Returns:
        pd.DataFrame: DataFrame con la nueva columna añadida.
    """

    if stopwords_list is None:
        stopwords_set = set(nltk_stopwords.words('spanish'))
    else:
        stopwords_set = set(stopwords_list)
    
    if key_words is None:
        key_words = []
    
    # Cargar el modelo de spaCy una sola vez
    nlp = spacy.load("es_core_news_sm", disable=["parser", "ner"])

    counts = []

    for idx in df.index:
        n_words = 0
        text = df.at[idx, col]

        if pd.isnull(text):
            counts.append(n_words)
            continue

        # Tokenización y limpieza
        tokens = word_tokenize(text)
        tokens = (word.lower() for word in tokens)
        tokens = (word for word in tokens if word not in stopwords_set)
        tokens = (quitar_tildes(word) for word in tokens)
        text_ready01 = ' '.join(tokens)
        text_ready01 = text_ready01.split()
        text_ready = singularizar(text_ready01)
        text_ready = ' '.join(text_ready)

        # Lematización
        doc = nlp(text_ready)
        lemmas = (token.lemma_ for token in doc)

        n_words = sum(1 for word in lemmas if word in key_words)

        counts.append(n_words)

    return counts