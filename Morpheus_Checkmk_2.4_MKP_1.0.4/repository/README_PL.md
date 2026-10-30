# HPE Morpheus → Checkmk 2.4 — MKP 1.0.4

Autor: **Pawel Wladzinski**
Kontakt: **pawel.wladzinski@vayana.pl**

Wydanie 1.0.0 zmienia nazwę widoczną pakietu/reguły i metadane autora. Logika monitorowania jest taka sama jak w 0.2.2. Nazwy usług i wewnętrzny identyfikator reguły `morpheus` pozostają zgodne z poprzednimi wersjami; zapisane URL, tokeny, prefiksy i filtry nie są zmieniane.

Uniwersalna integracja REST API dla Morpheusa. Pakiet nie zawiera adresu klienta, tokenu, konta, nazwy site ani konfiguracji DCD. URL i token są wymagane w każdej regule. Domyślne timeouty, progi i prefiks `morpheus-vm-` są neutralnymi ustawieniami technicznymi. Nie zmieniono nazw ani kluczy istniejących reguł, dlatego zapisane ustawienia z wersji 0.1.0 pozostają użyteczne po aktualizacji.

Kod oparto na odpowiedziach Morpheus 9.1.0.1. Wersja 0.1.0 działała na Checkmk **2.4.0p26 CME**; wersja 1.0.4 wymaga walidacji i testu na docelowym site. Testy lokalne i publiczne API nie zastępują testu pełnego środowiska.

## Zmiana 1.0.3: czytelne nazwy usług infrastruktury

Unikalne nazwy klastra, hypervisora i datastore nie zawierają już `[ID]`. Chmury są identyfikowane nazwą, np. `Morpheus Cloud Example-HVM`. ID obiektu i chmury są nadal w danych kolektora i szczegółach usług (`notice`), poza głównym podsumowaniem przy stanie OK.

Jeżeli nazwa powtarza się w danym rodzaju obiektów, kolektor dodaje nazwę chmury, potem w razie potrzeby ID obiektu i chmury. Kolejność obiektów w odpowiedzi API nie wpływa na nazwy. Kolizja, której nie można rozstrzygnąć tymi polami, daje błąd zamiast przypisania danych do niewłaściwego obiektu. Dodanie/usunięcie obiektu o takiej samej nazwie lub zmiana nazwy obiektu może zmienić item usługi i wymagać discovery.

Ta wersja świadomie zmienia itemy istniejących usług infrastruktury/chmur. Po instalacji wykonaj **Service discovery → Rescan** na hoście integracji API, zaakceptuj nowe usługi i usuń stare usługi jako vanished, potem **Activate changes**. Zastosuj tę zmianę najpierw w środowisku testowym. Historia wykresów poprzednich nazw nie jest automatycznie przenoszona do nowych usług. Nie ma automatycznej migracji ani kasowania starych plików RRD.

Sprawdź reguły z warunkami itemów/nazw usług: dopasowania zawierające stare `[ID]` lub numer chmury wymagają zmiany na nowe nazwy. VM piggyback, nazwy hostów VM, prefiksy, URL, tokeny, filtry i konfiguracja DCD pozostają takie same. Wcześniejsze poprawki cache VM i wykresów są zachowane.

Przykłady:

- `Morpheus Cluster HVM-CLUSTER1 CPU`
- `Morpheus Hypervisor HYPERVISOR1 Memory`
- `Morpheus Datastore HVM_DATASTORE01 Usage`
- `Morpheus Hardware HYPERVISOR1`
- `Morpheus Cloud Example-HVM`

## Poprawki 1.0.2: stabilność metryk VM i wykresy

### Ostatni kompletny pomiar VM

Próbki Morpheus 9.1 pokazują przeplatanie pełnych `server.stats` niepełnymi statystykami (CPU Ready i pojemności bez zużycia). Pole root `stats` zwraca wtedy zera CPU/RAM bez własnego timestampu. Pakiet nie traktuje tych zer jako zastępczego pomiaru.

