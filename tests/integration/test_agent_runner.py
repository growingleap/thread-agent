from threadagent.project_loader import ProjectLoader
from threadagent.project_runner import ProjectRunner
from utils import replace_placeholder


class TestAgentRunner:
    def test_run_simple_chatbot(self, agents_root):
        project = ProjectLoader("simple_chatbot", agents_root).load_project()
        project = replace_placeholder(project)
        runner = ProjectRunner(project)
        result = runner.run("hello")
        assert result is not None

    def test_run_agent_with_tool_terminal(self, agents_root, tmp_path):
        project = ProjectLoader("agent_with_tool_terminal", agents_root).load_project()
        project = replace_placeholder(project)
        runner = ProjectRunner(project)
        runner.run(f"create a file named test.txt in {str(tmp_path)} and write hello world in it")
        p = tmp_path / "test.txt"
        assert p.read_text().strip() == "hello world"

    def test_run_agent_with_type_summarization(self, agents_root):
        project = ProjectLoader("agent_with_type_summarize", agents_root).load_project()
        project = replace_placeholder(project)
        runner = ProjectRunner(project)
        result = runner.run("https://lilianweng.github.io/posts/2023-06-23-agent/")
        assert result is not None
