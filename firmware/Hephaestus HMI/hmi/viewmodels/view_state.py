from dataclasses import dataclass, field

PLACEHOLDER = "----"


@dataclass
class ViewState:
    connected: bool = False
    running: bool = False
    manual_mode: bool = False
    busy: bool = False
    temperature_text: str = PLACEHOLDER
    setpoint_text: str = PLACEHOLDER
    output_text: str = PLACEHOLDER
    banner_text: str = "CONNECTING..."
    banner_level: str = "warn"
    link_text: str = "OFFLINE"
    link_level: str = "warn"
    mode_switch_enabled: bool = False
    fields_enabled: bool = False
    apply_enabled: bool = False
    run_button_text: str = "START SYSTEM"
    run_button_level: str = "start"
    run_button_enabled: bool = False
    locked_note_visible: bool = False
    fault_active: bool = False
    safe_limit: float | None = None
    status_rows: dict = field(default_factory=dict)
    hints: dict = field(default_factory=dict)
