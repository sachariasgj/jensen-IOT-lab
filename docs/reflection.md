# Reflektionsdokument

1. **Varför ska sensorerna kommunicera med ett API i stället för direkt med PostgreSQL?**

    Fördelen med att sensorerna kommunicerar med ett API istället för direkt med PostgreSQL
    är att man då får ett kontrollerat lager mellan sensorerna och databasen. Det möjligör 
    för validering av inkommande data, fel hantering, och man kan begränsa åtkomsten till databasen.

    Detta gör att sensorerna inte behöver känna till databasens adresss, användare, lösenord eller databasstruktur.
    Det gör det lättare att underhålla, samt göra förändringar i framtiden eftersom sensorerna bara behöver känna till
    API gränssnittet.

2. **Varför ska felaktig sensordata stoppas innan den sparas?**

    Det är ju ganska självklart att felaktig data stoppas...
    Vi vill ju kunna lita på datan som vi sparar i databasen.

3. **Varför passar PostgreSQL för historiska mätvärden?**

    Det passar bra eftersom vi vill att mätdatan ska vara persistent,
    vilket gör att datan finns kvar om vi stänger ner docker och sedan startar den igen.

    Detta ger oss även möjligheten att analysera datan (vilket vi gör genom att t.ex ta avg temp).

4. **Vad händer med lösningen om Redis försvinner?**

    Om redis töms/går ner så förlorar vi bara cachen, så all historisk data finns fortfarande kvar i PostgresSQL databasen.
    Vi kommer även få en cache miss, vilket i vår lösning leder till att senaste mätvärdena hämtas direkt från PostgresSQL databasen.

    Så i kort får vi bara lite högre latency eftersom vi inte har vår redis cache, utan datan måste hela tiden hämtas direkt från 
    PostgresSQL databasen.

5. **Vad händer med lösningen om PostgreSQL försvinner?**

    Om PostgreSQL försvinner får vi betydligt större problem, eftersom den innehåller all historik.
    Vilket då gör att vi inte kan få fram historisk sensordata.

    I bästa fall kan redis eventuellt lagra senaste mätvärdet, men det är inte tillräckligt för att ersätta
    PostgreSQL.

6. **Varför används Docker Compose lokalt?**

    Docker compose används för att starta och koppla ihop projektets tjänster på ett reproducerbart sätt.
    I vårt fall består miljön av API, simulator, PostgreSQL och Redis.

    fördelen med detta är att hela miljön startar tillsammans och tjänsternas nätverk, miljövariabler,
    portar, beroenden och volymer definieras på ett ställe.

    En del utav uppgiften var ju även att köra det lokalt för att verifiera att sensordatan är persistent.

7. **Vad automatiserar din CI-pipeline?**

    Min CI pipeline körs automatiskt vid push och pull request.
    Den checkar ut repositoryt, installerar Python-beroenden fron api/requirements.txt, 
    den kör testerna med hjälp av pytest samt bygger våran API Docker-image. 

    Detta gör att t.ex felaktiga tester eller problem med Docker-bygget automatiskt upptäcks 
    innan ändringarna integreras vidare.

8. **Vad observerade du när du tog bort en Kubernetes Pod?**
    
    Jag såg att podden terminerades i loggen, samt att en ny pod automatiskt startade upp.
    Deploymenten är konfigurerar med tre repliker, vilket innebär att Kubernetes hela
    tiden försöker hålla tre Poddar igång samtidigt. När en försvann upptäckte Kubernetes att det
    faktiska antalet inte längre motsvarade det önskade antalet och skapade därför en ersättare.

    Detta är ett tydligt exempel på self-healing, vilket är en utav Kubernetes styrkor.

9. **Varför kan flera repliker ge högre tillgänglighet?**

    Fördelen med flera repliker är att det då finns flera instanser av samma API tillgängligt samtidigt.
    Om en pod kraschar eller tas bort kan de andra fortsätta att hantera trafik medans Kubernetes startar
    en ersättare. Detta gör att lösningen blir mindre beroende av att en enda pod alltid fungerar.

    I vår labb använder vi oss av 3 st replikas och när jag testade att deleta en pod, fungerade fortfarande vårt API
    precis som det skulle, eftersom de två andra replikasen tog hand om trafiken istället medans Kubernetes startade
    en ny pod.


10. **När hade Kubernetes varit overkill för en lösning?**

    Kubernetes hade varit overkill om man har en liten lösning med få tjänster, låg trafik och små krav
    på scaling eller hög tillgänglighet. T.ex om ett API bara körs på en enda server som enkelt
    kan hanteras av Docker Compose kan Kubernetes innebära mer konfiguration och driftarbete än nyttan
    den ger.

    Den här labben t.ex hade gått att köra utan kubernetes, och vi hade kunnat konfigurerar Docker Compose så att
    den automatiskt startar om/startar upp vid fel eller om API:et går ner. Enda nackdelen med detta är att medans API:et
    är nere så förlorar vi mätdata som skickas, förutsatt att sensorerna inte har en cache samt en check för att se att 
    API:et har tagit emot datan.
