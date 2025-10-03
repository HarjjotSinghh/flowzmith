"""
CLI Commands Configuration Loader

Loads command definitions from the centralized JSON configuration file.
This ensures consistency between the Python CLI and the frontend.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class CommandField:
    name: str
    label: str
    type: str
    required: bool
    placeholder: Optional[str] = None
    options: Optional[List[Dict[str, str]]] = None
    default_value: Optional[Any] = None
    help_text: Optional[str] = None


@dataclass
class CommandStep:
    id: str
    title: str
    description: Optional[str]
    fields: List[CommandField]


@dataclass
class CLICommand:
    id: str
    name: str
    description: str
    icon: str
    category: str
    requires_input: bool
    endpoint: Optional[str] = None
    method: Optional[str] = None
    streaming: bool = False
    redirect_to: Optional[str] = None
    steps: Optional[List[CommandStep]] = None


@dataclass
class CommandCategory:
    id: str
    label: str
    color: str


class CommandsConfig:
    """Loads and provides access to CLI commands configuration."""
    
    def __init__(self, config_path: Optional[Path] = None):
        if config_path is None:
            # Default to config/cli-commands.json relative to this file
            config_path = Path(__file__).parent.parent / "config" / "cli-commands.json"
        
        self.config_path = config_path
        self._config = self._load_config()
        self._commands = self._parse_commands()
        self._categories = self._parse_categories()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load the JSON configuration file."""
        with open(self.config_path, 'r') as f:
            return json.load(f)
    
    def _parse_commands(self) -> List[CLICommand]:
        """Parse commands from configuration."""
        commands = []
        for cmd_data in self._config.get('commands', []):
            steps = None
            if 'steps' in cmd_data:
                steps = [
                    CommandStep(
                        id=step['id'],
                        title=step['title'],
                        description=step.get('description'),
                        fields=[
                            CommandField(
                                name=field['name'],
                                label=field['label'],
                                type=field['type'],
                                required=field['required'],
                                placeholder=field.get('placeholder'),
                                options=field.get('options'),
                                default_value=field.get('defaultValue'),
                                help_text=field.get('helpText')
                            )
                            for field in step['fields']
                        ]
                    )
                    for step in cmd_data['steps']
                ]
            
            command = CLICommand(
                id=cmd_data['id'],
                name=cmd_data['name'],
                description=cmd_data['description'],
                icon=cmd_data['icon'],
                category=cmd_data['category'],
                requires_input=cmd_data['requiresInput'],
                endpoint=cmd_data.get('endpoint'),
                method=cmd_data.get('method'),
                streaming=cmd_data.get('streaming', False),
                redirect_to=cmd_data.get('redirectTo'),
                steps=steps
            )
            commands.append(command)
        
        return commands
    
    def _parse_categories(self) -> List[CommandCategory]:
        """Parse categories from configuration."""
        return [
            CommandCategory(
                id=cat['id'],
                label=cat['label'],
                color=cat['color']
            )
            for cat in self._config.get('categories', [])
        ]
    
    @property
    def version(self) -> str:
        """Get configuration version."""
        return self._config.get('version', '1.0.0')
    
    @property
    def commands(self) -> List[CLICommand]:
        """Get all commands."""
        return self._commands
    
    @property
    def categories(self) -> List[CommandCategory]:
        """Get all categories."""
        return self._categories
    
    def get_command_by_id(self, command_id: str) -> Optional[CLICommand]:
        """Get a command by its ID."""
        for cmd in self._commands:
            if cmd.id == command_id:
                return cmd
        return None
    
    def get_commands_by_category(self, category: str) -> List[CLICommand]:
        """Get all commands in a category."""
        return [cmd for cmd in self._commands if cmd.category == category]
    
    def get_category_by_id(self, category_id: str) -> Optional[CommandCategory]:
        """Get a category by its ID."""
        for cat in self._categories:
            if cat.id == category_id:
                return cat
        return None


# Global instance
_config_instance: Optional[CommandsConfig] = None


def get_commands_config() -> CommandsConfig:
    """Get the global commands configuration instance."""
    global _config_instance
    if _config_instance is None:
        _config_instance = CommandsConfig()
    return _config_instance


# Convenience functions
def get_all_commands() -> List[CLICommand]:
    """Get all available commands."""
    return get_commands_config().commands


def get_command_by_id(command_id: str) -> Optional[CLICommand]:
    """Get a command by its ID."""
    return get_commands_config().get_command_by_id(command_id)


def get_commands_by_category(category: str) -> List[CLICommand]:
    """Get all commands in a category."""
    return get_commands_config().get_commands_by_category(category)


def get_all_categories() -> List[CommandCategory]:
    """Get all categories."""
    return get_commands_config().categories
