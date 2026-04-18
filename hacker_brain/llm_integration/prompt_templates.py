"""
Prompt Templates - قوالب الأسئلة للنماذج اللغوية
"""

from typing import Dict, List


class PromptTemplates:
    """قوالب متخصصة لمهام الأمن السيبراني الدفاعي"""

    VULNERABILITY_ANALYSIS = """
    Analyze the following vulnerability:

    Type: {vuln_type}
    Description: {description}
    Context: {context}

    Please provide:
    1. Root cause analysis
    2. Severity assessment
    3. Potential impact
    4. Recommended fix
    """

    SAFE_SECURITY_GUIDANCE = """
    Analyze the following security issue:

    Issue Type: {vuln_type}
    Target System: {target}
    Constraints: {constraints}

    Please provide:
    1. Risk summary
    2. Defensive recommendations
    3. Mitigation steps
    4. Validation steps
    """

    CODE_REVIEW = """
    Review the following {language} code for security issues:

    ```{language}
    {code}
    ```

    List all vulnerabilities found.
    """

    DECISION_ADVICE = """
    Given the current situation:

    Target: {target}
    Defenses: {defenses}
    Available tools: {tools}

    What is the best next defensive action? Explain reasoning.
    """

    @classmethod
    def get_template(cls, name: str) -> str:
        return getattr(cls, name.upper(), cls.VULNERABILITY_ANALYSIS)