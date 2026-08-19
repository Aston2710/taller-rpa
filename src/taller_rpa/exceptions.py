"""Excepciones personalizadas del bot."""

from __future__ import annotations


class BotException(Exception):
    """Excepción base del bot."""


class FileReadError(BotException):
    """El archivo de entrada no se pudo leer o su formato no es soportado."""


class ValidationFailedError(BotException):
    """El archivo no cumple la estructura mínima esperada."""


class SubmissionError(BotException):
    """Falló el envío de una solicitud al formulario web."""
