import webbrowser
from urllib import parse

from qgis.PyQt.QtGui import QPixmap
from qgis.core import QgsMessageLog
from requests.models import PreparedRequest

from geocatbridge.utils.gui import loadUiType
from geocatbridge.utils.meta import getTrackerUrl
from geocatbridge.utils.files import getIconPath

WIDGET, BASE = loadUiType(__file__)


class ErrorDialog(BASE, WIDGET):

    def __init__(self, html_error, md_error):
        super(ErrorDialog, self).__init__()
        self.setupUi(self)

        pixmap = QPixmap(getIconPath("geocatlogo"))
        self.labelIcon.setPixmap(pixmap)

        self.txtError.setHtml(html_error)

        tracker_url = getTrackerUrl()
        if not tracker_url:
            self.btnSendReport.setEnabled(False)
        else:
            self.btnSendReport.clicked.connect(lambda: self.sendReport(md_error, tracker_url))
        self.btnClose.clicked.connect(self.close)

    def sendReport(self, error, tracker_url):
        """ Copies the given stacktrace in a GeoCat support form. """
        payload = {
            "subject": "[Crash Report] GeoCat Bridge for QGIS",
            "message": error
        }
        req = PreparedRequest()
        try:
            req.prepare("GET", tracker_url, params=parse.urlencode(payload, quote_via=parse.quote))
            webbrowser.open_new(req.url)
        except Exception as e:
            QgsMessageLog().logMessage(f"Failed to send crash report: {e}", 'GeoCat Bridge')
