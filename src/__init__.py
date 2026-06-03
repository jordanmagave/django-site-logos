"""Núcleo da aplicação seguindo arquitetura hexagonal.

Camadas:
- domain: regras de negócio puras (sem dependências externas)
- ports: protocolos (interfaces) que o domínio espera
- use_cases: orquestração dos casos de uso
- adapters: implementações concretas (Django, Segment, MaxMind, etc.)
"""
