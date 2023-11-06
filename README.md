# Thread Agent (TA)

Thread Agent is a Multi-modal Fusion Agents Framework to simplify AI agent development.

## Why Thread Agent?

Large Language Modeling (LLM) is an emerging technology which enables developer to build AI applications efficiently.

However, developing LLM-based applications is still a time-consuming for most programmers and researchers. 
It takes a long time to write code and debug. 

Thread Agent provides a framework to simplify the development of LLM-based applications. 
A configuration can be provided to build a LLM-based application in a few minutes.

## Getting Started

### Quick Start

#### Create a new project

You can create a project with a given name in `new` command, for example, `myproject`:

```shell
ta new <name>
```

Thread agent will ask you some questions to generate a configuration file. After that, `<name>.toml` will be created in your current directory. You can edit this configuration manually to customize your project.

#### Run the Project Once

`run` command is used to run a project with single message. You can run the project with the following command:

```shell
ta run <name> -m"<message>"
```

Thread agent will find `<name>` project configuration file and run the project with the given message.

#### Shell mode

`shell` command is used to run a project with shell mode. You can run the project with the following command:

```shell
ta shell <name>
```

Thread agent will open a shell with `<name>` project configuration file. You can input your messages one by one.

## Development

### Prerequisites
This project utilizes [Poetry](https://python-poetry.org/) v1.6.0+ as a dependency manager.

Install Poetry: **[documentation on how to install it](https://python-poetry.org/docs/#installation)**.

### Install Dependencies

Go into source code directory and run the following command:
```shell
poetry install
```

### Run Thread Agent

You can open a shell with python virtual environment and corresponding dependencies.
```shell
poetry shell
```

Then, you can run `python` directly to run Thread Agent:
```shell
python src/threadagent/app.py new <name>
```

### Lint

Thread Agent use `ruff` as a linter. You can run the following command to check the code:
```shell
poetry run ruff check .
```

### Run Tests

Thread Agent use `pytest` as a test framework. Before you run tests, run the following command to create a local configuration which is required by integration tests:
```shell
cp env.examle.toml env.toml
```

And then, write your own configuration in `env.toml`. 

After your editing, you can run the following command to run all tests:
```shell
poetry run pytest
```