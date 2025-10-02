import os
from pathlib import Path
from dotenv import load_dotenv
import json


load_dotenv()


def get_project_root() -> Path:
    current_path = Path(__file__).resolve()

   
    for parent in current_path.parents:
        if (parent / "pyproject.toml").exists():
            return parent

    return current_path.parent.parent.parent


def resolve_relative_paths(config: dict, project_root: Path) -> dict:
   
    for server_name, server_config in config["mcpServers"].items():
        if "args" in server_config:
            for i, arg in enumerate(server_config["args"]):
                if isinstance(arg, str) and not arg.startswith("${"):
                  
                    if arg.endswith(".py") and not os.path.isabs(arg):
                        
                        absolute_path = project_root / arg
                        if absolute_path.exists():
                            config["mcpServers"][server_name]["args"][i] = str(absolute_path)
                        else:
                            
                            print(f"Warning: Server file not found at {absolute_path}")
                            print(f"Keeping original path: {arg}")

    return config


def resolve_env_vars(config: dict) -> dict:
    
    skipped_servers = []
    for server_name, server_config in config["mcpServers"].items():
        for property in server_config.keys():
            if property == "env":
                for key, value in server_config[property].items():
                    if isinstance(value, str) and value.startswith("${"):
                        env_var_name = value[2:-1]
                        env_var_value = os.environ.get(env_var_name, None)
                        if env_var_value is None or env_var_value == "":
                            print(f"\nEnvironment variable {env_var_name} is not set\n")
                            print(f"Skipping server {server_name}\n")
                            skipped_servers.append(server_name)
                            continue
                        config["mcpServers"][server_name][property][key] = env_var_value
            if property == "args":
                for i, arg in enumerate(server_config[property]):
                    if isinstance(arg, str) and arg.startswith("${"):
                        env_var_name = arg[2:-1]
                        env_var_value = os.environ.get(env_var_name, None)
                        if env_var_value is None or env_var_value == "":
                            print(f"\nEnvironment variable {env_var_name} is not set\n")
                            print(f"Skipping server {server_name}\n")
                            skipped_servers.append(server_name)
                            continue
                        config["mcpServers"][server_name][property][i] = env_var_value

    for server_name in set(skipped_servers):
        del config["mcpServers"][server_name]

    return config


config_file = Path(__file__).parent / "mcp_config.json"
if not config_file.exists():
    raise FileNotFoundError(f"mcp_config.json file {config_file} does not exist")

with open(config_file, "r") as f:
    config = json.load(f)

project_root = get_project_root()

config = resolve_relative_paths(config, project_root)

mcp_config = resolve_env_vars(config)
