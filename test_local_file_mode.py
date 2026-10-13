from unittest.mock import patch

import pytest

import auditor


@pytest.mark.parametrize("path", ["missing.html", "https://example.com/page"])
def test_file_mode_never_falls_back_to_network(path, capsys):
    with patch("auditor.fetch") as fetch:
        assert auditor.main(["--file", path]) == 2
    fetch.assert_not_called()
    assert "No such local HTML file" in capsys.readouterr().err
