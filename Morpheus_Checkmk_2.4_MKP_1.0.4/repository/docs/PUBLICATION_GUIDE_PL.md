# Publikacja na GitHub i Checkmk Exchange — 1.0.4

Git to program do kontroli wersji. GitHub to serwis, na którym zakładasz konto i udostępniasz repozytorium. Do opisanej poniżej metody przeglądarkowej nie potrzebujesz instalować Gita, tworzyć klucza SSH ani generować tokenu GitHub.

## 1. Załóż konto GitHub

1. Otwórz https://github.com/signup.
2. Wybierz rejestrację adresem e-mail albo obsługiwaną metodą logowania Google/Apple.
3. Podaj adres, do którego masz dostęp, ustaw hasło i wybierz nazwę użytkownika, np. `pawel-wladzinski`, jeżeli jest wolna. Nazwa użytkownika będzie częścią adresu repozytorium.
4. Wykonaj kroki weryfikacyjne i potwierdź e-mail wiadomością od GitHub.
5. Do publicznego projektu wystarczy bezpłatne konto GitHub Free.
6. W profilu ustaw wyświetlaną nazwę `Pawel Wladzinski`. E-mail autora w przygotowanych plikach to `pawel.wladzinski@vayana.pl`; pozostanie publiczny w kodzie i metadanych.
7. W **Settings → Password and authentication** skonfiguruj uwierzytelnianie dwuskładnikowe i zachowaj kody odzyskiwania u siebie.

Instrukcja producenta: https://docs.github.com/en/account-and-profile/how-tos/account-management/creating-an-account-on-github

## 2. Utwórz repozytorium

1. Zaloguj się i otwórz https://github.com/new.
2. Jako Owner wybierz swoje konto.
3. **Repository name:** `checkmk-morpheus`.
4. **Description:** `Read-only HPE Morpheus platform, infrastructure and VM monitoring for Checkmk 2.4.`
5. Ustaw **Public**, jeżeli chcesz już upublicznić kod. Możesz najpierw utworzyć Private i zmienić widoczność po sprawdzeniu plików.
6. Włącz **Add a README file**, żeby od razu mieć gałąź `main` i wygodny przycisk dodawania plików.
7. Nie wybieraj dodatkowego szablonu licencji ani `.gitignore` — oba pliki są w przygotowanym folderze.
8. Kliknij **Create repository**.

Przykładowy format adresu, nie gotowy link Twojego projektu:

```text
https://github.com/TWOJA_NAZWA/checkmk-morpheus
```

Instrukcja: https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-new-repository

## 3. Wgraj przygotowany kod

1. Rozpakuj otrzymane archiwum publikacyjne na swoim komputerze.
2. Otwórz znajdujący się w nim folder **repository**. To jego zawartość ma trafić do głównego katalogu GitHub; nie wgrywaj całego zewnętrznego ZIP-a ani dodatkowego katalogu o nazwie `repository`.
3. W GitHub wybierz **Add file → Upload files**.
4. Przeciągnij zawartość folderu `repository`, zachowując katalogi `src`, `tests` i `docs`. Gotowy `README.md` zastąpi początkowy pusty README.
5. Uwzględnij `.gitignore` i `.gitattributes`. Na macOS pokaż ukryte pliki skrótem **Command + Shift + .**, jeśli Finder ich nie pokazuje. Jeżeli uploader pominie te pliki, dodaj je osobno przez **Add file → Create new file**, wpisując dokładną nazwę i kopiując zawartość lokalnego pliku.
6. Nie dodawaj folderu `package`, własnych eksportów API, konfiguracji instancji, tokenów ani zrzutów zawierających dane klienta. Folder `package` służy do załączników wydania, nie jest częścią przygotowanego drzewa źródłowego.
7. Wpisz komunikat commita: `Prepare HPE Morpheus Monitoring 1.0.4` i zatwierdź zmiany w `main`.
8. Sprawdź, że na głównej stronie renderuje się angielski README, a katalogi są na poziomie głównym repozytorium.

Instrukcja: https://docs.github.com/en/repositories/working-with-files/managing-files/adding-a-file-to-a-repository

## 4. Utwórz wydanie GitHub

1. W repozytorium otwórz **Releases → Draft a new release**; przy pierwszym wydaniu interfejs może pokazać **Create a new release**.
2. Utwórz tag **v1.0.4** dla gałęzi `main`.
3. **Release title:** `HPE Morpheus Monitoring 1.0.4`.
4. Wklej opis z `repository/docs/RELEASE_NOTES_1.0.4_EN.md`.
5. Dodaj dwa załączniki z folderu `package`: `morpheus-1.0.4.mkp` i `SHA256SUMS.txt`.
6. Sprawdź opis i załączniki. **Save draft** zapisuje szkic; **Publish release** udostępnia wydanie użytkownikom zgodnie z widocznością repozytorium.

