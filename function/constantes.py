# constantes.py

from function.utilidades import quitar_tildes, singularizar

# Diccionario de meses a español
MESES = {
    "ene": 1,
    "feb": 2,
    "mar": 3,
    "abr": 4,
    "may": 5,
    "jun": 6,
    "jul": 7,
    "ago": 8,
    "sept": 9,
    "oct": 10,
    "nov": 11,
    "dic": 12
}

# Bolsa de palabras
KEY_WORDS_NOUNS = [
    "estudiantes", "becas", "ayudas", "recursos destinados", "prestamos",
    "beneficios", "acceso", "inclusion", "igualdad", "diversidad",
    "equidad", "derechos", "apoyo", "libertad", "justicia",
    "oportunidades", "discriminacion", "participacion", "balance", "proporcionalidad"
]

KEY_WORDS_NOUNS = [singularizar(quitar_tildes(word)) for word in KEY_WORDS_NOUNS]

KEY_WORDS_VERBS = [
    "apoyar", "ayudar", "prestar"
]

KEY_WORDS_ADJECTIVES = [
    "social", "equitativo", "cultural", "laboral"
]

KEY_WORDS = KEY_WORDS_VERBS + KEY_WORDS_NOUNS + KEY_WORDS_ADJECTIVES


# Texto que no interesa extraer pero que igualmente está presente en todos los documentos
TEXTO_BASURA = "Conozca el detalle del proceso de admisión a la UCR Listado de las 153 carreras que ofrecen diplomados, grados y pregrados en la UCR Espacios abiertos a todo público para debatir desde la universidad temas de interés nacional Aseguramiento de la calidad de la Universidad de Costa Rica Servicios científicos a la comunidad nacional Listado de centros e institutos por áreas del conocimiento Opciones abiertas de formación para todo público Órgano Colegiado cuyas decisiones son de acatamiento obligatorio para toda la comunidad universitaria Instancia universitaria de mayor jerarquía ejecutiva Un recorrido para reconocer de dónde venimos   "