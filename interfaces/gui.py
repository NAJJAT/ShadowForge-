import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import asyncio

class RedTeamGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("RedTeam AI - Security Testing Framework")
        self.root.geometry("900x600")
        self.root.configure(bg='#1a1a2e')
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Tab 1: Scanner
        self.scanner_tab = tk.Frame(self.notebook, bg='#1a1a2e')
        self.notebook.add(self.scanner_tab, text="🔍 Scanner")
        self._build_scanner_tab()
        
        # Tab 2: Exploit Builder
        self.exploit_tab = tk.Frame(self.notebook, bg='#1a1a2e')
        self.notebook.add(self.exploit_tab, text="⚡ Exploit Builder")
        self._build_exploit_tab()
        
        # Tab 3: Status
        self.status_tab = tk.Frame(self.notebook, bg='#1a1a2e')
        self.notebook.add(self.status_tab, text="📊 Status")
        self._build_status_tab()
        
        # Tab 4: Identity
        self.identity_tab = tk.Frame(self.notebook, bg='#1a1a2e')
        self.notebook.add(self.identity_tab, text="🆔 Identity")
        self._build_identity_tab()
        
        self.root.mainloop()
    
    def _build_scanner_tab(self):
        # URL input
        tk.Label(self.scanner_tab, text="Target URL:", fg='white', bg='#1a1a2e').pack(pady=5)
        self.url_entry = tk.Entry(self.scanner_tab, width=70, bg='#2a2a3e', fg='white')
        self.url_entry.pack(pady=5)
        
        # Scan button
        self.scan_btn = tk.Button(self.scanner_tab, text="Start Scan", command=self.start_scan, bg='#00cc88', fg='black')
        self.scan_btn.pack(pady=10)
        
        # Results area
        self.results_text = scrolledtext.ScrolledText(self.scanner_tab, height=20, bg='#0a0a1e', fg='#00ffcc')
        self.results_text.pack(fill='both', expand=True, padx=10, pady=10)
    
    def _build_exploit_tab(self):
        tk.Label(self.exploit_tab, text="Vulnerability Type:", fg='white', bg='#1a1a2e').pack(pady=5)
        self.vuln_type = ttk.Combobox(self.exploit_tab, values=['sql_injection', 'command_injection', 'xss', 'lfi'])
        self.vuln_type.pack(pady=5)
        
        tk.Label(self.exploit_tab, text="Target URL:", fg='white', bg='#1a1a2e').pack(pady=5)
        self.target_entry = tk.Entry(self.exploit_tab, width=70, bg='#2a2a3e', fg='white')
        self.target_entry.pack(pady=5)
        
        tk.Label(self.exploit_tab, text="Parameter:", fg='white', bg='#1a1a2e').pack(pady=5)
        self.param_entry = tk.Entry(self.exploit_tab, width=30, bg='#2a2a3e', fg='white')
        self.param_entry.pack(pady=5)
        
        self.build_btn = tk.Button(self.exploit_tab, text="Build Exploit", command=self.build_exploit, bg='#ff8844', fg='black')
        self.build_btn.pack(pady=10)
        
        self.exploit_text = scrolledtext.ScrolledText(self.exploit_tab, height=15, bg='#0a0a1e', fg='#ffcc00')
        self.exploit_text.pack(fill='both', expand=True, padx=10, pady=10)
    
    def _build_status_tab(self):
        self.status_text = scrolledtext.ScrolledText(self.status_tab, height=20, bg='#0a0a1e', fg='#00ffcc')
        self.status_text.pack(fill='both', expand=True, padx=10, pady=10)
        self.update_status()
    
    def _build_identity_tab(self):
        self.gen_btn = tk.Button(self.identity_tab, text="Generate New Identity", command=self.generate_identity, bg='#aa44ff', fg='white')
        self.gen_btn.pack(pady=10)
        self.identity_text = scrolledtext.ScrolledText(self.identity_tab, height=15, bg='#0a0a1e', fg='#ffcc00')
        self.identity_text.pack(fill='both', expand=True, padx=10, pady=10)
    
    def start_scan(self):
        def scan():
            from vulnerability_hunter.pattern_matching.web_vuln_scanner import WebVulnerabilityScanner
            import asyncio
            
            url = self.url_entry.get()
            self.results_text.insert(tk.END, f"Scanning {url}...\n")
            
            async def run():
                scanner = WebVulnerabilityScanner()
                return await scanner.scan_url(url, {})
            
            vulns = asyncio.run(run())
            self.results_text.insert(tk.END, f"\nFound {len(vulns)} vulnerabilities:\n")
            for v in vulns:
                self.results_text.insert(tk.END, f"  - {v.name} ({v.severity.value}): {v.description[:80]}\n")
        
        threading.Thread(target=scan).start()
    
    def build_exploit(self):
        from exploit_developer.exploit_builder.from_vulnerability import ExploitBuilder
        
        vuln_info = {
            "type": self.vuln_type.get(),
            "url": self.target_entry.get(),
            "parameter": self.param_entry.get(),
            "os_type": "linux",
        }
        
        builder = ExploitBuilder(simulation_mode=True)
        exploit = builder.build_from_vulnerability(vuln_info)
        
        self.exploit_text.delete(1.0, tk.END)
        self.exploit_text.insert(tk.END, f"Exploit ID: {exploit.id}\n")
        self.exploit_text.insert(tk.END, f"Type: {exploit.exploit_type.value}\n")
        self.exploit_text.insert(tk.END, f"Payload: {exploit.payload}\n\n")
        self.exploit_text.insert(tk.END, "Instructions:\n")
        for inst in exploit.instructions[:5]:
            self.exploit_text.insert(tk.END, f"  - {inst}\n")
    
    def update_status(self):
        from opsec_shield.anonymization.vpn_chain_manager import VPNChainManager
        from self_learning.memory.experience_memory import ExperienceMemory
        
        vpn = VPNChainManager(simulation_mode=True)
        status = vpn.get_chain_status()
        
        memory = ExperienceMemory(simulation_mode=True)
        stats = memory.get_statistics()
        
        self.status_text.delete(1.0, tk.END)
        self.status_text.insert(tk.END, f"VPN Chain: {'Connected' if status['is_connected'] else 'Disconnected'}\n")
        self.status_text.insert(tk.END, f"Exit IP: {status['exit_ip']}\n")
        self.status_text.insert(tk.END, f"Experience Memory: {stats['total']} records\n")
        self.status_text.insert(tk.END, f"Success Rate: {stats['success_rate']*100:.1f}%\n")
        self.status_text.insert(tk.END, f"Top Techniques: {stats.get('top_techniques', [])[:3]}\n")
        
        self.root.after(5000, self.update_status)
    
    def generate_identity(self):
        from opsec_shield.synthetic_identity.identity_generator import SyntheticIdentity
        
        generator = SyntheticIdentity()
        identity = generator.generate()
        
        self.identity_text.delete(1.0, tk.END)
        self.identity_text.insert(tk.END, f"Name: {identity.name}\n")
        self.identity_text.insert(tk.END, f"Email: {identity.email}\n")
        self.identity_text.insert(tk.END, f"Phone: {identity.phone}\n")
        self.identity_text.insert(tk.END, f"BTC: {identity.crypto_wallets['bitcoin'][:30]}...\n")
        self.identity_text.insert(tk.END, f"XMR: {identity.crypto_wallets['monero'][:30]}...\n")

if __name__ == "__main__":
    RedTeamGUI()