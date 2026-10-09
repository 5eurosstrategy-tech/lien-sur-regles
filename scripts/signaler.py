"""Signale automatiquement les sites nouvellement bloqués (aucune donnée d'utilisateur : uniquement l'adresse du site piégé).
- antiphishing.ch (Office fédéral de la cybersécurité OFCS)
- Netcraft (alimente les listes de blocage des navigateurs)
"""
import json, subprocess, sys, urllib.request, urllib.parse

def block(ref):
    try: return set(json.loads(subprocess.check_output(["git", "show", f"{ref}:regles.json"]))["block"])
    except Exception: return set()

before, after = sys.argv[1], sys.argv[2]
new = sorted(block(after) - block(before))
print(f"{len(new)} nouveau(x) site(s) à signaler")
ok = 0
for d in new:
    url = d if d.startswith("http") else f"https://{d}/"
    try:
        r = urllib.request.urlopen(urllib.request.Request("https://www.antiphishing.ch/fr/index.php",
            data=urllib.parse.urlencode({"url": url}).encode(), headers={"User-Agent": "StopArnaques-veille/1.0"}), timeout=30)
        body = r.read().decode("utf-8", "ignore")
        good = "enregistr" in body
        print(("OK " if good else "?? ") + "antiphishing.ch " + url); ok += good
    except Exception as e: print("ÉCHEC antiphishing.ch", url, e)
    try:
        req = urllib.request.Request("https://report.netcraft.com/api/v3/report/urls",
            data=json.dumps({"email": "5euros.strategy@gmail.com", "urls": [{"url": url, "country": "CH"}]}).encode(),
            headers={"Content-Type": "application/json"})
        print("OK netcraft", url, urllib.request.urlopen(req, timeout=30).status)
    except Exception as e: print("ÉCHEC netcraft", url, e)
print(f"Terminé : {ok}/{len(new)} confirmés par antiphishing.ch")
