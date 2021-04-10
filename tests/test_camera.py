"""Tests for camera component."""
import logging
from unittest.mock import call, mock_open, patch

from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.mail_and_packages.const import CAMERA, DOMAIN
from tests.const import FAKE_CONFIG_DATA

_LOGGER = logging.getLogger(__name__)


async def test_update_file_path(
    hass,
    mock_imap_no_email,
    mock_osremove,
    mock_osmakedir,
    mock_listdir,
    mock_update_time,
    mock_copy_overlays,
    mock_hash_file,
    mock_getctime_today,
    caplog,
):
    """Test update_file_path service."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="imap.test.email",
        data=FAKE_CONFIG_DATA,
    )

    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    with patch("os.path.isfile", return_value=True), patch(
        "os.access", return_value=True
    ):
        state = hass.states.get("camera.mail_usps_camera")
        assert state.attributes.get("friendly_name") == "Mail USPS Camera"
        assert (
            "custom_components/mail_and_packages/mail_none.gif"
            in state.attributes.get("file_path")
        )

        service_data = {"entity_id": "camera.mail_usps_camera"}
        await hass.services.async_call(DOMAIN, "update_image", service_data)
        await hass.async_block_till_done()

        assert (
            "custom_components/mail_and_packages/mail_none.gif"
            in state.attributes.get("file_path")
        )

        await hass.services.async_call(DOMAIN, "update_image")
        await hass.async_block_till_done()

        assert (
            "custom_components/mail_and_packages/mail_none.gif"
            in state.attributes.get("file_path")
        )

        # TODO: Add process_mail and check camera file path


async def test_check_file_path_access(
    hass,
    mock_imap_no_email,
    mock_osremove,
    mock_osmakedir,
    mock_listdir,
    mock_update_time,
    mock_copy_overlays,
    mock_hash_file,
    mock_getctime_today,
    caplog,
):
    """Test check_file_path_access function."""
    with patch("os.path.isfile", return_value=True), patch(
        "os.access", return_value=False
    ):
        entry = MockConfigEntry(
            domain=DOMAIN,
            title="imap.test.email",
            data=FAKE_CONFIG_DATA,
        )

        entry.add_to_hass(hass)
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
        assert "Could not read camera" in caplog.text


async def test_async_camera_image(
    hass,
    mock_imap_no_email,
    mock_osremove,
    mock_osmakedir,
    mock_listdir,
    mock_update_time,
    mock_copy_overlays,
    mock_hash_file,
    mock_getctime_today,
):
    """Test async_camera_image function."""

    with patch("os.path.isfile", return_value=True), patch(
        "os.access", return_value=False
    ):
        entry = MockConfigEntry(
            domain=DOMAIN,
            title="imap.test.email",
            data=FAKE_CONFIG_DATA,
        )

        entry.add_to_hass(hass)
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

        cameras = hass.data[DOMAIN][entry.entry_id][CAMERA]
        m_open = mock_open()
        with patch("builtins.open", m_open, create=True):
            image = await cameras[0].async_camera_image()

        assert m_open.call_count == 1
        assert (
            "custom_components/mail_and_packages/mail_none.gif"
            in m_open.call_args.args[0]
        )
        assert m_open.call_args.args[1] == "rb"


async def test_async_camera_image_file_error(
    hass,
    mock_imap_no_email,
    mock_osremove,
    mock_osmakedir,
    mock_listdir,
    mock_update_time,
    mock_copy_overlays,
    mock_hash_file,
    mock_getctime_today,
    caplog,
):
    """Test async_camera_image function."""

    with patch("os.path.isfile", return_value=True), patch(
        "os.access", return_value=False
    ):
        entry = MockConfigEntry(
            domain=DOMAIN,
            title="imap.test.email",
            data=FAKE_CONFIG_DATA,
        )

        entry.add_to_hass(hass)
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

        cameras = hass.data[DOMAIN][entry.entry_id][CAMERA]
        m_open = mock_open()
        with patch("builtins.open", m_open, create=True):
            m_open.side_effect = FileNotFoundError
            image = await cameras[0].async_camera_image()

        assert "Could not read camera" in caplog.text


async def test_async_on_demand_update(
    hass,
    mock_imap_no_email,
    mock_osremove,
    mock_osmakedir,
    mock_listdir,
    mock_update_time,
    mock_copy_overlays,
    mock_hash_file,
    mock_getctime_today,
):
    """Test async_camera_image function."""

    with patch("os.path.isfile", return_value=True), patch(
        "os.access", return_value=False
    ):
        entry = MockConfigEntry(
            domain=DOMAIN,
            title="imap.test.email",
            data=FAKE_CONFIG_DATA,
        )

        entry.add_to_hass(hass)
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

        cameras = hass.data[DOMAIN][entry.entry_id][CAMERA]
        m_open = mock_open()
        with patch("builtins.open", m_open, create=True):
            image = await cameras[0].async_on_demand_update()

        assert image is None
