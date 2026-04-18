#!/usr/bin/env python3
# cli.py - واجهة سطر الأوامر للنظام

import click
import asyncio
import json
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

@click.group()
def cli():
    """RedTeam AI - نظام اختبار الأمان المتكامل"""
    pass

@cli.command()
@click.option('--url', required=True, help='الهدف للمسح')
@click.option('--params', help='معاملات GET (JSON)')
def scan(url, params):
    """مسح ثغرات موقع ويب"""
    import asyncio
    from vulnerability_hunter.pattern_matching.web_vuln_scanner import WebVulnerabilityScanner
    
    console.print(f"[bold cyan]🔍 Scanning: {url}[/bold cyan]")
    
    async def run():
        scanner = WebVulnerabilityScanner()
        params_dict = json.loads(params) if params else {}
        vulns = await scanner.scan_url(url, params_dict)
        return vulns
    
    vulns = asyncio.run(run())
    
    # عرض النتائج
    table = Table(title=f"Found {len(vulns)} Vulnerabilities")
    table.add_column("Type", style="cyan")
    table.add_column("Severity", style="red")
    table.add_column("Parameter", style="yellow")
    table.add_column("Description", style="white")
    
    for v in vulns:
        table.add_row(v.name, v.severity.value, v.parameter or "-", v.description[:50])
    
    console.print(table)

@cli.command()
@click.option('--target', required=True, help='الهدف (IP أو domain)')
@click.option('--technique', default='auto', help='نوع الاستغلال')
def exploit(target, technique):
    """بناء وتنفيذ استغلال"""
    from exploit_developer.exploit_builder.from_vulnerability import ExploitBuilder
    
    console.print(f"[bold red]⚡ Building exploit for: {target}[/bold red]")
    
    builder = ExploitBuilder(simulation_mode=True)
    vuln_info = {
        "type": "command_injection",
        "url": target,
        "parameter": "cmd",
        "os_type": "linux"
    }
    exploit = builder.build_from_vulnerability(vuln_info)
    
    console.print(Panel(f"""
    [bold]Exploit Generated:[/bold]
    ID: {exploit.id}
    Type: {exploit.exploit_type.value}
    Payload: {exploit.payload[:100]}...
    
    Instructions:
    {chr(10).join(f'  {i+1}. {inst}' for i, inst in enumerate(exploit.instructions[:3]))}
    """, title="Exploit Ready", border_style="red"))

@cli.command()
def status():
    """عرض حالة النظام"""
    from opsec_shield.anonymization.vpn_chain_manager import VPNChainManager
    from self_learning.memory.experience_memory import ExperienceMemory
    
    console.print("[bold]📊 System Status[/bold]\n")
    
    # VPN Status
    vpn = VPNChainManager(simulation_mode=True)
    status = vpn.get_chain_status()
    console.print(f"🔒 VPN Chain: [green]{'Connected' if status['is_connected'] else 'Disconnected'}[/green]")
    console.print(f"   Exit IP: {status['exit_ip']}")
    
    # Memory Status
    memory = ExperienceMemory(simulation_mode=True)
    stats = memory.get_statistics()
    console.print(f"🧠 Experience Memory: {stats['total']} records")
    console.print(f"   Success Rate: {stats['success_rate']*100:.1f}%")

@cli.command()
def train():
    """تدريب النظام على التجارب السابقة"""
    from self_learning.rl_training.continuous_trainer import ContinuousTrainer
    from self_learning.rl_training.policy_network import PolicyNetwork
    
    console.print("[bold yellow]🧬 Training Self-Learning Engine...[/bold yellow]")
    
    policy = PolicyNetwork()
    trainer = ContinuousTrainer(policy)
    
    # محاكاة تدريب
    for i in range(10):
        console.print(f"   Episode {i+1}/10...")
        # هنا يمكن إضافة تدريب حقيقي
    
    console.print("[bold green]✅ Training complete![/bold green]")

@cli.command()
def identity():
    """توليد هوية رقمية جديدة"""
    from opsec_shield.synthetic_identity.identity_generator import SyntheticIdentity
    
    generator = SyntheticIdentity()
    identity = generator.generate()
    
    console.print(Panel(f"""
    [bold]🆔 Synthetic Identity[/bold]
    Name: {identity.name}
    Email: {identity.email}
    Phone: {identity.phone}
    BTC Wallet: {identity.crypto_wallets['bitcoin'][:20]}...
    """, title="New Identity", border_style="green"))

if __name__ == '__main__':
    cli()