Po pierwszym kompletnym odczycie VM kolektor zapisuje prywatny snapshot z oryginalnym `stats.ts`. Gdy lista i próba odczytu szczegółów nie zapewniają kompletnego pomiaru, wykorzystuje cały poprzedni snapshot i pokazuje **Statistics source: last complete snapshot (current API metrics incomplete)**. Nie miesza pól z różnych próbek. Wiek dotyczy rzeczywistego czasu źródłowego; nie jest zerowany przy odczycie cache. Brak pierwszego kompletnego pomiaru nadal daje UNKNOWN.

Domyślnie snapshot awaryjny daje **WARN od 120 s / CRIT od 900 s**, licząc od oryginalnego timestampu pomiaru. Obowiązuje bardziej restrykcyjny z normalnego i awaryjnego limitu wieku. Limity cache są w **Morpheus VM metric levels** jako **Warning/Critical cached VM snapshot age in seconds**. Po osiągnięciu CRIT check nie publikuje wartości zużycia jako bieżących. Wartość CPU lub RAM przekraczająca próg nadal alarmuje również w czasie korzystania ze snapshotu.

Cache jest zapisywany atomowo jako plik 0600 w `$OMD_ROOT/var/check_mk/morpheus_vm_stats/<identity>/<vm-id>.json`; katalog identity ma 0700. Oddzielne cache dla adresów appliance, tokenów i site. Zawiera tylko wybrane pola metryk oraz pojemności VM; brak haseł i pełnych konfiguracji. Zmiana przydziału CPU/RAM/storage blokuje użycie poprzedniego snapshotu; zaobserwowane wyłączenie VM usuwa jej snapshot. Bez `OMD_ROOT` cache jest wyłączony. Snapshoty usuniętych VM nie tworzą hostów ani danych piggyback; emitowany jest wyłącznie bieżący inwentarz API. Pliki takich usuniętych VM nie są automatycznie sprzątane.

### Główne i pomocnicze wykresy

- Jawne szablony wykresów dla CPU, RAM, storage, datastore, multipath, hypervisorów, klastrów, hardware, sensorów oraz appliance/API. W Checkmk 2.4 jawne szablony są przetwarzane przed automatycznymi wykresami pozostałych metryk, dzięki czemu wykres wieku danych jest pomocniczy.
- 43 metryki z czytelnymi nazwami i jednostkami, 30 szablonów wykresów oraz 12 Perf-O-Meterów. CPU/RAM i zajętość datastore mają procenty; czas ma sekundy; pojemności są prezentowane w jednostkach binarnych.
- Dotychczasowe metryki `*_mib` zachowują nazwy i wartości historyczne. Wyrażenia wykresów mnożą je przez 1048576, aby poprawnie pokazywać MiB/GiB jako jednostki bajtowe. Nie ma migracji ani zmiany skali istniejących RRD.
- CPU VM ma otwartą górną skalę i nie jest ograniczany do 100%. Progi WARN/CRIT na wykresach procentowych pochodzą z metryk checka.
- VM storage pokazuje wykorzystanie/pojemność raportowaną przez API, a nie filesystemy gościa. Perf-O-Meter storage przedstawia stosunek tych danych; nie wprowadza nowych progów ani alarmów zajętości filesystemów.
- Po aktualizacji, jeśli GUI zachowuje stare definicje, uruchom jako użytkownik site `omd restart apache` i odśwież stronę. Sprawdź docelowe GUI po wdrożeniu; lokalna walidacja API nie zastępuje testu renderowania w działającej instancji Checkmk.

## Poprawki 1.0.1: metryki VM

