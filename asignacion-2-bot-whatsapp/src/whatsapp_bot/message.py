"""Builder para el texto del mensaje que envía el bot."""

from __future__ import annotations


class MensajeBuilder:
    """Arma el texto del mensaje paso a paso (Builder pattern)."""

    def __init__(self) -> None:
        self._lineas: list[str] = []

    def tarea_finalizada(self) -> "MensajeBuilder":
        self._lineas.append("Tarea finalizada.")
        return self

    def con_patrones(self, patrones: list[str]) -> "MensajeBuilder":
        self._lineas.append(f"Patrones utilizados: {', '.join(patrones)}.")
        return self

    def build(self) -> str:
        if not self._lineas:
            raise ValueError("El mensaje no tiene contenido")
        return "\n".join(self._lineas)
