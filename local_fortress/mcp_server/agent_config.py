"""
QoreLogic Agent Configuration Loader

Loads agent configuration from ~/.qorelogic/config/agents.json
(or container-mapped equivalent).

This bridges the Dashboard's agent configuration UI to the runtime.
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

# Configuration paths (in order of priority)
CONFIG_PATHS = [
    # 1. Dashboard-saved config (via /api/agents/config -> ledger volume)
    "/app/ledger/config/agents.json",
    # 2. Docker container mount point (legacy)
    "/config/agents.json",
    # 3. Host user directory
    os.path.expanduser("~/.qorelogic/config/agents.json"),
    # 4. Environment variable override
    os.environ.get("QORELOGIC_AGENTS_CONFIG", ""),
]

@dataclass
class AgentConfig:
    """Configuration for LLM-backed agents with hybrid mode support."""
    provider: str = "ollama"
    endpoint: str = "http://localhost:11434/api/generate"
    models: Dict[str, str] = None
    prompts: Dict[str, str] = None
    # Hybrid mode: resolved per-agent configs (from Dashboard)
    agents: Dict[str, Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.models is None:
            self.models = {
                "sentinel": "qwen2.5-coder:7b",
                "judge": "qwen2.5-coder:7b",
                "overseer": "qwen2.5-coder:7b",
                "scrivener": "qwen2.5-coder:7b"
            }
        if self.prompts is None:
            self.prompts = {
                "sentinel": "You are SENTINEL, the Security Analysis Engine. Detect secrets, unsafe functions, injection vulnerabilities, and PII exposure. Return JSON: {verdict, findings, risk_grade}. Fast-fail on critical issues.",
                "judge": "You are JUDGE, the Compliance Arbiter. Validate findings, apply Lewicki-Bunker trust model, enforce citation rules. Return: {verdict, rationale, trust_delta}. L3 requires human oversight.",
                "overseer": "You are OVERSEER, the Strategic Coordinator. Manage multi-agent workflows, monitor trust scores, enforce operational modes. Return: {action, target, context}. Prioritize human alignment.",
                "scrivener": "You are SCRIVENER, the Documentation Engine. Generate accurate docs, validate sources, detect echo content. Return Markdown with metadata: {sources, confidence}. Never fabricate citations."
            }
        if self.agents is None:
            self.agents = {}
    
    def get_model(self, agent_role: str) -> str:
        """Get the model for a specific agent role (checks hybrid mode first)."""
        role = agent_role.lower()
        # Hybrid mode: check agents dict first
        if role in self.agents and self.agents[role].get("model"):
            return self.agents[role]["model"]
        return self.models.get(role, "default")
    
    def get_prompt(self, agent_role: str) -> str:
        """Get the system prompt for a specific agent role (checks hybrid mode first)."""
        role = agent_role.lower()
        if role in self.agents and self.agents[role].get("prompt"):
            return self.agents[role]["prompt"]
        return self.prompts.get(role, "")
    
    def get_endpoint(self, agent_role: str = None) -> str:
        """Get the LLM API endpoint (optionally per-agent in hybrid mode)."""
        if agent_role:
            role = agent_role.lower()
            if role in self.agents and self.agents[role].get("endpoint"):
                return self.agents[role]["endpoint"]
        return self.endpoint
    
    def get_provider(self, agent_role: str = None) -> str:
        """Get the provider (optionally per-agent in hybrid mode)."""
        if agent_role:
            role = agent_role.lower()
            if role in self.agents and self.agents[role].get("provider"):
                return self.agents[role]["provider"]
        return self.provider


class AgentConfigLoader:
    """
    Loads and caches agent configuration.
    
    Configuration is loaded once at startup and can be refreshed via reload().
    """
    
    _instance: Optional['AgentConfigLoader'] = None
    _config: Optional[AgentConfig] = None
    _config_path: Optional[str] = None
    _last_mtime: float = 0
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def load(self, force_reload: bool = False) -> AgentConfig:
        """
        Load configuration from the first available config path.
        
        Args:
            force_reload: If True, bypass cache and reload from disk.
            
        Returns:
            AgentConfig with loaded or default values.
        """
        if self._config and not force_reload:
            # Check if file has been modified
            if self._config_path and os.path.exists(self._config_path):
                current_mtime = os.path.getmtime(self._config_path)
                if current_mtime <= self._last_mtime:
                    return self._config
        
        # Try each config path
        for path in CONFIG_PATHS:
            if path and os.path.exists(path):
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    self._config = AgentConfig(
                        provider=data.get("provider", "ollama"),
                        endpoint=data.get("endpoint", "http://localhost:11434/api/generate"),
                        models=data.get("models", {}),
                        prompts=data.get("prompts", {}),
                        agents=data.get("agents", {})
                    )
                    self._config_path = path
                    self._last_mtime = os.path.getmtime(path)
                    
                    logger.info(f"Loaded agent config from {path}")
                    return self._config
                    
                except (json.JSONDecodeError, IOError) as e:
                    logger.warning(f"Failed to load config from {path}: {e}")
                    continue
        
        # No config found, use defaults
        logger.info("No agents.json found, using default configuration")
        self._config = AgentConfig()
        return self._config
    
    def reload(self) -> AgentConfig:
        """Force reload configuration from disk."""
        return self.load(force_reload=True)
    
    def get_config(self) -> AgentConfig:
        """Get current configuration (loads if not yet loaded)."""
        if self._config is None:
            return self.load()
        return self._config


# Singleton accessor
def get_agent_config() -> AgentConfig:
    """Get the current agent configuration."""
    return AgentConfigLoader().get_config()


def reload_agent_config() -> AgentConfig:
    """Force reload agent configuration from disk."""
    return AgentConfigLoader().reload()
