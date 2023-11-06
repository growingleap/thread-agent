import os
import tomllib


def load_env() -> dict:
    current_path = os.path.abspath(os.path.dirname(__file__))
    env_file = os.path.join(current_path, "config", "env.toml")
    with open(env_file, "rb") as f:
        return tomllib.load(f)


def replace_placeholder(project) -> dict:
    env = load_env()
    project["llm"]["openai"]["api_key"] = env["OPENAI_API_KEY"]
    project["llm"]["openai"]["api_base"] = env["OPENAI_API_BASE"]
    return project

