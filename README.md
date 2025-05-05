#USING CONFIG:
from pvninja.config import PVNinjaConfig
cfg = PVNinjaConfig.load()

{
  "broker": "192.168.50.102",
  "port": 1883,
  "username": "myname",
  "password": "mypass",
  "db_dsn": "postgresql://username:password@192.168.50.102:5432/pvninja"
}

 User‑specific config dir	$XDG_CONFIG_HOME/pvninja/config.json
‑ or ~/.config/pvninja/config.json if XDG_CONFIG_HOME is unset	This is the standard Linux location for per‑user app settings.
② Project root	<project‑clone>/config.json	Handy for quick dev runs or CI.