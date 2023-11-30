import os

from threadagent.project_loader import ProjectLoader, load_project_config


class TestProjectLoader:
    def test_load_config(self):
        current_path = os.path.abspath(os.path.dirname(__file__))
        path = os.path.join(current_path, "agents", "simple_chatbot.toml")
        project_config = load_project_config(path)

        project = ProjectLoader(project_config).load_project()
        assert project.name == "simple_chatbot"

    def test_load_project(self):
        current_path = os.path.abspath(os.path.dirname(__file__))
        path = os.path.join(current_path, "agents", "simple_chatbot.toml")
        project_config = load_project_config(path)

        project = ProjectLoader(project_config).load_project()
        assert project.name == "simple_chatbot"
        assert project.agents["foo"].name == "foo"
        assert project.entry.name == "foo"

    def test_load_workflow(self):
        current_path = os.path.abspath(os.path.dirname(__file__))
        path = os.path.join(current_path, "agents", "picture_book_writer.toml")
        project_config = load_project_config(path)

        project = ProjectLoader(project_config).load_project()
        assert project.name == "script_writer"
        assert project.agents["script_writer"].name == "script_writer"
        assert project.entry.name == "starter"

