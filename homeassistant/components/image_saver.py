"""
A component which allows you to send data to Datadog.

For more details about this component, please refer to the documentation at
https://home-assistant.io/components/image_saver/
"""
import io
import logging

from homeassistant.exceptions import HomeAssistantError
from homeassistant.loader import get_component
import homeassistant.util.dt as dt_util


_LOGGER = logging.getLogger(__name__)

DATE_TIME_STR_FORMAT = '%Y-%m-%d_%H:%M'
DEFAULT_TIMEOUT = 10
DOMAIN = 'image_saver'
SERVICE_SAVE = 'save'


def setup(hass, _):
    """Setup the Image_saver component."""
    def image_saver_service(service):
        """Service for saving image."""
        from PIL import Image
        camera_entity = service.get('camera_entity')
        timeout = service.get('timeout', DEFAULT_TIMEOUT)
        folder_path = service.get('folder_path')

        if not folder_path:
            _LOGGER.error("Folder path is missing")
            return
        elif not hass.config.is_allowed_path(folder_path):
            _LOGGER.error("Folder path is invalid or not allowed.")
            return

        camera = get_component('camera')
        try:
            image = yield from camera.async_get_image(hass, camera_entity,
                                                      timeout=timeout)

        except HomeAssistantError as err:
            _LOGGER.error("Error on receive image from entity: %s", err)
            return

        _time_str = dt_util.as_local(dt_util.utcnow()).strftime(DATE_TIME_STR_FORMAT)
        image_path = folder_path + _time_str
        stream = io.BytesIO(image)
        img = Image.open(stream)
        img.save(image_path, 'png')

        hass.bus.async_fire('image saved', {
            'entity_id': camera_entity,
            'image_path': image_path
        })

    hass.services.async_register(DOMAIN, SERVICE_SAVE, image_saver_service)

    return True
