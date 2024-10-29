import os
import sys
import pandas as pd
from shiny import App, Inputs, Outputs, Session, reactive, render, ui
import code.web_scraping as ws
import uvicorn

def obtener_ruta_recurso(ruta_relativa):
    """Obtiene la ruta absoluta compatible con PyInstaller."""
    if getattr(sys, 'frozen', False):
        # Cuando se ejecuta como un ejecutable
        base_dir = sys._MEIPASS  # Directorio temporal del ejecutable
    else:
        # Cuando se ejecuta como un script
        base_dir = os.path.dirname(os.getcwd())  # Directorio del script

    return os.path.join(base_dir, ruta_relativa)

# Obtener la ruta al archivo CSV
hist_data_path = obtener_ruta_recurso('OTECEU_ETL\\data\\historic_data.csv')

# Cargar los datos del CSV
try:
    df = pd.read_csv(hist_data_path)
    df = df.loc[df["n_by_text"] >= 4, :]
    l_df = len(df)
    print(f"CSV cargado exitosamente con {l_df} registros.")
except FileNotFoundError:
    print(f"Error: No se encontró el archivo en la ruta {hist_data_path}.")
    df = pd.DataFrame()  # DataFrame vacío en caso de error
    l_df = 0
except Exception as e:
    print(f"Error al cargar el archivo CSV: {e}")
    df = pd.DataFrame()
    l_df = 0

# === Definición de la Interfaz de Usuario ===
app_ui = ui.page_fluid(
    ui.tags.style("body { background-color: lightblue; }"),
    ui.tags.img(
        src='https://www.ucr.ac.cr/vistas/webucr_ucr_5/imagenes/firma-ucr-c.svg',
        height="100%", width="100%"
    ),
    ui.layout_columns(
        ui.card(
            ui.tags.b("Información recolectada del sitio oficial NOTICIAS UCR:"),
            ui.layout_columns(
                ui.card(
                    ui.tags.b("Título de la noticia"),
                    ui.output_text("text_title"),
                    ui.output_ui("image_output", fill=True),
                    ui.layout_columns(
                        ui.input_action_button("action_resta", "⬅️"),
                        ui.input_action_button("action_suma", "➡️")
                    ),
                ),
                ui.card(
                    ui.tags.b("Resumen"),
                    ui.output_text("text_resumen"),
                    ui.card(
                        ui.tags.b("Información de autoría"),
                        ui.layout_columns(
                            ui.card(ui.tags.b("Autores"), ui.output_text("text_autor")),
                            ui.card(ui.tags.b("Fecha de publicación"), ui.output_text("text_fecha"))
                        )
                    ),
                    ui.tags.b("Actualización de base de datos"),
                    ui.card(
                        ui.input_action_button("action_button", "Actualizar datos"),
                        ui.output_text("counter")
                    )
                ),
                ui.card(
                    ui.tags.b("Fuente de la información"),
                    ui.card(ui.tags.b("Link de imagen:"), ui.output_text("text_link_img")),
                    ui.card(ui.tags.b("Link de noticia:"), ui.output_text("text_link_notice"))
                )
            )
        )
    )
)

def server(input: Inputs, output: Outputs, session: Session):
    index = reactive.Value(0)

    @reactive.Effect
    @reactive.event(input.action_suma)
    def _aumentar_index():
        if l_df > 0:
            nuevo_index = (index() + 1) % l_df
            index.set(nuevo_index)

    @reactive.Effect
    @reactive.event(input.action_resta)
    def _disminuir_index():
        if l_df > 0:
            nuevo_index = (index() - 1) % l_df
            index.set(nuevo_index)

    def get_current_row():
        if l_df > 0:
            return df.iloc[index()]
        else:
            return pd.Series()

    @output
    @render.ui
    def image_output():
        row = get_current_row()
        imagen_url = row.get('imagen_url', '')
        if imagen_url:
            return ui.HTML(f'<img src="{imagen_url}" alt="Imagen no disponible" style="width:100%; height:100%;" />')
        return ui.HTML("No image available.")

    @output
    @render.text
    def text_resumen():
        row = get_current_row()
        return row.get('resumen_art', '')

    @output
    @render.text
    def text_autor():
        row = get_current_row()
        return row.get('autor_redacta', '')

    @output
    @render.text
    def text_fecha():
        row = get_current_row()
        return row.get('fecha_publicacion', '').upper()

    @output
    @render.text
    def text_title():
        row = get_current_row()
        return row.get('titulo_articulo', '')

    @output
    @render.text
    def text_link_notice():
        row = get_current_row()
        return row.get('notice_url', '')

    @output
    @render.text
    def text_link_img():
        row = get_current_row()
        return row.get('imagen_url', '')

    @output
    @render.text
    @reactive.event(input.action_button)
    def counter():
        try:
            ws.scrape_data(hist_data_path)
            return "Datos actualizados exitosamente."
        except Exception as e:
            return f"Error durante la actualización: {str(e)}"

# Definir la instancia de la aplicación a nivel de módulo
app = App(app_ui, server)

def run_app():
    """Función para ejecutar la aplicación localmente."""
    app.run()
