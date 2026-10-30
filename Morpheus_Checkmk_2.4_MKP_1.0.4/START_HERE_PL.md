# HPE Morpheus Monitoring 1.0.4 — pakiet publikacyjny

Autor i opiekun: Pawel Wladzinski <pawel.wladzinski@vayana.pl>.

- `repository/`: zawartość gotowa do wgrania do głównego katalogu GitHub; kod, README, GPL-2.0-only, changelog i testy.
- `package/morpheus-1.0.4.mkp`: plik instalacyjny dla Checkmk i zgłoszenia do Exchange.
- `package/SHA256SUMS.txt`: suma kontrolna MKP.
- [Instrukcja konta GitHub i publikacji krok po kroku](repository/docs/PUBLICATION_GUIDE_PL.md).
- [Opis do Checkmk Exchange](repository/docs/EXCHANGE_DESCRIPTION_EN.md).
- [Opis wydania GitHub](repository/docs/RELEASE_NOTES_1.0.4_EN.md).

Nie utworzono konta/repozytorium i niczego nie opublikowano. Po utworzeniu repozytorium dodaj jego prawdziwy adres do opisu Exchange. Download-URL w MKP pozostaje pusty; instrukcja opisuje opcjonalne przebudowanie z Twoim adresem.

Wydanie 1.0.4 nie zmienia logiki monitorowania względem 1.0.3. Zmienia materiały publikacyjne, metadane i licencję nowego wydania. Lokalnie przeszło 67 testów oraz walidacja publicznych API Checkmk 2.4. Przed zgłoszeniem sprawdź ten MKP na własnej instancji testowej. Nie dołączono screenshotów prywatnego środowiska.
