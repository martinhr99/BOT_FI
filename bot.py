import feedparser
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext, MessageHandler, filters
from telegram.request import HTTPXRequest
import logging
import asyncio
import httpx
from telegram.error import RetryAfter

# Configuración del logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Lista de enlaces RSS de periódicos de España
RSS_FEEDS = [

                ### EL PAÍS   ###

    "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/portada",                                 # Portada
    "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/section/espana",                          # España
    "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/section/internacional",                   # Internacional
    "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/section/opinion",                         # Opinión
    #"https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/section/economia",                        # Economía
    #"https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/section/deportes",                        # Deportes
    "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/section/cultura",                         # Cultura
    #"https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/section/tecnologia",                      # Tecnología
    #"https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/section/ciencia",                         # Ciencia
    #"https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/section/gente-y-estilo",                  # Gente y Estilo
    
                ### EL MUNDO  ###
    "https://elmundo.es/rss/portada.xml",                                                               # Portada  


                ### ABC       ###   
    "https://www.abc.es/rss/2.0/portada/",                                                              # Portada
    "https://www.abc.es/rss/2.0/ultima-hora/",                                                          # Última hora    
    "https://www.abc.es/rss/2.0/opinion/",                                                              # Opinión 
    "https://www.abc.es/rss/2.0/espana/madrid/",                                                        # Madrid
    "https://www.abc.es/rss/2.0/espana/casa-real/",                                                     # Casa Real
    "https://www.abc.es/rss/2.0/espana/",                                                               # España     
    "https://www.abc.es/rss/2.0/internacional/",                                                        # Internacional
    #"https://www.abc.es/rss/2.0/economia/",                                                             # Economía
    "https://www.abc.es/rss/2.0/deportes/",                                                             # Deportes
    #"https://www.abc.es/rss/2.0/sociedad/",                                                             # Sociedad
    #"https://www.abc.es/rss/2.0/cultura/",                                                              # Cultura
    "https://www.abc.es/rss/2.0/xlsemanal/",                                                            # XL Semanal

                ### EL CONFIDENCIAL  ###
    "https://rss.elconfidencial.com/rss",                                                              # Portada
    #"https://rss.elconfidencial.com/rss/empresas",                                                      # Empresas
    #"https://rss.elconfidencial.com/rss/mercados",                                                      # Mercados
    "https://rss.elconfidencial.com/rss/espana",                                                        # España
    #"https://rss.elconfidencial.com/rss/internacional",                                                 # Internacional
    #"https://rss.elconfidencial.com/rss/opinion",                                                       # Opinión
    #"https://rss.elconfidencial.com/rss/cultura",                                                       # Cultura
    "https://rss.elconfidencial.com/rss/deportes",                                                      # Deportes

                ### LA VANGUARDIA  ###   

    "https://www.lavanguardia.com/rss/home.xml",                                                        # Últimas noticias
    "https://www.lavanguardia.com/mvc/feed/rss/internacional",                                          # Internacional
    "https://www.lavanguardia.com/mvc/feed/rss/politica",                                               # Política
    "https://www.lavanguardia.com/mvc/feed/rss/sociedad",                                               # Sociedad
    "https://www.lavanguardia.com/mvc/feed/rss/economia",                                               # Economía
    #"https://www.lavanguardia.com/mvc/feed/rss/cultura",                                                # Cultura
    #"https://www.lavanguardia.com/mvc/feed/rss/deportes",                                               # Deportes

                ### 20 MINUTOS  ###
    "https://www.20minutos.es/rss/",                                                                    # Portada
    "https://www.20minutos.es/rss/deportes/",                                                           # Deportes
    "https://www.20minutos.es/rss/nacional/",                                                           # Nacional
    "https://www.20minutos.es/rss/internacional/",                                                      # Internacional
    #"https://www.20minutos.es/rss/cultura/",                                                            # Cultura
    #"https://www.20minutos.es/rss/tecnologia/",                                                         # Tecnología
    #"https://www.20minutos.es/rss/gente/",                                                              # Gente
    #"https://www.20minutos.es/rss/salud/",                                                              # Salud


                ### EUROPA PRESS ###
    "https://www.europapress.es/rss/rss.aspx?ch=00066",                                                 # Nacional
    "https://www.europapress.es/rss/rss.aspx?ch=00005",                                                 # Economía
    "https://www.europapress.es/rss/rss.aspx?ch=00027",                                                 # Deportes
    "https://www.europapress.es/rss/rss.aspx?ch=00008",                                                 # Internacional

    
                ### EL CONFIDENCIAL ###
    "https://rss.elconfidencial.com/ultimahora.xml",                                                    # Última Hora
    "https://rss.elconfidencial.com/economia.xml",                                                      # Economía
    "https://rss.elconfidencial.com/deportes.xml",                                                      # Deportes
    
                ### MARCA ###
    "https://www.marca.com/rss"                                                                       # Portada

    
]

