
import pandas as pd
from shiny import App, Inputs, Outputs, Session, reactive, render, ui
from shiny.types import FileInfo
import code.web_scraping as ws


hist_data_path = r'C:\Users\Steve\freelance_work\OTECEU_ETL\data\historic_data.csv'

# === Definición de la Interfaz de Usuario ===
app_ui = ui.page_fluid(
    ui.tags.img(
            src='https://www.ucr.ac.cr/vistas/webucr_ucr_5/imagenes/firma-ucr-c.svg',
            height="100%", width="100%"
        ),
    ui.navset_card_pill(
        ui.nav_panel( "Visualización de Datos",
        ui.tags.style("body { background-color: lightblue; }"),
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
        ui.input_numeric("strong_num", "¿Qué tan estricto debe ser el modelo?", 8, min= 4, max= 20)
        ),
    ),
)

def server(input: Inputs, output: Outputs, session: Session):
    
    @reactive.Calc
    def data_path():
        if input.file_upload() is not None:
            try:
                return input.file_upload()[0]["datapath"]
            except Exception as e:
                print(f"Error al cargar el archivo CSV: {e}")
                return None
        else:
            print("No existe dicho path")
            return None

    @reactive.Calc
    def df():
        path = data_path()
        if path:
            try:
                df = pd.read_csv(path)
                df["fecha_publicacion_CD"] = pd.to_datetime(df["fecha_publicacion_CD"], format= "%Y-%m-%d")
                df.sort_values("fecha_publicacion_CD", ascending= False, inplace= True)
                df = df.loc[df["n_by_text"] >= 8, :]
                return df
            except Exception as e:
                print(f"Error al leer el CSV: {e}")
                return pd.DataFrame()
        else:
            return pd.DataFrame()
    
    @reactive.Calc
    def l_df():
        return len(df())

    index = reactive.Value(0)

    @reactive.Effect
    @reactive.event(input.action_suma)
    def _aumentar_index():
        if l_df() > 0:
            nuevo_index = (index() + 1) % l_df()
            index.set(nuevo_index)

    @reactive.Effect
    @reactive.event(input.action_resta)
    def _disminuir_index():
        if l_df() > 0:
            nuevo_index = (index() - 1) % l_df()
            index.set(nuevo_index)

    @reactive.Calc
    def get_current_row():
        if l_df() > 0:
            return df().iloc[index()]
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
        fecha = row.get('fecha_publicacion', '')
        return fecha.upper() if isinstance(fecha, str) else ''

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
    
    # Variable reactiva para el mensaje de actualización
    update_message = reactive.Value("")

    @reactive.Effect
    @reactive.event(input.action_button)
    def _actualizar_datos():
        try:
            ws.scrape_data(data_path())
            update_message.set("Datos actualizados exitosamente.")
        except Exception as e:
            update_message.set(f"Error durante la actualización: {str(e)}")
    
    @output
    @render.text
    def counter():
        return update_message()



app = App(app_ui, server)

def run_app():
    """Función para ejecutar la aplicación localmente."""
    return app.run()     