"""UI-level application state for search results."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from ..core.services.search_service import SearchMatch
from ..core.data.models import Document


@dataclass
class AppState:
    """Track search results and selection state."""

    search_matches: list[SearchMatch] = field(default_factory=list)
    selected_paper: Optional[Document] = None
    enable_ai_analysis: bool = False
