# Push-Benachrichtigungen mit ntfy

## Produktiver Ist-Stand

- Portainer-Stack und Container: `ntfy`
- öffentliche Adresse: `https://ntfy.sukstorf.de`
- lokaler Port: `8093`
- persistente Daten: `/home/sebastian/docker/ntfy/data`
- Benutzer: `sebastian`
- privates Topic: `schreibprojekte`
- anonymer Zugriff: durch `auth-default-access: deny-all` gesperrt
- iPhone-Push: über die offizielle ntfy-App und `upstream-base-url: https://ntfy.sh`

Der Health-Endpunkt ist absichtlich ohne Anmeldung erreichbar:

```bash
curl https://ntfy.sukstorf.de/v1/health
```

## Portainer-Stack

```yaml
services:
  ntfy:
    image: binwiederhier/ntfy:v2.26.3
    container_name: ntfy
    command: [serve]
    restart: unless-stopped
    init: true
    environment:
      TZ: Europe/Berlin
      NTFY_BASE_URL: https://ntfy.sukstorf.de
      NTFY_CACHE_FILE: /var/lib/ntfy/cache.db
      NTFY_AUTH_FILE: /var/lib/ntfy/auth.db
      NTFY_AUTH_DEFAULT_ACCESS: deny-all
      NTFY_ENABLE_LOGIN: "true"
      NTFY_ENABLE_SIGNUP: "false"
      NTFY_BEHIND_PROXY: "true"
      NTFY_UPSTREAM_BASE_URL: https://ntfy.sh
      NTFY_CACHE_DURATION: 7d
      NTFY_ATTACHMENT_CACHE_DIR: /var/lib/ntfy/attachments
      NTFY_LOG_LEVEL: info
    volumes:
      - /home/sebastian/docker/ntfy/data:/var/lib/ntfy
    ports:
      - "8093:80"
    healthcheck:
      test: ["CMD-SHELL", "wget -q --tries=1 http://localhost:80/v1/health -O - | grep -Eo '\"healthy\"\\s*:\\s*true' || exit 1"]
      interval: 60s
      timeout: 10s
      retries: 3
      start_period: 30s
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"
    networks: [ntfy_net]

networks:
  ntfy_net:
    name: ntfy_net
```

## Eigener Token für den Nachtlauf

Das Skript verwendet nicht das Benutzerpasswort, sondern einen widerrufbaren ntfy-Token. Token
interaktiv erzeugen und anschließend ausschließlich auf dem Homeserver ablegen:

```bash
sudo docker exec -it ntfy ntfy token add sebastian
mkdir -p /home/sebastian/.config/schreibprojekte
chmod 700 /home/sebastian/.config/schreibprojekte
nano /home/sebastian/.config/schreibprojekte/ntfy.env
chmod 600 /home/sebastian/.config/schreibprojekte/ntfy.env
```

Inhalt von `ntfy.env`:

```text
NTFY_TOKEN=tk_HIER_DEN_TOKEN_EINTRAGEN
```

Der Wrapper lädt diese Datei vor `start` und `resume`. Sie gehört niemals in Git, Obsidian oder
das Manuskriptverzeichnis.

## Konfiguration des Schreibprojekts

Die nicht geheime Serverkonfiguration enthält:

```json
"notifications": {
  "ntfy": {
    "enabled": true,
    "base_url": "https://ntfy.sukstorf.de",
    "topic": "schreibprojekte",
    "token_env": "NTFY_TOKEN"
  }
}
```

Der Nachtlauf meldet Start, Wiederaufnahme, jeden abgeschlossenen numerischen Akt, Abbruch und
Abschluss. Nummern `101` bis `199` bilden Akt 1, `201` bis `299` Akt 2 und so weiter. Ein Fehler
beim Versand wird ausschließlich protokolliert und stoppt keine Lektoratsprüfung.

## Test

```bash
source /home/sebastian/.config/schreibprojekte/ntfy.env
curl -H "Authorization: Bearer $NTFY_TOKEN" -H "Title: Homestories" -d "Push-Test" https://ntfy.sukstorf.de/schreibprojekte
```

Das Topic `schreibprojekte` wird in der iPhone-App mit dem selbst gehosteten Server
`https://ntfy.sukstorf.de` abonniert.
