import os
import tempfile
import pytest
from PIL import Image
from scripts.extract_mascots import normalize_label, extract_mascots, EXPECTED_STATES

def test_normalize_label():
    assert normalize_label("USING TOOLS") == "using_tools"
    assert normalize_label("HELLO") == "hello"
    assert normalize_label("  TRICKY_@_LABEL 123  ") == "tricky__label_123"

def test_expected_states_mapping():
    assert EXPECTED_STATES[0][0] == "IDLE"
    assert EXPECTED_STATES[0][3] == "THINKING"
    assert EXPECTED_STATES[1][4] == "USING TOOLS"
    assert EXPECTED_STATES[2][5] == "SLEEPING"

def create_mock_sprite_sheet(path, cols=6, rows=3, cell_w=50, cell_h=50):
    img = Image.new("RGBA", (cols * cell_w, rows * cell_h), (255, 0, 0, 128))
    img.save(path)

def test_extract_mascots_integration():
    with tempfile.TemporaryDirectory() as temp_dir:
        input_path = os.path.join(temp_dir, "sheet.png")
        output_dir = os.path.join(temp_dir, "extracted")
        
        create_mock_sprite_sheet(input_path, cols=6, rows=3, cell_w=100, cell_h=100)
        
        success = extract_mascots(
            input_path=input_path,
            output_dir=output_dir,
            mode="mascot",
            rows=3,
            cols=6,
            preview=False,
            dry_run=False,
            remove_background=False,
            label_height=20,
            padding=5
        )
        
        assert success is True
        
        # Check files
        files = os.listdir(output_dir)
        assert len(files) == 19  # 18 images + 1 manifest
        assert "manifest.json" in files
        assert "idle.png" in files
        assert "using_tools.png" in files
        
        # Verify transparency (RGBA) and size
        with Image.open(os.path.join(output_dir, "idle.png")) as idle_img:
            assert idle_img.mode == "RGBA"
            assert idle_img.size == (110, 90)
