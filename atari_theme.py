"""
Atari 2600 / Arcade Cabinet Theme for Zuup Preference Collection
================================================================
CRT phosphor aesthetics, limited arcade color palette, scanlines,
and chunky tactile components.
"""

import gradio as gr

# Atari 2600 NTSC-inspired palette
ATARI_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&family=VT323&display=swap');

:root {
    --atari-bg: #0a0a0f;
    --atari-surface: #141420;
    --atari-surface-elevated: #1a1a28;
    --atari-border: #2a2a3a;
    --atari-border-strong: #3a3a4a;
    --atari-phosphor: #7cd0ac;
    --atari-phosphor-bright: #90e4c0;
    --atari-phosphor-dim: #5c9c5c;
    --atari-orange: #fc6323;
    --atari-orange-dim: #d0805c;
    --atari-blue: #3854a8;
    --atari-text: #e0e0e0;
    --atari-muted: #909090;
    --atari-success: #7cd0ac;
    --atari-warning: #fc6323;
    --atari-error: #c05858;
}

.gradio-container {
    background: var(--atari-bg) !important;
    font-family: 'VT323', 'IBM Plex Mono', monospace !important;
    min-height: 100vh;
    position: relative;
}

/* Optional scanline overlay - subtle CRT feel */
.gradio-container.atari-scanlines::before {
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
    background: repeating-linear-gradient(
        0deg,
        transparent,
        transparent 2px,
        rgba(0, 0, 0, 0.08) 2px,
        rgba(0, 0, 0, 0.08) 4px
    );
    z-index: 9999;
}

.main-header {
    text-align: center;
    padding: 2rem 1rem;
    background: var(--atari-surface) !important;
    border: 2px solid var(--atari-border) !important;
    border-radius: 6px !important;
    margin-bottom: 1.5rem;
    box-shadow: 0 0 20px rgba(124, 208, 172, 0.1);
}

.main-header h1 {
    font-family: 'Press Start 2P', cursive !important;
    font-size: 1rem !important;
    font-weight: 400 !important;
    color: var(--atari-phosphor) !important;
    text-shadow: 0 0 10px rgba(124, 208, 172, 0.5);
    margin-bottom: 0.5rem !important;
    letter-spacing: 0.1em;
}

.main-header p {
    color: var(--atari-muted) !important;
    font-size: 1.25rem !important;
    font-family: 'VT323', monospace !important;
}

.domain-card {
    background: var(--atari-surface) !important;
    border: 2px solid var(--atari-border) !important;
    border-radius: 6px !important;
    padding: 1rem !important;
    transition: all 0.2s ease !important;
}

.domain-card:hover {
    border-color: var(--atari-phosphor) !important;
    box-shadow: 0 0 15px rgba(124, 208, 172, 0.2) !important;
}

.response-panel {
    background: var(--atari-surface) !important;
    border: 2px solid var(--atari-border) !important;
    border-radius: 6px !important;
    padding: 1.5rem !important;
    font-family: 'VT323', monospace !important;
    font-size: 1.1rem !important;
    line-height: 1.6 !important;
    max-height: 500px !important;
    overflow-y: auto !important;
}

.response-panel-a {
    border-left: 4px solid var(--atari-phosphor) !important;
    box-shadow: -4px 0 12px rgba(124, 208, 172, 0.15) !important;
}

.response-panel-b {
    border-left: 4px solid var(--atari-orange) !important;
    box-shadow: -4px 0 12px rgba(252, 99, 35, 0.15) !important;
}

.preference-btn {
    padding: 1rem 2rem !important;
    font-size: 1rem !important;
    font-weight: 600 !important;
    font-family: 'Press Start 2P', cursive !important;
    border-radius: 4px !important;
    transition: all 0.15s ease !important;
    min-width: 150px !important;
    border: 3px solid !important;
}

.preference-btn:hover {
    transform: translateY(-1px);
}

.preference-btn:active {
    transform: translateY(1px);
}

.btn-a {
    background: var(--atari-surface) !important;
    border-color: var(--atari-phosphor) !important;
    color: var(--atari-phosphor) !important;
    box-shadow: 0 0 10px rgba(124, 208, 172, 0.2) !important;
}

.btn-a:hover {
    box-shadow: 0 0 20px rgba(124, 208, 172, 0.4) !important;
    color: var(--atari-phosphor-bright) !important;
}

