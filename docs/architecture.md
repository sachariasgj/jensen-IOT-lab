# Arkitekturdiagram

Diagrammet visar den färdiga lösninges lokala Docker Compose-miljö, CI-pipeline samt en simpel kubernetes demo.

![Arkitekturdiagram](architecture.png)

Den lokala miljön består av tre simulerade IoT-sensorer, REST API,
PostgreSQL och Redis. Sensorerna skickar mätvärden till vårt API
med hjälp av HTTP POST. PosgreSQL används för persistent historik
medan Redis används som cache för senaste mätvärdet (för varje sensor).

GitHub Actions används för CI och kör tester för att sedan bygga en
Docker-image för vårt API vid push och pull requests.

Kubernetes exemplet bestor av en Service och en Deployment med tre pod-repliker.
Om en Pod försvinner skapar Kubernetes automatiskt en ersättare för att behålla
det önskade antalet repliker, vilket i vårt fall är 3 st repliker.