- CPU VM zachowuje surowe `stats.cpuUsage` z API również powyżej 100%. Morpheus może raportować CPU w skali obejmującej wiele rdzeni. Wtyczka nie dzieli wartości przez vCPU ani nie ogranicza ich do 100%. Dotychczasowy limit powodował UNKNOWN przy odczycie 108,37%.
- Progi CPU odnoszą się do tej samej skali API: domyślne WARN 90 / CRIT 95 oznaczają, że 108,37% nadal jest alarmem CRIT. W regule **Morpheus VM metric levels** można teraz podać poziomy powyżej 100. Taką regułę ogranicz do item `CPU` i odpowiednich hostów. Dobierz poziomy po sprawdzeniu sposobu liczenia CPU przez danego providera; nie zakładaj identycznej skali wszystkich chmur ani metryk z/bez agenta.
- Przy niepełnych statystykach włączonej VM kolektor próbuje GET `/api/servers/{id}`. Wybiera cały snapshot szczegółowy tylko wtedy, gdy zawiera więcej prawidłowych grup CPU/RAM/storage. Zachowuje oryginalny timestamp i nie miesza pól różnych pomiarów.
- Dodatkowe odczyty są ograniczone do 10 VM na cykl i dostępnego budżetu czasu. Niepowodzenie zapytania szczegółowego nie usuwa VM z inwentarza i nie przerywa wymaganych danych platformy/VM.
- Brak metryk w obu endpointach nadal daje UNKNOWN. Ten mechanizm może ograniczyć skutki okresowych braków, ale nie gwarantuje ich usunięcia. Świeży `stats.ts` nie stanowi dowodu kompletności metryk. W 1.0.1 nie było cache zużycia VM; mechanizm 1.0.2 opisano powyżej.
- Źródło `stats_source` oraz wynik próby `stats_detail_status` są widoczne w danych kolektora. Przy użyciu szczegółów usługa pokazuje źródło w podsumowaniu.
- Zerowa wartość `usedMemory` jest nadal wyświetlana jako wartość podana przez API. Przy rozłączonym agencie gościa nie interpretuj jej jako potwierdzenia zerowego użycia RAM. Dokładny RAM i filesystemy gościa monitoruj agentem OS.
- Nie zmienia się nazewnictwo hostów, konfiguracja DCD, URL, token ani filtry. Stary host po zmianie nazwy VM wymaga osobnej weryfikacji i uporządkowania w Setup.

## Obsługa okresowego braku sensorów (od 0.2.2)

Przy okresowym braku sensorów w liście hypervisorów kolektor odczytuje `/api/servers/{id}`. Jeśli również tam brak sensorów, używa ostatniego poprawnego pomiaru hardware, z zachowaniem jego pierwotnego `stats.ts`. Źródło danych jest jawnie pokazane w usłudze. Cache jest prywatny dla site, adresu appliance i konta/tokenu; zawiera tylko wybrane pola sensorów. Jest zapisywany atomowo z prawami 0600 w `$OMD_ROOT/var/check_mk/morpheus_hardware/`. Bez `OMD_ROOT` cache jest wyłączony; nadal działa zapytanie szczegółowe.

Nowa reguła **Morpheus hardware data freshness** ma domyślne progi **WARN 120 s / CRIT 900 s**. Dotyczy podsumowania i szczegółowych sensorów. Bieżący timestamp CPU/RAM nie odmładza pomiaru hardware. Brak jakiegokolwiek poprawnego pomiaru nadal daje UNKNOWN. Po krytycznym wieku check nie publikuje odczytów jako aktualnych. Nie zmienia się sposób zbierania metryk VM, datastore, CPU ani RAM. Przy zmianie tokenu odrębna historia cache zaczyna się od nowa.

## Zachowana poprawka statusu klastra

Status klastra `syncing` jest traktowany jako przejściowy stan OK. Nadal obowiązują progi wieku ostatniej synchronizacji i ocena członków klastra. Nie zmieniono mapowania statusów hypervisorów/datastore. Nieznane statusy nadal dają UNKNOWN, a `error` — CRIT.

## Zakres wersji 0.2.x

