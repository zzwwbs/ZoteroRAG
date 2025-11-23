"""QRunnable wrapper to execute chat requests off the UI thread."""

from __future__ import annotations

from PySide6.QtCore import QObject, QRunnable, Signal

from ..core.services.ai_service import AIService, AIServiceError, UnauthorizedAIServiceError


class _ChatWorkerSignals(QObject):
    result = Signal(str)
    error = Signal(str)
    finished = Signal()
    usage = Signal(object)


class ChatRunnable(QRunnable):
    """Run AIService.chat in a background thread."""

    def __init__(self, service: AIService, messages: list[dict]) -> None:
        super().__init__()
        self._service = service
        self._messages = messages
        self.signals = _ChatWorkerSignals()

    def run(self) -> None:
        try:
            reply, usage = self._service.chat(self._messages)
            self.signals.result.emit(reply)
            self.signals.usage.emit(usage)
        except (AIServiceError, UnauthorizedAIServiceError) as error:
            self.signals.error.emit(str(error))
        except Exception as error:  # pragma: no cover - safeguard
            self.signals.error.emit(str(error))
        finally:
            self.signals.finished.emit()
