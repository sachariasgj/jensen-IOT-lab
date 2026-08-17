# Jensen IoT Platform 

Detta är en IoT-plattform utvecklad som en del av DDM-labben.

Lösningen består av ett REST API byggt med Flask, tre simulerade IoT-sensorer,
PostgreSQL för persistent lagring av mätvärden samt Redis för cache av senaste
mätvärdet.

Projektet körs lokalt med Docker Compose. GitHub Actions används för CI och
projektet innehåller även en Kubernetes-demo med tre repliker av API:t.

## Index

- [Arkitektur](#arkitektur)
- [Verktyg-för-att-köra-projektet](#verktyg-för-att-köra-projektet)
- [Starta-projektet](#starta-projektet)
- [API-endpoints](#api-endpoints)
- [Sensor-simulator](#sensor-simulator)
- [PostgreSQL](#postgresql)
- [Redis-cache](#redis-cache)
- [Tester](#tester)
- [SQL-uppgifter](#sql-uppgifter)
- [CI](#ci)
- [Kubernetes](#kubernetes)
- [Dokumentation](#dokumentation)
- [Begränsningar](#kända-begränsningar)
- [Stoppar-projektet](#stoppa-projektet)

## Arkitektur

Den lokala miljön består av:

- Flask REST API
- Tre simulerade IoT-sensorer
- PostgreSQL
- Redis
- Docker Compose

Sensorerna skickar mätvärden till API:t via `POST /measurements`.
API:t validerar inkommande data innan det lagras i PostgreSQL.

PostgreSQL används för persistent lagring och innehåller historiska mätvärden.
Redis används som cache för senaste mätvärdet för respektive sensor.

Ett arkitekturdiagram och en mer detaljerad beskrivning finns här:
[docs/architecture.md](docs/architecture.md)

## Verktyg för att köra projektet


För att köra projektet behövs:

- Git
- Docker Engine eller Docker Desktop
- Docker Compose
- Minikube och kubectl för Kubernetes-daemon

Python behöver inte installeras lokalt eftersom Python och projektets 
dependencies installeras i Docker-imagen som används för API:t

## Starta projektet

Klona repositoryt och gå sedan till projektets root-mapp.

Bygg och starta sedan samtliga tjänster:

```bash
docker compose up --build -d
```

Kontrollera att tjänsterna körs:

```bash
docker compose ps
```

Dessa tjänster ska startas:

- `api`
- `simulator`
- `db`
- `redis`

API:t exponeras lokalt på:

```text
http://localhost:5001
```

## API endpoints

Några exempel på API:ts endpoints:

| Method | Endpoint | Beskrivning
|---|---|---|
| GET | `/health` | används för att kontrollera att API:t körs |
| GET | `/devices` | Hämtar registrerade sensorer |
| GET | `/measurements` | Hämtar alla mätvärden |
| POST | `/measurements` | Sparar ett nytt mätvärde |
| GET | `/devices/<device_id>/measurements` | Hämtar historik för en sensor |
| GET | `/devices/<device_id>/latest` | Hämtar senaste mätvärdet från den angivna sensorn |
| GET | `/statistics` | Hämtar statistik över mätvärden, ex avg temp, antal sensorer etc. |

Giltiga mätvärden valideras och sparas i PostgreSQL. Ett lyckat POST-anrop
returnerar HTTP-status `201`.

Ogiltig sensordata eller data från en okänd sensor returnerar HTTP-status `400`
och datan sparas inte i databasen.

## Sensor simulator

Simulatorn innehåller tre simulerade IoT-sensorer som skickar mätvärden till API:t.

Simulatorns loggar kan följas med:

```bash
docker compose logs -f simulator
```

Giltiga mätvärden ska ge status `201`. Simulatorn skickar även avsiktligt
ogiltiga mätvärden som ska stoppas av API:ts validering och ge status `400`.

## PostgreSQL

PostgreSQL används för persistent lagring för enheter (sensorer) och historiska
mätvärden.

Databasen använder Docker-volymen `postgres_data`, vilket innebär att 
mätvärden finns kvar efter att containern stängs ner eller startas upp på nytt:

```bash
docker compose down
docker compose up -d
```

För att radera den sparade datan kan miljön tas bort tillsammans med volymerna:

```bash
docker compose down -v
```

## Redis cache

Redis används för att cacha det senaste mätvärdet för varje sensor.

Cache-nycklar använder formatet:

```text
latest:<device_id>
```

Vid hämtning av senaste mätvärdet kontrolleras Redis först. Skulle
vi då få en cache miss hämtas värdet från PostgreSQL databasen och läggs sedan
in i Redis cachen.

Kort sagt är PostgreSQL den enda persistenta datakällan och Redis fungerar i
nuvarande konfiguration endast som cache.

## Tester

Projektets automatiserade tester körs med:

```bash
docker compose exec api python -m pytest -q
```

Testerna verifierar bland annat valideringen av inkommande sensordata.

## SQL-uppgifter

De obligatoriska SQL-frågorna för t.ex antal mätningar,
medeltemperatur och mätningar från de senaste 24 timmarna finns i:

[docs/queries.sql](docs/queries.sql)

## CI

Projektet använder GitHub Actions för CI (Continuous Integration).

Pipelinen körs automatiskt vid `push` och `pull request` och:

1. Checkar ut repositoryt
2. Installerar Python-dependencies
3. Kör testerna med pytest
4. Bygger API:ts Docker-image

Workflow-filen finns i:

`.github/workflows/ci.yml`

## Kubernetes

Projektet innehåller en introducerande Kubernetes-demo för REST API:t.

Minikube startas med:

```bash
minikube start --driver=docker
```

API-imagen byggs direkt i Minikube:

```bash
minikube image build -t jensen-iot-api:lab ./api
```

Deployment och Service skapas med:

```bash
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

För att kontrollera poddarna:

```bash
kubectl get pods
```

Deploymenten är konfigurerad för att använda tre replicas av API:t. Om en pod
tas bort skapar Kubernetes automatiskt en ersättare för att återställa till
det antal replicas vi konfigurerat den för (som nämnt tidigare 3).

Tjänsten kan öppnas med:

```bash
minikube service jensen-iot-api
```

PostgreSQL, Redis och simulatorn ingår inte i kubernetes-daemon utan körs genom
den lokala Docker Compose-miljön.

## Dokumentation

Mer dokumentation finns i `docs/`:

- [Arkitektur](docs/architecture.md)
- [Reflektion](docs/reflection.md)
- [SQL-frågor](docs/queries.sql)
- [Labbguide](docs/lab-guide.md)

## Kända begränsningar

- Kubernetes-daemon distribuerar endast REST API:t. PostgreSQL och Redis
  körs inte i Kubernetes
- Redis används endast som cache för senaste mätvärdet och kan därför inte
  ersätta PostgreSQL om databasen blir otillgänglig.
  
- Projektet använder simulerade sensorer och inte fysisk hårdvara, vilket
  av egen erfarenhet ger falsk trygget när det med simulering fungerar, 
  vilket inte är en garanti att det skulle fungera på samma sätt med riktig
  sensorhårdvara

## Stoppa projektet

Stoppa den lokala Docker Compose-miljön med:

```bash
docker compose down
```

Stoppa Minikube med:

```bash
minikube stop
```
