import time

import numpy as np
import pyqtgraph as pg
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from .. import config
from . import theme

pg.setConfigOptions(antialias=True, foreground=theme.TEXT, background=theme.PLOT_BG)


class TrendPanel(QWidget):
    WINDOWS = (("1 min", 60), ("5 min", 300), ("15 min", 900), ("1 hour", 3600), ("6 hours", 21600))

    def __init__(self, parent=None):
        super().__init__(parent)
        self._follow = True
        self._auto_y = True
        self._window = float(config.DEFAULT_PLOT_WINDOW_S)
        self._t = np.empty(0)
        self._pv = np.empty(0)
        self._sp = np.empty(0)

        axis = pg.DateAxisItem(orientation="bottom")
        self._plot = pg.PlotWidget(axisItems={"bottom": axis})
        self._item = self._plot.getPlotItem()
        self._vb = self._item.getViewBox()
        self._item.showGrid(x=True, y=True, alpha=0.22)
        self._item.setLabel("left", "Temperature", units="°C")
        self._item.setClipToView(True)
        self._item.setDownsampling(auto=True, mode="subsample")
        self._item.addLegend(offset=(70, 12))
        self._vb.setLimits(minXRange=2.0, yMin=-20.0, yMax=130.0, minYRange=0.5)
        self._vb.disableAutoRange()

        self._pv_curve = self._item.plot(
            pen=pg.mkPen(theme.PV, width=2.6), name="Current temperature", connect="finite"
        )
        self._sp_curve = self._item.plot(
            pen=pg.mkPen(theme.SP, width=2.0, style=Qt.PenStyle.DashLine), name="Target temperature", connect="finite"
        )
        self._limit_line = pg.InfiniteLine(
            pos=50.0,
            angle=0,
            pen=pg.mkPen(theme.RED, width=1.4, style=Qt.PenStyle.DotLine),
            label="SAFE LIMIT",
            labelOpts={"position": 0.97, "color": theme.RED, "anchors": [(1, 1), (1, 1)]},
        )
        self._item.addItem(self._limit_line, ignoreBounds=True)
        self._limit_line.setVisible(False)
        self._vb.sigRangeChangedManually.connect(self._on_manual_range)

        self._live_button = self._button("LIVE", "Follow the newest data", self._on_live_toggled, checkable=True)
        self._live_button.setChecked(True)
        self._auto_y_button = self._button("AUTO Y", "Fit the temperature axis automatically", self._on_auto_y_toggled, checkable=True)
        self._auto_y_button.setChecked(True)

        self._window_combo = QComboBox()
        for title, _ in self.WINDOWS:
            self._window_combo.addItem(title)
        self._window_combo.setCurrentIndex(1)
        self._window_combo.currentIndexChanged.connect(self._on_window_picked)
        self._window_combo.setToolTip("Visible time span while LIVE")

        bar = QHBoxLayout()
        bar.setSpacing(6)
        bar.addWidget(self._live_button)
        bar.addWidget(self._window_combo)
        bar.addSpacing(10)
        bar.addWidget(self._button("Time +", "Zoom in horizontally", lambda: self._zoom_time(0.5)))
        bar.addWidget(self._button("Time -", "Zoom out horizontally", lambda: self._zoom_time(2.0)))
        bar.addWidget(self._button("<", "Move back in time", lambda: self._pan(-0.25)))
        bar.addWidget(self._button(">", "Move forward in time", lambda: self._pan(0.25)))
        bar.addSpacing(10)
        bar.addWidget(self._auto_y_button)
        bar.addWidget(self._button("Temp +", "Zoom in vertically", lambda: self._zoom_temp(0.6)))
        bar.addWidget(self._button("Temp -", "Zoom out vertically", lambda: self._zoom_temp(1.6)))
        bar.addSpacing(10)
        bar.addWidget(self._button("FIT ALL", "Show the whole recording", self._fit_all))
        bar.addStretch(1)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        layout.addLayout(bar)
        layout.addWidget(self._plot, 1)

        self._apply_view()

    def _button(self, text, tooltip, handler, checkable=False):
        button = QPushButton(text)
        button.setToolTip(tooltip)
        button.setCheckable(checkable)
        if checkable:
            button.toggled.connect(handler)
        else:
            button.clicked.connect(lambda _checked=False: handler())
        button.setMinimumWidth(button.sizeHint().width())    
        return button

    def set_history(self, times, temperature, setpoint):
        self._t, self._pv, self._sp = times, temperature, setpoint
        self._pv_curve.setData(times, temperature)
        self._sp_curve.setData(times, setpoint)
        self._apply_view()

    def set_safe_limit(self, value):
        if value is None:
            self._limit_line.setVisible(False)
            return
        self._limit_line.setValue(value)
        self._limit_line.setVisible(True)

    def _y_extent(self, start, end):
        if len(self._t) == 0:
            return 15.0, 60.0
        mask = (self._t >= start) & (self._t <= end)
        values = np.concatenate((self._pv[mask], self._sp[mask]))
        values = values[np.isfinite(values)]
        if values.size == 0:
            return 15.0, 60.0
        low, high = float(values.min()), float(values.max())
        pad = max(1.5, (high - low) * 0.12)
        return low - pad, high + pad

    def _apply_view(self):
        if self._follow:
            last = float(self._t[-1]) if len(self._t) else time.time()
            start = last - self._window
            end = last + self._window * 0.03
            self._vb.setXRange(start, end, padding=0)
        else:
            start, end = self._vb.viewRange()[0]
        if self._auto_y:
            low, high = self._y_extent(start, end)
            self._vb.setYRange(low, high, padding=0)

    def _set_follow(self, value):
        self._follow = value
        self._live_button.blockSignals(True)
        self._live_button.setChecked(value)
        self._live_button.blockSignals(False)
        if value:
            self._apply_view()

    def _set_auto_y(self, value):
        self._auto_y = value
        self._auto_y_button.blockSignals(True)
        self._auto_y_button.setChecked(value)
        self._auto_y_button.blockSignals(False)
        if value:
            self._apply_view()

    def _on_live_toggled(self, checked):
        self._set_follow(checked)

    def _on_auto_y_toggled(self, checked):
        self._set_auto_y(checked)

    def _on_window_picked(self, index):
        if index < 0:
            return
        self._window = float(self.WINDOWS[index][1])
        self._set_follow(True)

    def _on_manual_range(self, mask):
        if mask[0]:
            self._set_follow(False)
        if mask[1]:
            self._set_auto_y(False)

    def _zoom_time(self, factor):
        if self._follow:
            self._window = max(5.0, self._window * factor)
            self._window_combo.blockSignals(True)
            self._window_combo.setCurrentIndex(-1)
            self._window_combo.blockSignals(False)
            self._apply_view()
        else:
            self._vb.scaleBy(x=factor)

    def _zoom_temp(self, factor):
        self._set_auto_y(False)
        self._vb.scaleBy(y=factor)

    def _pan(self, fraction):
        self._set_follow(False)
        start, end = self._vb.viewRange()[0]
        self._vb.translateBy(x=(end - start) * fraction)

    def _fit_all(self):
        if len(self._t) == 0:
            return
        self._set_follow(False)
        self._set_auto_y(False)
        self._vb.setXRange(float(self._t[0]), float(self._t[-1]) + 1.0, padding=0.02)
        low, high = self._y_extent(float(self._t[0]), float(self._t[-1]))
        self._vb.setYRange(low, high, padding=0)
