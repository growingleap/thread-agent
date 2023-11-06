import os

from threadagent.project_loader import ProjectLoader


class TestProjectLoader:
    def test_load_config(self):
        current_path = os.path.abspath(os.path.dirname(__file__))
        path = os.path.join(current_path, "agents")

        config = ProjectLoader("simple_chatbot", path).load_project()
        assert config["project"]["name"] == "simple_chatbot"
