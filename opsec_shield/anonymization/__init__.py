def __init__(self):
    self.simulation_mode = settings.SIMULATION_MODE
    self.vpn_enabled = settings.VPN_ENABLED
    self.chain_length = settings.VPN_CHAIN_LENGTH
    self.rotation_interval = settings.VPN_ROTATION_INTERVAL_SECONDS
    self.providers = settings.vpn_provider_list
    self.excluded_countries = settings.VPN_EXCLUDED_COUNTRIES