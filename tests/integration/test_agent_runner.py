from utils import load_project


class TestAgentRunner:
    def test_run_simple_chatbot(self, agents_root):
        project = load_project(agents_root, "simple_chatbot")
        result = project.invoke("hello")
        assert result is not None

    def test_run_agent_with_tool_terminal(self, agents_root, tmp_path):
        project = load_project(agents_root, "agent_with_tool_terminal")
        project.invoke(f"create a file named test.txt in {str(tmp_path)} "
                       f"and write hello world in it")
        p = tmp_path / "test.txt"
        assert p.read_text().strip() == "hello world"

    def test_run_agent_with_type_summarization(self, agents_root):
        project = load_project(agents_root, "agent_with_type_summarize")
        result = project.invoke("https://lilianweng.github.io/posts/2023-06-23-agent/")
        assert result is not None

    def test_run_script_writer(self, agents_root):
        project = load_project(agents_root, "picture_book_writer")
        result = project.invoke("Iron Man fights with Sun Wukong because of misunderstanding. "
                                "Finally the misunderstanding is eliminated "
                                "and they become friends")
        assert result is not None