Instrukcja: https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository

Nie deklaruj pełnego wsparcia 2.5 lub innych wersji Morpheusa bez testów. Nazwa pakietu nie zawiera „beta”, ale opis wprost podaje zakres sprawdzenia i ograniczenia.

## 5. Dodaj repozytorium do metadanych MKP — opcjonalnie

Obecny MKP ma puste pole projektu Download-URL. Nie ma tam fikcyjnego adresu. Opis Exchange można już uzupełnić rzeczywistym linkiem do repozytorium.

Jeśli chcesz także ten link w `mkp inspect`, po utworzeniu repozytorium uruchom z głównego katalogu kodu, podstawiając swój prawdziwy adres:

```bash
python3 build.py --download-url https://github.com/TWOJA_NAZWA/checkmk-morpheus
```

Wynik jest w `dist/morpheus-1.0.4.mkp`. Tę wersję dołącz do szkicu wydania, a następnie zaktualizuj sumę kontrolną:

```bash
cd dist
sha256sum morpheus-1.0.4.mkp > SHA256SUMS.txt
```

Na macOS zamiast `sha256sum` można użyć `shasum -a 256`. Zmiana metadanych zmienia bajty MKP, dlatego trzeba ponownie wyliczyć checksumę. Zrób to przed pierwszą publikacją tagu; po opublikowaniu i zmianie zawartości użyj nowej wersji.

Jeżeli nie chcesz nic budować lokalnie, użyj dostarczonego MKP z pustym Download-URL i dodaj prawdziwy link na stronie Exchange. Przebudowanie pakietu nie jest wymagane do założenia repozytorium.

## 6. Sprawdź paczkę na testowej instancji Checkmk

Wgraj `package/morpheus-1.0.4.mkp` i jako użytkownik właściwej instancji wykonaj:

```bash
mkp inspect ~/morpheus-1.0.4.mkp
mkp add ~/morpheus-1.0.4.mkp
mkp enable morpheus 1.0.4
cmk-validate-plugins
```

Sprawdź pobieranie danych, discovery, stany VM, wykresy i zapisane reguły. Wersja 1.0.4 nie zmienia działania 1.0.3, ale ten konkretny plik MKP wymaga testu po instalacji. Błędy walidacji innych rozszerzeń należy odróżnić od błędów `morpheus`.

Przy aktualizacji z wersji sprzed 1.0.3 pamiętaj o nowych nazwach usług infrastruktury i chmur. Wymagane jest discovery oraz sprawdzenie reguł dopasowujących stare nazwy.

## 7. Zgłoś pakiet do Checkmk Exchange

1. Otwórz https://exchange.checkmk.com/ i załóż oddzielne konto przez **Register**.
2. Potwierdź e-mail i zaloguj się. Konto GitHub nie zastępuje konta Exchange.
3. Wybierz **Upload new package**.
4. Wgraj **`package/morpheus-1.0.4.mkp`**, a nie ZIP-a publikacyjnego.
5. Wklej opis z `repository/docs/EXCHANGE_DESCRIPTION_EN.md` i dodaj rzeczywisty adres repozytorium.
6. Wybierz pasującą ikonę z dostępnych, np. kategorię chmury/infrastruktury. Nie dołączono ani nie użyto oficjalnych logotypów HPE/Checkmk.
7. Przejrzyj regulamin i zatwierdź zgłoszenie. Publikacja następuje po moderacji przez Checkmk; przygotowanie pakietu nie oznacza akceptacji.
8. Następne wersje dodawaj na stronie tego samego rozszerzenia przez **Add Version**.

Instrukcje:
- https://exchange.checkmk.com/how-to-upload
- https://docs.checkmk.com/latest/en/devel_mkps.html

## Co jest przygotowane, a co wymaga Twojego działania

Przygotowane: kod i testy, angielski README, changelog, GPL-2.0-only, COPYRIGHT, kontakt autora, instrukcje zgłoszeń, opis Exchange, opis wydania, gotowy MKP i jego SHA-256.

Twoje działania: utworzenie kont i repozytorium, potwierdzenie adresu, test dokładnego MKP na swoim site, publikacja kodu/wydania i zgłoszenie do moderacji. Nie są do tego potrzebne hasła ani tokeny przekazywane do rozmowy. Nie dołączono screenshotów z prywatnego środowiska; możesz później dodać własne zanonimizowane ilustracje.

