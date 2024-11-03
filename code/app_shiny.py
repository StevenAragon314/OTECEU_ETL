
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

def server(input: Inputs, output: Outputs, session: Session):

    index = reactive.Value(0)

    @reactive.calc
    def data():
        if input.file_upload() is not None:
            file_path = input.file_upload()[0]["datapath"]
            try:
                df = pd.read_csv(file_path)
                df = df.loc[df["n_by_text"] >= 4, :]
                if input.daterange()[0] and input.daterange()[1]:
                    df = df.loc[
                        (df["fecha_publicacion_CD"] <= input.daterange()[1]) &
                        (df["fecha_publicacion_CD"] >= input.daterange()[0]), :
                    ]
                l_df = len(df)
                print(f"CSV cargado exitosamente con {l_df} registros.")
                return (df, l_df, file_path)
            except FileNotFoundError:
                print(f"Error: No se encontró el archivo en la ruta {file_path}.")
            except Exception as e:
                print(f"Error al cargar el archivo CSV: {e}")
        # Retorno por defecto
        return pd.DataFrame(), 0, None

    @output
    @render.text
    def file_status():
        df, l_df, _ = data()
        if input.file_upload() is not None and l_df > 0:
            return "Archivo cargado y filtrado exitosamente."
        elif input.file_upload() is not None:
            return "El archivo no contiene registros después del filtrado."
        return "No se ha cargado ningún archivo."

    @output
    @render.table
    def file_preview():
        df, l_df, _ = data()
        if not df.empty:
            return df.head()
        return pd.DataFrame()

    @reactive.Effect
    @reactive.event(input.action_suma)
    def _aumentar_index():
        _, l_df, _ = data()
        if l_df > 0:
            nuevo_index = (index() + 1) % l_df
            index.set(nuevo_index)

    @reactive.Effect
    @reactive.event(input.action_resta)
    def _disminuir_index():
        _, l_df, _ = data()
        if l_df > 0:
            nuevo_index = (index() - 1) % l_df
            index.set(nuevo_index)

    def get_current_row():
        _, l_df, _ = data()
        if l_df > 0:
            return data()[0].iloc[index()]
        else:
            return None

    @output
    @render.ui
    def image_output():
        row = get_current_row()
        imagen_url = row.get('imagen_url', '') if row is not None else ''
        if imagen_url:
            return ui.HTML(f'<img src="{imagen_url}" alt="Imagen no disponible" style="width:100%; height:100%;" />')
        return ui.HTML('<p>No hay imagen disponible.</p>')

    @output
    @render.text
    def text_resumen():
        row = get_current_row()
        return row.get('resumen_art', '') if row is not None else ''

    @output
    @render.text
    def text_autor():
        row = get_current_row()
        return row.get('autor_redacta', '') if row is not None else ''

    @output
    @render.text
    def text_fecha():
        row = get_current_row()
        return row.get('fecha_publicacion', '').upper() if row is not None else ''

    @output
    @render.text
    def text_title():
        row = get_current_row()
        return row.get('titulo_articulo', '') if row is not None else ''

    @output
    @render.text
    def text_link_notice():
        row = get_current_row()
        return row.get('notice_url', '') if row is not None else ''

    @output
    @render.text
    def text_link_img():
        row = get_current_row()
        return row.get('imagen_url', '') if row is not None else ''

    # Variable reactiva para el estado de actualización
    update_status = reactive.Value("")

    @output
    @render.text
    def counter():
        return update_status()

    @reactive.Effect
    @reactive.event(input.action_button)
    def _actualizar_datos():
        _, _, file_path = data()
        if file_path:
            try:
                ws.scrape_data(file_path)
                update_status.set("Datos actualizados exitosamente.")
            except Exception as e:
                update_status.set(f"Error durante la actualización: {str(e)}")
        else:
            update_status.set("No hay archivo cargado para actualizar.")


app = App(app_ui, server)

# def run_app():
#     """Función para ejecutar la aplicación localmente."""
#     app.run()
if '__name__' == '__main__':
    app.run()