.btn-b {
    background: var(--atari-surface) !important;
    border-color: var(--atari-orange) !important;
    color: var(--atari-orange) !important;
    box-shadow: 0 0 10px rgba(252, 99, 35, 0.2) !important;
}

.btn-b:hover {
    box-shadow: 0 0 20px rgba(252, 99, 35, 0.4) !important;
    color: #ff8c5a !important;
}

.btn-tie {
    background: var(--atari-surface) !important;
    border-color: var(--atari-border-strong) !important;
    color: var(--atari-muted) !important;
}

.btn-tie:hover {
    border-color: var(--atari-text) !important;
    color: var(--atari-text) !important;
}

.slider-label {
    color: var(--atari-text) !important;
    font-weight: 500 !important;
}

.stat-card {
    background: var(--atari-surface) !important;
    border: 2px solid var(--atari-border) !important;
    border-radius: 6px !important;
    padding: 1rem !important;
    text-align: center !important;
}

.stat-number {
    font-size: 2rem !important;
    font-weight: 700 !important;
    color: var(--atari-phosphor) !important;
    text-shadow: 0 0 8px rgba(124, 208, 172, 0.3);
}

.progress-bar {
    height: 8px !important;
    border-radius: 4px !important;
    background: var(--atari-border) !important;
    overflow: hidden !important;
}

.progress-fill {
    height: 100% !important;
    background: var(--atari-phosphor) !important;
    border-radius: 4px !important;
    box-shadow: 0 0 8px rgba(124, 208, 172, 0.5);
    transition: width 0.3s ease !important;
}

.prompt-display {
    background: var(--atari-surface) !important;
    border: 2px solid var(--atari-border) !important;
    border-left: 4px solid var(--atari-phosphor) !important;
    border-radius: 6px !important;
    padding: 1.5rem !important;
    font-size: 1.1rem !important;
    line-height: 1.7 !important;
}

.dimension-slider {
    margin: 0.75rem 0 !important;
}

.footer-info {
    text-align: center;
    padding: 1rem;
    color: var(--atari-muted);
    font-size: 0.9rem;
    margin-top: 2rem;
    font-family: 'VT323', monospace !important;
}

/* Gradio component overrides */
.block label, .block-title {
    color: var(--atari-text) !important;
    font-family: 'VT323', monospace !important;
}

input, textarea, select {
    background: var(--atari-surface) !important;
    border: 2px solid var(--atari-border) !important;
    color: var(--atari-text) !important;
}

.prose, .prose p, .markdown-text, span {
    color: var(--atari-text) !important;
}

/* Tab styling - arcade cabinet labels */
.tabs {
    border: 2px solid var(--atari-border) !important;
    border-radius: 6px !important;
}

/* Scrollbar styling */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

::-webkit-scrollbar-track {
    background: var(--atari-bg);
}

::-webkit-scrollbar-thumb {
    background: var(--atari-border-strong);
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: var(--atari-phosphor-dim);
}
"""

# Gradio theme configuration
atari_theme = gr.themes.Base(
    primary_hue="emerald",
    secondary_hue="amber",
    neutral_hue="slate",
    font=("VT323", "monospace"),
    font_mono=("VT323", "monospace"),
).set(
    body_background_fill="#0a0a0f",
    body_background_fill_dark="#0a0a0f",
    block_background_fill="#141420",
    block_background_fill_dark="#141420",
    block_border_color="#2a2a3a",
    block_border_color_dark="#2a2a3a",
    block_label_text_color="#e0e0e0",
    block_label_text_color_dark="#e0e0e0",
    block_title_text_color="#e0e0e0",
    block_title_text_color_dark="#e0e0e0",
    body_text_color="#e0e0e0",
    body_text_color_dark="#e0e0e0",
    body_text_color_subdued="#909090",
    body_text_color_subdued_dark="#909090",
    input_background_fill="#141420",
    input_background_fill_dark="#141420",
    input_border_color="#2a2a3a",
    input_border_color_dark="#2a2a3a",
    button_primary_background_fill="#141420",
    button_primary_background_fill_hover="#1a1a28",
    button_primary_text_color="#7cd0ac",
    button_secondary_background_fill="#141420",
    button_secondary_background_fill_hover="#1a1a28",
    button_secondary_text_color="#909090",
)


def get_atari_css() -> str:
    """Return the Atari theme CSS string."""
    return ATARI_CSS


def get_atari_theme() -> gr.themes.Theme:
    """Return the Atari Gradio theme."""
    return atari_theme