# Lista para almacenar las noticias que ya han sido enviadas
sent_news = set()

# Función que recoge las noticias de los RSS
def get_rss_news():
    news_list = []
    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries:
            news_item = {
                'title': entry.title,
                'link': entry.link
            }
            news_list.append(news_item)
    return news_list


# Comando /start para iniciar el bot
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('¡Hola! Este es tu bot de noticias. Te enviaré las noticias automáticamente.')

# Comando /stop para detener el bot
async def stop(update: Update, context: CallbackContext) -> None:
    context.bot_data['active'] = False  # Desactiva el bot
    await update.message.reply_text("El bot ahora está inactivo. Usa /start para activarlo de nuevo.")

# Comando /news para obtener noticias al momento
async def news(update: Update, context: CallbackContext) -> None:
    news_list = get_rss_news()  # Obtener noticias

    if news_list:
        for news in news_list:
            try:
                await send_message_with_retry(context, update.message.chat_id, f"{news['title']}: {news['link']}")  # Enviar las noticias al chat
                await asyncio.sleep(60)  # Esperar 1 segundo entre cada mensaje para evitar el control de inundación
            except Exception as e:
                logger.error(f"Error al enviar el mensaje: {e}")
    else:
        await update.message.reply_text("Lo siento, no se pudieron obtener noticias.")



# Función para enviar un mensaje y manejar el error de "flood control"
async def send_message_with_retry(context: CallbackContext, chat_id: int, text: str):
    retries = 5  # Número de reintentos antes de rendirse
    delay = 5  # Retraso inicial entre intentos (en segundos)
    
    for attempt in range(retries):
        try:
            # Intentar enviar el mensaje
            await context.bot.send_message(chat_id=chat_id, text=text)
            #logger.info(f"Mensaje enviado: {text}")
            return  # Si el mensaje se envió con éxito, salimos de la función
        except RetryAfter as e:
            retry_after = e.retry_after
            logger.error(f"Error al enviar el mensaje: Flood control exceeded. Retry in {retry_after} seconds")
            await asyncio.sleep(retry_after)  # Esperar el tiempo recomendado antes de reintentar
            delay = min(retry_after * 2, 60)  # Incrementar el tiempo de espera progresivamente
        except Exception as e:
            logger.error(f"Error inesperado: {e}")
            break  # Si ocurre otro tipo de error, salimos de la función

# Función para enviar noticias automáticamente
async def send_news(context: CallbackContext) -> None:
    news_list = get_rss_news()  # Obtener las noticias no enviadas aún
    if news_list:
        chat_id = -4501917651  # Tu chat ID
        for news in news_list:
            try:
                await send_message_with_retry(context, chat_id, f"{news['title']}: {news['link']}")
                await asyncio.sleep(1)  # Esperar 1 segundo entre cada mensaje para evitar el control de inundación
            except Exception as e:
                logger.error(f"Error al enviar el mensaje: {e}")
    else:
        logger.info("No hay nuevas noticias para enviar.")

# Función para manejar mensajes cuando el bot está activo
async def handle_message(update: Update, context: CallbackContext) -> None:
    if context.bot_data.get('active', False):  # Solo responde si está activo
        await update.message.reply_text(f"Recibí tu mensaje: {update.message.text}")
    else:
        await update.message.reply_text("El bot está inactivo. Usa /start para activarlo.")

# Función principal para crear el bot
def main() -> None:
    """Inicia el bot."""
    # Token de tu bot de Telegram
    TOKEN = '8052426936:AAE7RyPRibGoEub6fLliFHMbyqOaqhMEczM'

    # Configurar el tiempo de espera
    request = HTTPXRequest(connect_timeout=10.0, read_timeout=60.0)

    # Crear la aplicación y el manejador del bot con el tiempo de espera configurado
    app = Application.builder().token(TOKEN).request(request).build()
    app.bot_data['active'] = False

    # Añadir los manejadores para los comandos
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("news", news))
    app.add_handler(CommandHandler("stop", stop))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
  

    # Añadir un trabajo periódico para enviar noticias cada 15 minutos
    job_queue = app.job_queue
    job_queue.run_repeating(send_news, interval=900, first=0)  # 900 segundos = 15 minutos

    # Iniciar el bot
    app.run_polling()

if __name__ == "__main__":
    main()
