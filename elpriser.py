from nordpool import elspot
from datetime import datetime
import requests
# Hent spotpriser for DK1 (Vestdanmark)
prices_spot = elspot.Prices()
today = prices_spot.hourly(areas=["DK1"])

# Funktion til at beregne netto salgspris (øre/kWh)
def beregn_salgspris(spotpris_øre: float) -> float:
    """
    Beregner netto salgspris i øre/kWh for overskudsproduktion.
    """
    indfoedning_cerius = 0.56   # øre/kWh
    balancetarif = 0.24         # øre/kWh
    samlet_fradrag = indfoedning_cerius + balancetarif
    return round(spotpris_øre - samlet_fradrag, 2)


def hent_eur_dkk_kurs():
    """
    Henter den seneste EUR til DKK valutakurs fra ECB.
    Returnerer kursen som float.
    """
    url = "https://data-api.ecb.europa.eu/service/data/EXR/D.DKK.EUR.SP00.A?format=jsondata"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        # Naviger i JSON-strukturen for at finde den seneste kurs
        observations = data['dataSets'][0]['series']['0:0:0:0:0']['observations']
        # Hent den seneste observation
        seneste_tidspunkt = sorted(observations.keys())[-1]
        seneste_kurs = observations[seneste_tidspunkt][0]
        return float(seneste_kurs)
    except Exception as e:
        print(f"Fejl ved hentning af eurokurs: {e}")
        return None
# Valutakurs og konverteringsfaktor
EUR_to_DKK = hent_eur_dkk_kurs()
if EUR_to_DKK is None:
    # Håndter fejl, f.eks. ved at bruge en standardværdi eller afslutte scriptet
    EUR_to_DKK = 7.45  # Standardværdi som fallback


print("Tidspunkt | Spotpris (øre/kWh) | Salgspris (øre/kWh)")
print("-" * 50)
for hour_data in today['areas']['DK1']['values']:
    time = hour_data['start']
    eur_per_mwh = hour_data['value']
    
    # Konverter EUR/MWh → DKK/kWh → øre/kWh
    spotpris_øre = (eur_per_mwh * EUR_to_DKK) / 10
    
    salgspris = beregn_salgspris(spotpris_øre)
    print(f"{time.strftime('%H:%M')}     | {spotpris_øre:.2f}           | {salgspris:.2f}")
