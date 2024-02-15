import logging
import pyautogui
import numpy as np

from PySide6.QtCore import QRect, QSize, Qt, QTimer, Signal
from PySide6.QtGui import QBrush, QColor, QFontMetrics, QPainter, QPen, QImage, QPixmap

from PySide6.QtWidgets import QLabel

log = logging.getLogger(__name__)


class CamRoiComponent(QLabel):
    roi_added = Signal(QRect)

    def __init__(self):
        super().__init__()
        self.rois = []  # List of QRect objects representing the ROIs

        self.current_roi = None
        self.is_drawing = False
        self.edit_state = False
        self.collided_roi_index = -1
        self.toggle_state_last = 0
        self.demo_mode = "TOGGLE_KEYS"

        self.current_pixmap = None
        self.qImage = QImage(640, 480, QImage.Format_RGB888)
        self.img_data = np.frombuffer(self.qImage.bits(), np.uint8).reshape(
            (self.qImage.height(), self.qImage.width(), 3)
        )

        self.msg = ""
        self.show_text = False

    def _add_roi(self, roi):
        self.rois.append(roi)
        self.roi_added.emit(roi)  # Emit the signal with the new ROI

    def set_image(self, pixmap):
        np.copyto(self.img_data, pixmap.frame)  # Copy the frame data to the QImage
        self.current_pixmap = QPixmap.fromImage(self.qImage)
        self.update()  # Schedule a repaint

    def mousePressEvent(self, event):
        if self.edit_state:  # Check if the edit button is toggled
            self.is_drawing = True
            self.current_roi = QRect(event.position().toPoint(), QSize(0, 0))

    def mouseMoveEvent(self, event):
        if self.is_drawing:
            self.current_roi.setBottomRight(event.position().toPoint())
            self.update()

    def mouseReleaseEvent(self, event):
        if self.is_drawing:
            self._add_roi(self.current_roi)
            self.is_drawing = False
            self.update()

    def setEditState(self, state):
        self.edit_state = state

    def set_collision(self, index):
        self.collided_roi_index = index

    def set_msg(self, msg):
        self.msg = msg
        self.show_text = True
        QTimer.singleShot(5000, self._hideText)
        self.update()

    def _hideText(self):
        self.show_text = False
        self.update()  # This will trigger a repaint of the widget

    def _showText(self, painter, width, height, text):
        # Set the color for the text
        color = QColor(255, 0, 0)  # This is red. Adjust RGB values as needed.
        pen = QPen(color)
        painter.setPen(pen)

        font = painter.font()
        font.setPointSize(24)
        painter.setFont(font)

        # Calculate the position to draw the text
        text = self.msg
        font_metrics = QFontMetrics(font)
        text_width = font_metrics.boundingRect(text).width()
        text_height = font_metrics.height()

        x = (width - text_width) / 2
        y = (height + text_height) / 2  # + because the y-coordinate is the baseline of the text

        # Draw the text at the calculated position
        painter.drawText(x, y, text)

    def paintEvent(self, event):
        super().paintEvent(event)

        if self.current_pixmap:
            painter = QPainter(self)
            painter.drawPixmap(0, 0, self.current_pixmap)

            painter.setPen(QPen(Qt.black, 2))
            painter.setBrush(QBrush(QColor(0, 255, 0, 127)))  # Semi-transparent green

            # for index, roi in enumerate(self.rois):
            #     if index == self.collided_roi_index:  # Check if the current ROI is the collided one
            #         painter.setBrush(QBrush(QColor(255, 0, 0, 127)))  # red
            #     else:
            #         painter.setBrush(QBrush(QColor(0, 255, 0, 127)))  # green
            #     painter.drawRect(roi)

            # if self.demo_mode == "TOGGLE_KEYS":
            #     if self.collided_roi_index == -1:
            #         self.toggle_state_last = 0
            #     elif self.collided_roi_index == 0 and self.toggle_state_last == 0:
            #         pyautogui.keyDown("space")
            #         # pyautogui.scroll(10)
            #         print("space")
            #         self.toggle_state_last = 1
            #     elif self.collided_roi_index == 1 and self.toggle_state_last == 0:
            #         # pyautogui.press("w")
            #         pyautogui.keyDown("w")
            #         # pyautogui.scroll(-10)
            #         self.toggle_state_last = 1

            # if self.demo_mode == "SCROLL":
            #     if self.collided_roi_index == 0:
            #         pyautogui.scroll(-1)
            #     elif self.collided_roi_index == 1:
            #         pyautogui.scroll(1)

            if self.is_drawing and self.current_roi:
                painter.drawRect(self.current_roi)

            if self.show_text == True:
                self._showText(painter, self.current_pixmap.width(), self.current_pixmap.height(), self.msg)

            painter.end()
        else:
            painter = QPainter(self)
            width = 640
            height = 480
            painter.setPen(QPen(Qt.black, 2))
            painter.setBrush(QBrush(QColor(0, 0, 0, 0)))  # Semi-transparent green
            painter.drawRect(0, 0, width, height)
            if self.show_text == True:
                self._showText(painter, width, height, self.msg)

            painter.end()
