
import pandas as pd
from shiny import App, Inputs, Outputs, Session, reactive, render, ui
from shiny.types import FileInfo
import code.web_scraping as ws


hist_data_path = r'C:\Users\Steve\freelance_work\OTECEU_ETL\data\historic_data.csv'

# === Definición de la Interfaz de Usuario ===
app_ui = ui.page_fluid(
    ui.navset_card_pill(
        ui.nav_panel( "Visualización de Datos",
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
        ),
        ),
        ui.nav_panel( "Ajuste de Datos",
         ui.input_file("file_upload", "Selecciona un archivo CSV", accept=[".csv"]),
        ui.input_date_range("daterange", "Selecciona un rango de fechas", start= '2024-03-01'),
        ui.output_text("file_status"),
        ui.output_text("file_preview")
        ),
    ),
)

import pandas as pd
from shiny import reactive, render, ui
from shiny.types import Inputs, Outputs, Session

# Asegúrate de definir 'hist_data_path' y 'ws' en algún lugar del código

def server(input: Inputs, output: Outputs, session: Session):
    
    @reactive.Calc
    def data():
        # Verifica si se ha subido un archivo
        if input.file_upload() is not None:
            # Obtén la ruta temporal del archivo subido
            file_path = input.file_upload()[0]["datapath"]
            try:
                # Cargar el CSV usando la ruta
                df = pd.read_csv(file_path)
                return df
            except Exception as e:
                print(f"Error al cargar el archivo CSV: {e}")
                return pd.DataFrame()
        else:
            return pd.DataFrame()

    @output
    @render.text
    def file_status():
        if input.file_upload() is not None:
            return "Archivo cargado exitosamente."
        return "No se ha cargado ningún archivo."

    @output
    @render.text
    def file_preview():
        df = data()
        if not df.empty:
            return df.head().to_string()  # Muestra las primeras filas del DataFrame
        return "No hay datos para mostrar."

    df = data()
    l_df = len(df)

    # Incrementar el índice
    @reactive.Effect
    @reactive.event(input.action_suma)
    def _aumentar_index():
        if l_df > 0:
            nuevo_index = (index() + 1) % l_df
            index.set(nuevo_index)

    # Decrementar el índice
    @reactive.Effect
    @reactive.event(input.action_resta)
    def _disminuir_index():
        if l_df > 0:
            nuevo_index = (index() - 1) % l_df
            index.set(nuevo_index)

    # Función para obtener la fila actual
    def get_current_row():
        if l_df > 0:
            return df.iloc[index()]
        else:
            return pd.Series()

    # Salida de imagen
    @output
    @render.ui
    def image_output():
        row = get_current_row()
        imagen_url = row.get('imagen_url', '')
        if imagen_url:
            return ui.HTML(f'<img src="{imagen_url}" alt="Imagen no disponible" style="width:100%; height:100%;" />')
        return ui.HTML("No image available.")

    # Salida de resumen
    @output
    @render.text
    def text_resumen():
        row = get_current_row()
        return row.get('resumen_art', '')

    # Salida de autor
    @output
    @render.text
    def text_autor():
        row = get_current_row()
        return row.get('autor_redacta', '')

    # Salida de fecha
    @output
    @render.text
    def text_fecha():
        row = get_current_row()
        return row.get('fecha_publicacion', '').upper()

    # Salida de título
    @output
    @render.text
    def text_title():
        row = get_current_row()
        return row.get('titulo_articulo', '')

    # Salida de enlace de la noticia
    @output
    @render.text
    def text_link_notice():
        row = get_current_row()
        return row.get('notice_url', '')

    # Salida de enlace de la imagen
    @output
    @render.text
    def text_link_img():
        row = get_current_row()
        return row.get('imagen_url', '')

    # Salida de actualización de datos
    @output
    @render.text
    @reactive.event(input.action_button)
    def counter():
        try:
            ws.scrape_data(hist_data_path)  # Asegúrate de que esta función esté definida en 'ws'
            return "Datos actualizados exitosamente."
        except Exception as e:
            return f"Error durante la actualización: {str(e)}"



app = App(app_ui, server)

# def run_app():
#     """Función para ejecutar la aplicación localmente."""
#     app.run()
if '__name__' == '__main__':
    app.run()