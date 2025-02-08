import asyncio
from winrt.windows.media.control import GlobalSystemMediaTransportControlsSessionManager as MediaManager
from winrt.windows.storage.streams import DataReader
import os


username = os.getlogin()


def c_session_info():
    async def get_info():
        session_manager = await MediaManager.request_async()
        current_session = session_manager.get_current_session()

        try:
            info = await current_session.try_get_media_properties_async()
            title = info.title
            artist = info.artist
            return f"Now Playing: {title} by {artist}"

        except Exception as e:
            return "No active media session to control."

    session = asyncio.run(get_info())
    return session

def play_pause():
    async def get_session():
        try:
            session_manager = await MediaManager.request_async()
            current_session = session_manager.get_current_session()
            return await current_session.try_toggle_play_pause_async()
        except AttributeError:
            pass
    
    pause_play = asyncio.run(get_session())
    return pause_play

async def control_media():
    session_manager = await MediaManager.request_async()
    current_session = session_manager.get_current_session()

    if not current_session:
        return "No active media session to control."

    try:
        info = await current_session.try_get_media_properties_async()
        thumbnail = info.thumbnail


        if thumbnail:
            await save_thumbnail(thumbnail, "thumbnail.jpg")

    except Exception as e:
        return ""

async def save_thumbnail(thumbnail, filename, directory=fr"C:\Users\{username}\AppData\Local\Temp"):
    try:
        if directory:
            os.makedirs(directory, exist_ok=True)
            filepath = os.path.join(directory, filename)
        else:
            filepath = filename

        stream = await thumbnail.open_read_async()

        input_stream = stream.get_input_stream_at(0)
        data_reader = DataReader(input_stream)
        data_reader.load_async(stream.size)

        data = data_reader.read_bytes(stream.size)
        data_reader.detach_stream()

        with open(filepath, "wb") as file:
            file.write(bytes(data))

    except Exception as e:
        return ""


async def get_media_session():
    session_manager = await MediaManager.request_async()
    session = session_manager.get_current_session()
    
    if not session:
        print("No media session available.")

    return session

async def fast_forward():
    session = await get_media_session()
    if not session:
        print("⚠️ No active media session")
        return

    try:
        timeline = session.get_timeline_properties()
        
        current_ticks = timeline.position.duration
        max_ticks = timeline.max_seek_time.duration

        if max_ticks <= 0:
            print("❌ Seeking not supported")
            return

        success = await session.try_change_playback_position_async(current_ticks + 1e+8)

        
        if success:
            print("⏩ Fast forwarded 10s")
        else:
            print("❌ Fast forward failed (app rejected the request)")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")



async def rewind():
    session = await get_media_session()
    if not session:
        print("⚠️ No active media session")
        return

    try:
        timeline = session.get_timeline_properties()
        
        current_ticks = timeline.position.duration
        max_ticks = timeline.max_seek_time.duration

        if max_ticks <= 0:
            print("❌ Seeking not supported")
            return

        success = await session.try_change_playback_position_async(current_ticks - 1e+8)

        
        if success:
            print("⏩ Fast forwarded 10s")
        else:
            print("❌ Fast forward failed (app rejected the request)")
        
    except Exception as e:
        return ''


def start_asyncio_loop(panel):
    global loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    panel.loop = loop
    loop.run_forever()

def get_image():
    if loop:
        asyncio.run_coroutine_threadsafe(control_media(), loop)
    else:
        print("Loop not available yet.")