Nowe usługi pojawiają się **na hoście źródłowym integracji API**, bez tworzenia hostów DCD:

| Usługi | Zakres |
|---|---|
| Morpheus Infrastructure collection | Liczby obiektów i błędy nowych endpointów |
| Morpheus Datastore … State | Online, active, status, maintenance, stan lokalizacji |
| Morpheus Datastore … Usage | Pojemność, zajęte i wolne miejsce, procent zajętości, wykresy |
| Morpheus Datastore … Multipath | Liczba aktywnych/wszystkich/uszkodzonych ścieżek, jeśli API je raportuje |
| Morpheus Hypervisor … State | Status, zasilanie, maintenance, członkostwo |
| Morpheus Hypervisor … CPU / Memory | Zużycie i aktualność statystyk |
| Morpheus Hardware … | Zbiorczy stan sensorów sprzętu |
| Morpheus Cluster … State | Status, synchronizacja, członkowie, informacja o HA |
| Morpheus Cluster … CPU / Memory | Średnia CPU i pamięć z workerStats |
| Morpheus Sensor … | Opcjonalne indywidualne sensory sprzętowe i metryki odczytów |

Pozostają usługi platformy i chmur oraz istniejący piggyback VM. Nowa wersja nie zmienia domyślnej tożsamości VM ani ich nazw hostów.

Na danych testowych: **35 dodatkowych usług infrastruktury**, czyli około **46 usług na hoście API** razem z 11 wcześniejszymi. VM mają dodatkowe usługi na własnych hostach. Włączenie szczegółowych sensorów dodaje w przykładowych danych 440 usług; opcja jest domyślnie wyłączona.

## Aktualizacja z wcześniejszych wersji

1. Rozpakuj ZIP. Plik instalacyjny znajduje się w `package/morpheus-1.0.4.mkp`.
2. W GUI Checkmk: **Setup → Maintenance → Extension packages**, wgraj nowy MKP i włącz wersję 1.0.4.
3. Jako użytkownik site wykonaj:

```bash
cmk --version
cmk-validate-plugins
```

Zgłoszony wcześniej problem `netapp_eseries_drives` dotyczy innego pakietu. Nowe błędy odwołujące się do `morpheus` wymagają poprawienia przed aktywacją konfiguracji.

Alternatywa CLI jako użytkownik site, z plikiem MKP dostępnym w jego katalogu domowym:

```bash
mkp add ~/morpheus-1.0.4.mkp
mkp enable morpheus 1.0.4
cmk-validate-plugins
```

4. Otwórz istniejącą regułę **HPE Morpheus**. Zachowaj URL, token i ustawienie TLS. **Disable infrastructure collection** pozostaw wyłączone. **Discover individual hardware sensors** na początek pozostaw wyłączone.
5. Zapisz regułę, otwórz Service discovery hosta źródłowego API i wykonaj **Rescan / Full scan**.
6. Zaakceptuj nowe usługi i wykonaj **Activate changes**.
7. Najpierw sprawdź `Morpheus Infrastructure collection`, a potem usługi datastore.

Jeśli nowe pola lub reguły nie są widoczne po aktualizacji, odśwież procesy GUI jako użytkownik site:

```bash
omd restart apache
omd restart redis
```

## Konfiguracja u nowego klienta

1. Zainstaluj MKP i zweryfikuj wtyczki.
2. Utwórz konto odczytowe Morpheusa oraz token z dostępem do wymaganych chmur i endpointów.
3. Zapisz token w **Password store** Checkmk.
4. Utwórz host logiczny API, np. `morpheus-api`, z **Configured API integrations, no Checkmk agent**, bez SNMP. Skonfiguruj adres/host check zgodnie z dostępnością managera.
5. Dodaj regułę **HPE Morpheus** ograniczoną do tego hosta. Samodzielnie podaj URL danej instalacji i wpis tokenu z Password store.
6. TLS verification jest domyślnie włączone. Zaufaj CA docelowej instalacji albo świadomie użyj opcji wyłączenia weryfikacji.
7. Opcjonalne **Restrict infrastructure and VMs to cloud ID** ogranicza kolekcję do chmury wskazanej na docelowym appliance. Żaden ID klienta nie jest wpisany w pakiet.
8. Wykonaj discovery i aktywuj zmiany.

