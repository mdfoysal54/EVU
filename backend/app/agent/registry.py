from __future__ import annotations

from typing import Dict, Iterable, List, Optional

from .profiles import AgentProfile


class AgentRegistry:
    """
    Runtime registry for EVU agents.

    Later this can be backed by PostgreSQL, Redis, or a distributed
    service registry without changing the public API.
    """

    def __init__(self) -> None:
        self._agents: Dict[str, AgentProfile] = {}

    def register(
        self,
        agent: AgentProfile,
    ) -> AgentProfile:
        agent.touch()

        self._agents[agent.agent_id] = agent

        return agent

    def unregister(
        self,
        agent_id: str,
    ) -> bool:
        return (
            self._agents.pop(agent_id, None)
            is not None
        )

    def get(
        self,
        agent_id: str,
    ) -> Optional[AgentProfile]:
        return self._agents.get(agent_id)

    def get_by_name(
        self,
        name: str,
    ) -> Optional[AgentProfile]:
        for agent in self._agents.values():
            if agent.name == name:
                return agent

        return None

    def find_by_role(
        self,
        role: str,
    ) -> List[AgentProfile]:
        return [
            agent
            for agent in self._agents.values()
            if agent.role == role and agent.enabled
        ]

    def find_by_capability(
        self,
        capability: str,
    ) -> List[AgentProfile]:
        agents = [
            agent
            for agent in self._agents.values()
            if agent.enabled and agent.has_capability(capability)
        ]

        return sorted(
            agents,
            key=lambda agent: agent.capability_score(
                capability
            ),
            reverse=True,
        )

    def list(
        self,
        enabled_only: bool = False,
    ) -> List[AgentProfile]:
        agents = list(self._agents.values())

        if enabled_only:
            agents = [
                agent
                for agent in agents
                if agent.enabled
            ]

        return agents

    def enable(
        self,
        agent_id: str,
    ) -> AgentProfile:
        agent = self._require(agent_id)
        agent.enabled = True
        agent.touch()

        return agent

    def disable(
        self,
        agent_id: str,
    ) -> AgentProfile:
        agent = self._require(agent_id)
        agent.enabled = False
        agent.touch()

        return agent

    def _require(
        self,
        agent_id: str,
    ) -> AgentProfile:
        agent = self.get(agent_id)

        if agent is None:
            raise KeyError(
                f"Agent not found: {agent_id}"
            )

        return agent

    def __len__(self) -> int:
        return len(self._agents)