DCD jest konfigurowany osobno, tylko dla hostów VM. Dla hostów wyłącznie piggyback ustaw **No API integrations, no Checkmk agent**, **No SNMP**, **No IP** oraz **Always use and expect piggyback data**. Host źródłowy API zachowuje integrację API. Wybierz konektor Piggyback data, właściwy host źródłowy, folder docelowy i filtr `^morpheus-vm-[0-9]+$`, jeśli używasz domyślnego nazewnictwa. Na początek wyłącz automatyczne usuwanie hostów. Nowe datastore, hypervisory, klastry i sensory w tej wersji są usługami hosta API, a nie dodatkowymi hostami piggyback.

## Interpretacja datastore

- HVM: kolektor odczytuje datastore **klastra** (`/api/clusters/{id}/datastores`), nawet jeśli `/api/zones/{id}/data-stores` jest pusty.
- Pozostałe datastore są zbierane przez chmury. Wspólny datastore nie jest dublowany, jeśli występuje w kilku odpowiedziach.
- Źródłem pojemności jest `storageSize`. Gdy jej brakuje, używane jest `maxStorage` z wolumenu hypervisora po jednoznacznym dopasowaniu ID datastore i chmury. Sprzeczne pojemności nie są uśredniane ani zgadywane.
- Procent zajętości: `(storageSize - freeSpace) / storageSize * 100`.
- Domyślne progi zajętości datastore to **WARN 80%, CRIT 90%**. Zmienisz je w regule **Morpheus datastore capacity levels**.
- Brak pojemności, brak freeSpace, ujemne wartości albo freeSpace większe niż pojemność dają UNKNOWN. Zerowa pojemność nie oznacza 100% zajętości.
- Odrębne datastore katalogowe mogą znajdować się na tym samym filesystemie i raportować tę samą pojemność. Pakiet nie sumuje ich pojemności.
- Wiek danych jest oceniany na podstawie synchronizacji klastra/chmury; jest to wiek źródła inwentarza, nie gwarantowany moment wykonania pomiaru filesystemu.
- Datastore offline daje CRIT w State, a wykorzystanie nie jest interpretowane jako poprawne.

## Multipath, sprzęt i klaster

- Multipath: domyślnie wymagane 2 aktywne ścieżki. Degradacja/dodatnia liczba uszkodzonych daje WARN; 0 aktywnych lub błędny stan multipath daje CRIT. Minimum i wiek danych ustawisz w **Morpheus datastore multipath**.
- Sensory `ns` (not available) są liczone w podsumowaniu, ale nie oznaczają automatycznie usterki. Domyślnie brak osobnych usług dla tych sensorów.
- Hardware summary interpretuje statusy raportowane przez Morpheusa. Nie odgaduje obecności wentylatora na podstawie samego odczytu 0 RPM. Szczegółowe sensory mogą prezentować temperaturę, RPM, W, V i procenty. Progi sprzętowe wynikają ze statusu upstream; ta wersja nie ma osobnych numerycznych progów temperatury/fan.
- CPU hypervisora to `stats.cpuUsage` w procentach. Dla klastra używane jest `workerStats.cpuUsageAvg`, a nie suma procentów hostów.
- Pamięć klastra pochodzi z `workerStats` i nie musi odpowiadać sumie fizycznego zużycia pamięci hypervisorów. Rezerwacja jest osobną metryką.
- Stan HA jest informacyjny. Jeśli HA jest wymagane, zaznacz **Require cluster HA to be enabled** w **Morpheus cluster state and HA**. Wyłączone HA nie daje domyślnie alarmu.
- Maintenance Morpheusa jest prezentowany; nie ustawia automatycznie downtime w Checkmk.

## Aktualność i awarie API

Standardowe progi wieku danych to 900/1800 s; hardware ma odrębne progi 120/900 s. Dostosuj je do okresu synchronizacji providera. Po przekroczeniu krytycznego wieku lub przy braku czasu źródła checki metryk nie publikują zużycia jako bieżących danych.

Błąd nowego endpointu infrastruktury daje CRIT w `Morpheus Infrastructure collection`, ale nie zatrzymuje wcześniejszego monitoringu platformy i VM. Niepełna odpowiedź pojedynczego stronicowanego endpointu nie jest przyjmowana jako kompletna lista. Przy problemach z uprawnieniami rozszerz prawa odczytu lub tymczasowo wyłącz nowy zakres przez **Disable infrastructure collection**.

## Zabezpieczenia i przenośność

Kolektor wykonuje wyłącznie GET i blokuje przekierowania. Do Checkmk trafiają tylko wybrane pola. Nie kopiuje pełnych konfiguracji obiektów, kluczy ani haseł. Token jest przechowywany w konfiguracji danego site/Password store, nie w MKP.

W Checkmk 2.4 token jest przekazywany do agenta standardowym mechanizmem `Secret.unsafe()`. Moduł `setproctitle`, jeśli jest dostępny, usuwa argumenty z nazwy procesu po starcie; nadal istnieje krótkie okno ich widoczności. Przejrzyj wyniki diagnostyki przed ich publikowaniem. Ta wersja nie implementuje automatycznego odświeżania tokenu.

Fixtures w archiwum są ograniczone do dozwolonych pól i mają neutralne nazwy obiektów. Oryginalne załączniki użytkownika nie są dołączone. Pakiet nie instaluje ani nie zmienia konfiguracji DCD.

## Testy i ograniczenia

Kod źródłowy, builder i testy znajdują się w głównym katalogu przygotowanego repozytorium (`repository/` w ZIP-ie). Uruchomienie:

```bash
python3 -m unittest discover -s tests -v
python3 build.py
```

67 testów obejmuje paginację, przerwane odpowiedzi, kolizje, filtr poufnych pól, pojemność i progi datastore, multipath, problemy hardware, stan HA i członków, sensor temperatury, wiek danych oraz brakujące wartości. Testy funkcjonalne checków używają zastępczych obiektów API. Dodatkowy `tests/validate_public_api.py` uruchomiono z publicznymi klasami API Checkmk 2.4.0 dla usług, formularzy, metryk i wykresów; nie jest to pełne `cmk-validate-plugins` ani test API klienta. Wyniki w `TEST_RESULTS.txt`.

Nie zaimplementowano jeszcze: backupów, zdarzeń, sieci wirtualnych, pełnej inspekcji HA/quorum poza dostępnymi polami klastra, poszczególnych filesystemów gościa ani agenta BMC/Redfish. Te zakresy wymagają oddzielnych źródeł danych lub dalszego rozszerzenia.

Dokumentacja:
- https://docs.checkmk.com/2.4.0/en/devel_special_agents.html
- https://docs.checkmk.com/2.4.0/en/mkps.html
- https://apidocs.morpheusdata.com/reference/listclusterdatastores
- https://apidocs.morpheusdata.com/reference/listclouddatastores

Licencja tego wydania: GPL-2.0-only. Pełny tekst w LICENSE; kod instalowany przez MKP zawiera COPYING. Wcześniejsze wydania były udostępniane na MIT; niniejsza zmiana dotyczy nowego wydania.

Wersja 0.2.2 przeszła 38 testów lokalnych, w tym fallback szczegółów hosta, zachowanie czasu cache, alarmy wieku, prywatne uprawnienia pliku, odrzucanie uszkodzonego cache oraz zachowanie błędów sprzętu. Wymaga jeszcze walidacji i potwierdzenia działania na docelowym site.
